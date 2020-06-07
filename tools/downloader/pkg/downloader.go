package pkg

import (
	"bytes"
	"encoding/csv"
	"fmt"
	"io"
	"io/ioutil"
	"net/http"
	"os"
	"os/exec"
	"strings"
	"sync"
	"time"

	"github.com/panjf2000/ants/v2"
	"github.com/pkg/errors"
	"go.bobheadxi.dev/zapx/zapx"
	"go.uber.org/zap"
)

const (
	/* rows of csv file for easy reference
	0    , 1     , 2  , 3  , 4  , 5       , 6, 7    , 8    , 9    , 10  , 11    , 12   , 13   ,  14
	state,edit_at,city,name,date,date_text,id,Link 1,Link 2,Link 3,Link 4,Link 5,Link 6,Link 7,Link 8
	*/
	url = "https://raw.githubusercontent.com/2020PB/police-brutality/data_build/all-locations.csv"
)

// Downloader downloads the media contained in the csv file
type Downloader struct {
	path   string
	logger *zap.Logger
	// enables running concurrent downloads
	wp *ants.Pool
}

// New returns a new downloader
func New(logFile, path string, concurrency int) *Downloader {
	if _, err := os.Stat(path); os.IsNotExist(err) {
		if err := os.Mkdir(path, os.FileMode(0775)); err != nil {
			panic(err)
		}
	}
	logger, err := zapx.New(logFile, false)
	if err != nil {
		panic(err)
	}
	wp, err := ants.NewPool(concurrency)
	if err != nil {
		panic(err)
	}
	return &Downloader{path, logger, wp}
}

// Run starts the download process, note that maxDownloads doesn't necessarily equate to number of videos
// it really means the maximum number of entries in the csv to download, and some entries in the csv may have more than 1 associated video
func (d *Downloader) Run(takeScreenshots bool, timeout time.Duration, maxDownloads int) error {
	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	var (
		results []struct {
			name  string
			link  string
			pbid  string
			count int64
		}
		mux    = &sync.Mutex{}
		wg     = &sync.WaitGroup{}
		reader = csv.NewReader(resp.Body)
	)
	for i := 0; ; i++ {
		// the first read from the CSV file will be the header
		// so we need to make sure that we factor that in when
		// counting max downloads
		if maxDownloads != 0 && i >= maxDownloads+1 {
			break
		}
		// read the next record
		record, err := reader.Read()
		if err != nil && err != io.EOF {
			return err
		} else if err == io.EOF {
			d.logger.Info("finished downloading videos")
			break
		}
		// skip the first row as it contains column names OR
		// skip if the row has less than 8 elements as the 8th element is the start of the video links
		if i == 0 || len(record) < 8 {
			continue
		}
		wg.Add(1)
		d.wp.Submit(func() {
			defer wg.Done()
			pbid := record[6]
			// gets the last column so we dont get an out of range panic
			max := len(record) - 1
			var count int64 = 0
			for ii := 7; ii < max; ii++ {
				count++
				// this column is empty, and has no data
				if record[ii] == "" {
					continue
				}
				// if the file already exists, dont redownload
				_, err := os.Stat(d.getName(pbid, count))
				if os.IsExist(err) {
					continue
				}
				d.logger.Info("downloading video", zap.String("name", record[3]), zap.String("url", record[ii]))
				download := func() error {
					cmd := exec.Command("youtube-dl", "-o", d.getName(pbid, count), record[ii])
					return d.runCommand(cmd, timeout)
				}
				if err := download(); err != nil {
					d.logger.Error("failed to run command", zap.Error(err), zap.String("name", record[3]), zap.String("url", record[ii]))
				} else {
					// if the command run succeeded, then update the results for processing after all downloads are done
					mux.Lock()
					results = append(results, struct {
						name  string
						link  string
						pbid  string
						count int64
					}{
						name:  record[3],
						link:  record[ii],
						pbid:  pbid,
						count: count,
					})
					mux.Unlock()
				}
				// download the screenshot if specified
				// TODO(bonedaddy): enable adding this to the csv, for now it exists alongside everything else
				if takeScreenshots {
					if err := capture(d.getName(pbid, count), record[ii]); err != nil {
						d.logger.Error("failed to capture screenshot", zap.Error(err), zap.String("url", record[ii]))
					}
				}
			}
		})
	}
	// wait for pending download operations to finish
	wg.Wait()
	// read download dir to check for any file artifacts
	infos, err := ioutil.ReadDir(d.path)
	if err != nil {
		return err
	}
	for _, info := range infos {
		// this was an incorrectly downloaded piece of data, remove
		if strings.HasSuffix(info.Name(), ".part") {
			if err := os.Remove(d.path + "/" + info.Name()); err != nil {
				d.logger.Error("failed to remove file part", zap.String("file", info.Name()), zap.Error(err))
			}
		}
	}
	// backup the previous csv if it exists for posterity
	if data, err := ioutil.ReadFile(d.path + "/name_mapping.csv"); err != nil {
		d.logger.Error("failed to read previous name mapping file, likely doesn't exist", zap.Error(err))
	} else {
		if len(data) > 0 {
			ioutil.WriteFile(fmt.Sprintf("%s/name_mapping-%v.csv", d.path, time.Now().UnixNano()), data, os.FileMode(0640))
		}
	}
	var (
		fh      *os.File
		records [][]string
	)
	// addd the headers to write to the csv
	records = append(records, []string{"name", "link", "pbid", "link_number"})
	if _, err := os.Stat(d.path + "/name_mapping.csv"); err == nil {
		fh, err = os.Open(d.path + "/name_mapping.csv")
		if err != nil {
			// fallback to default
			d.logger.Error("failed to open existing csv", zap.Error(err))
		}
		// file exists, remove the headers as they will be read
		records = [][]string{}
		for {
			record, err := csv.NewReader(fh).Read()
			if err != nil && err == io.EOF {
				break
			}
			records = append(records, record)
		}
	} else {
		// open csv file to store mappings
		fh, err = os.Create(d.path + "/name_mapping.csv")
		if err != nil {
			return err
		}
	}
	writer := csv.NewWriter(fh)
	// write the previous csv file to disk
	// if no previous mapping exists, this will just write the headers
	for _, record := range records {
		writer.Write(record)
	}
	mux.Lock()
	// iterate over all results and add to csv
	for _, v := range results {
		writer.Write([]string{v.name, v.link, v.pbid, fmt.Sprint(v.count)})
	}
	mux.Unlock()
	// flush csv, writing to disk
	writer.Flush()
	return fh.Close()
}

func (d *Downloader) runCommand(cmd *exec.Cmd, timeout time.Duration) error {
	var errbuf bytes.Buffer
	cmd.Stderr = &errbuf
	if err := cmd.Start(); err != nil {
		return errors.Wrap(err, "failed to start command")
	}
	done := make(chan error)
	go func() { done <- cmd.Wait() }()
	select {
	case err := <-done:
		if err != nil {
			return errors.Wrapf(err, "command execution encountered failure: %s", errbuf.String())
		}
	case <-time.After(timeout):
		// this is meant to prevent any possible issue with cmd having a nil process when this is called
		defer recover()
		// kill the process
		if cmd.Process != nil {
			cmd.Process.Kill()
		}
		return errors.New("download stalled, skipping")
	}
	return nil
}

// uses an atomically increasing counter to prevent any possible chance of filename conflics when running many concurrent downloaders
func (d *Downloader) getName(id string, count int64) string {
	// fallback to youtube id
	if id == "" {
		id = "%(id)s"
	}
	return d.path + "/" + id + "." + fmt.Sprint(count) + ".%(ext)s"
}
