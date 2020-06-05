package pkg

import (
	"bytes"
	"encoding/csv"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"sync"
	"time"

	"github.com/panjf2000/ants/v2"
	"github.com/pkg/errors"
	"go.bobheadxi.dev/zapx/zapx"
	"go.uber.org/atomic"
	"go.uber.org/zap"
)

const (
	/* rows of csv file for easy reference
	0    , 1     , 2  , 3  , 4  , 5       , 6    , 7    ,  8   , 9    , 10   , 11  ,  12   , 13
	state,edit_at,city,name,date,date_text,Link 1,Link 2,Link 3,Link 4,Link 5,Link 6,Link 7,Link 8
	*/
	url = "https://raw.githubusercontent.com/2020PB/police-brutality/data_build/all-locations.csv"
)

// Downloader downloads the media contained in the csv file
type Downloader struct {
	path   string
	logger *zap.Logger
	// enables running concurrent downloads
	wp    *ants.Pool
	count *atomic.Int64
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
	return &Downloader{path, logger, wp, atomic.NewInt64(0)}
}

// Run starts the download process, note that maxDownloads doesn't necessarily equate to number of videos
// it really means the maximum number of entries in the csv to download, and some entries in the csv may have more than 1 associated video
func (d *Downloader) Run(timeout time.Duration, maxDownloads int) error {
	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	var (
		results []struct {
			name  string
			link  string
			count int64
		}
		mux    = &sync.Mutex{}
		wg     = &sync.WaitGroup{}
		reader = csv.NewReader(resp.Body)
	)
	for i := 0; maxDownloads != 0 && i < maxDownloads; i++ {
		// read the next record
		record, err := reader.Read()
		if err != nil && err != io.EOF {
			return err
		} else if err == io.EOF {
			d.logger.Info("finished downloading videos")
			break
		}
		// skip the first row as it contains column names OR
		// skip if the row has less than 7 elements as the 7th element is the start of the video links
		if i == 0 || len(record) < 7 {
			continue
		}
		wg.Add(1)
		d.wp.Submit(func() {
			defer wg.Done()
			// gets the last column so we dont get an out of range panic
			max := len(record) - 1
			for ii := 6; ii < max; ii++ {
				// this column is empty, and has no data
				if record[ii] == "" {
					continue
				}
				count := d.count.Inc()
				d.logger.Info("downloading video", zap.String("name", record[3]), zap.String("url", record[ii]))
				download := func() error {
					cmd := exec.Command("youtube-dl", "-o", d.getName(count), record[ii])
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
						count int64
					}{
						name:  record[3],
						link:  record[ii],
						count: count,
					})
					mux.Unlock()
				}
			}
		})
	}
	// wait for pending download operations to finish
	wg.Wait()
	// open csv file to store mappings
	fh, err := os.Create("name_mapping.csv")
	if err != nil {
		return err
	}
	writer := csv.NewWriter(fh)
	// write the csv file headers
	writer.Write([]string{"name", "link", "unique_video_number"})
	mux.Lock()
	// iterate over all results and add to csv
	for _, v := range results {
		writer.Write([]string{v.name, v.link, fmt.Sprint(v.count)})
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
func (d *Downloader) getName(count int64) string {
	return d.path + "/%(id)s." + fmt.Sprint(count) + ".%(ext)s"
}
