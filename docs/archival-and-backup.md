# Archival & Backup

The `police-brutality` repo contains two tools to enable easy archival, and backup/replication of existing archived data. Archival is done via a CLI tool that allows downloading the videos listed in the [`all-locations.csv` file](https://github.com/2020PB/police-brutality/blob/data_build/all-locations.csv), and optionally adding them to an IPFS node. Backup/replication is done via a public IPFS Cluster that anyone can join to mirror data. Additionally tooling is provided that enables anyone to spin up their own IPFS clusters.

# Tools

* [Archival/downloader tool](https://github.com/2020PB/police-brutality/tree/master/tools/downloader)
* [Backup/replication tool](https://github.com/2020PB/police-brutality/blob/23c2edc33d23a65610e0f885ca1e04a70806dc7a/tools/replicator/README.md)
  * TODO(bonedaddy): update link when the tooling is merged to master
