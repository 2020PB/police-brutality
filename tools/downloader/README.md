# downloader

`downloader` is a CLI tool that allows parsing over the all-locations csv file, and downloading all the videos referenced in the CSV file, and can  concurrently download multiples videos. Because some of the videos have file names that are longer than the maximum permitted characters in a file path, the videos are not saved under their name, but instead using the videoID as determined by youtube-dl, along with a unique number. This information is then stored in a final CSV file which contains the video name, the link used to download video, as well as the unique number so you can easily determine what video belongs to what incident. Additionally it allows uploading the video data to an IPFS HTTP API endpoint

The template for names of videos saved on disk is `[YOUTUBE-DL-VIDEO-ID].[UNIQUE-VIDEO-NUMBER].[EXTENSION]`, and the CSV file has the rows `name,link,unique_video_number`. So for example we have the following entry in the CSV file `Law enforcement gas a crowd chanting “we want peace” right after exiting the building.,https://twitter.com/courtenay_roche/status/1267653137969623040,1`, and two files we have downloaded: 

* `1267647898365427714.2.mp4`
* `1267653137969623040.1.mp4`

Given the row in the CSV file, the corresponding video would be `1267653137969623040.1.mp4`.


# install

* Ensure you have go installed at version 1.14+
* Ensure you have youtube-dl installed
* Build the binary using `go build` OR `make build`

# usage

## cli

To download all videos one by one:

```shell
$> downloader start
```

To concurrently download all videos, 10 at a time:

``` shell
$> downloader start -c 10
```

To download all videos, 10 at a time, for the first 10 incidents:

```shell
$> downloader start -c 10 -md 10
```

To download all videos, 10 at a time, and upload to an IPFS HTTP API endpoint:
```shell
$> downloader start -c 10 -upload.to_ipfs
```

To specify an alternate IPFS HTTP API endpoint other than the default:
```shell
$> downloader start -c 10 -uti -ie localhost:5001
```

Alternatively if the IPFS HTTP API endpoint requires JWT authentication:
```shell
$> downloader start -c 10 -uti -ie localhost:5001 --iat <your-jwt-here>
```

To view the help:
```shell
$> downloader start -h
NAME:
   downloader start - starts the downloader

USAGE:
   downloader start [command options] [arguments...]

OPTIONS:
   --directory value, --dir value, -d value    location to save videos to (default: "videos")
   --log.file value, --lf value, -l value      where to store log data (default: "downloader.log")
   --ipfs.endpoint value, --ie value           endpoint to upload videos to if ipfs uploading is enabled (default: "localhost:5001")
   --ipfs.auth_token value, --iat value        jwt to use with authentication to an ipfs http api endpoint [$IPFS_AUTH_TOKEN]
   --concurrency value, --con value, -c value  enables concurrent download of videos (default: 1)
   --max.downloads value, --md value           maximum number of of incidents to download, 0 indicates all of them (default: 0)
   --timeout value, -t value                   timeout to quit a download, you may need to adjust depending on your connection (default: 3m0s)
   --upload.to_ipfs, --uti                     enables uploading the video data to any ipfs endpoint (default: false)
   --help, -h                                  show help (default: false)
   
```

## package

Alternatively you can use this library as a package, to do so use `import github.com/2020PB/police-brutality/pkg`. See the `main.go` file for examples on how to use this as a library