package main

import (
	"os"
	"time"

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
				return dl.Run(c.Duration("timeout"), c.Int("max.downloads"))
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
			},
		},
	}
	if err := app.Run(os.Args); err != nil {
		panic(err)
	}
}
