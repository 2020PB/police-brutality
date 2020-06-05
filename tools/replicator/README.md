# replicator

> **WARNING**: If you value your privacy, and anonymity do not participate in this cluster. Participating in this cluster, **even** if coming behind an anonymization tool like Tor, or a VPN will likely lead to your real life identity being revealed, as IPFS is incredibly self-doxxing. If you want to participate in this cluster, and value your privacy and anonymity, do so from a cloud based VPS, ideally paid for via anonymous crypto.

The `replicator` tool allows anyone to easily mirror a public set of data on IPFS. It consists of spinning up lightweight an IPFS node, along with a lightweight IPFS Cluster client that follows a CRDT topic publish to by a set of trusted peers that are responsible for updating the "follow list" which is a set of IPFS CIDs that are replicated by the cluster. Anyone following this cluster will pin the data in the follow list locally.

# install

If you run a 64-bit version of linux you can use the `install_cluster_linux.sh` bash script to install the needed components. If you don't run a 64-bit version of Linux, you should update the script to work on your platform and then use the script, otherwise please see the following URLS:

* [ipfs-cluster-ctl](https://dist.ipfs.io/#ipfs-cluster-ctl)
* [ipfs-cluster-follow](https://dist.ipfs.io/#ipfs-cluster-follow)
* [ipfs-cluster-service](https://dist.ipfs.io/#ipfs-cluster-service)


To install the cluster tooling on 64-bit linux with the aforementioned script invoke as follows:

```shell
$> install_cluster_linux.sh linux-64bit
```

# usage

This folder contains the needed files and configurations for anyone to start a follow peer, or run their own follow cluster acting as a trusted peer. The trusted peer setup is a little more difficult, and requires running both go-ipfs and ipfs-cluster. Before running any of these steps make sure you have the following software installed on your local machine:

* go-ipfs
* ipfs-cluster-follow (only if running a follow peer)
* ipfs-cluster-service (only if running a trusted peer)
* ipfs-cluster-ctl (only if running a trusted peer)

## trusted peer

Trusted peer setup is a bit of an annoying task, and only needs to be done if you are interested in running your own cluster. If so make sure to read the instructions [provided by the ipfs cluster team](https://cluster.ipfs.io/documentation/collaborative/setup/)

## follow peer

First ensure that you valid a valid go-ipfs instance up and running on the machine you are rusing, and run the following command:

```shell
$> ipfs-cluster-follow 2020pb-dataset run --init 2020pb.temporal.cloud
```

This will start the cluster follow peer and being replicating the cluster data