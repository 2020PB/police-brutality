package main

import (
	"log"
	"os"
	"time"

	. "github.com/2020PB/police-brutality/pkg"
	"github.com/urfave/cli/v2"
)

func main() {
	app := cli.NewApp()
	app.Name = "downloader"
	app.Usage = "downloads videos listed in the csv file"
	app.Commands = cli.Commands{
		&cli.Command{
			Name:  "start",
			Usage: "starts the downloader",
			Action: func(c *cli.Context) error {
				dl := New(c.String("log.file"), c.String("directory"), c.Int("concurrency"))
				if err := dl.Run(c.Duration("timeout"), c.Int("max.downloads")); err != nil {
					return err
				}
				if c.Bool("upload.to_ipfs") {
					uploader, err := NewIPFSUploader(c.String("ipfs.endpoint"), c.String("ipfs.auth_token"))
					if err != nil {
						return err
					}
					hash, err := uploader.Upload(c.String("directory"))
					if err != nil {
						return err
					}
					log.Println("ipfs hash of directory: ", hash)
				}
				return nil
			},
			Flags: []cli.Flag{
				&cli.StringFlag{
					Name:    "directory",
					Aliases: []string{"dir", "d"},
					Usage:   "location to save videos to",
					Value:   "videos",
				},
				&cli.StringFlag{
					Name:    "log.file",
					Aliases: []string{"lf", "l"},
					Value:   "downloader.log",
					Usage:   "where to store log data",
				},
				&cli.StringFlag{
					Name:    "ipfs.endpoint",
					Aliases: []string{"ie"},
					Usage:   "endpoint to upload videos to if ipfs uploading is enabled",
					Value:   "localhost:5001",
				},
				&cli.StringFlag{
					Name:    "ipfs.auth_token",
					Aliases: []string{"iat"},
					Usage:   "jwt to use with authentication to an ipfs http api endpoint",
					EnvVars: []string{"IPFS_AUTH_TOKEN"},
				},
				&cli.IntFlag{
					Name:    "concurrency",
					Aliases: []string{"con", "c"},
					Value:   1,
					Usage:   "enables concurrent download of videos",
				},
				&cli.IntFlag{
					Name:    "max.downloads",
					Aliases: []string{"md"},
					Usage:   "maximum number of of incidents to download, 0 indicates all of them",
					Value:   0,
				},
				&cli.DurationFlag{
					Name:    "timeout",
					Aliases: []string{"t"},
					Value:   time.Minute * 3,
					Usage:   "timeout to quit a download, you may need to adjust depending on your connection",
				},
				&cli.BoolFlag{
					Name:    "upload.to_ipfs",
					Aliases: []string{"uti"},
					Usage:   "enables uploading the video data to any ipfs endpoint",
					Value:   false,
				},
			},
		},
	}
	if err := app.Run(os.Args); err != nil {
		panic(err)
	}
}
