package pkg

import (
	"io/ioutil"
	"os"
	"strings"
	"testing"
	"time"
)

func TestDownloader(t *testing.T) {
	var (
		logFile = "test.log"
		path    = "testdir"
	)
	t.Cleanup(func() {
		os.RemoveAll("testdir")
		os.Remove("test.log")
	})
	dl := New(logFile, path, 1)
	if _, err := os.Create(path + "/thisisatestfilethatweareusingtotestremovaloffileswith.part"); err != nil {
		t.Fatal(err)
	}
	if err := dl.Run(time.Minute, 2); err != nil {
		t.Fatal(err)
	}
	infos, err := ioutil.ReadDir(path)
	if err != nil {
		t.Fatal(err)
	}
	for _, info := range infos {
		if strings.HasSuffix(info.Name(), ".part") {
			t.Fatal("shouldn't have found .part file")
		}
	}
}
