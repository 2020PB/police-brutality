#! /bin/bash

# yoinked from https://github.com/RTradeLtd/cord19-collaborative-cluster/blob/master/scripts/install_cluster.sh
# multi-platform cluster download script, only supports linux 64-bit right now

VERSION="v0.12.1"
OS=""
case "$1" in 
    linux-64bit)
        OS="linux-amd64"
        wget "https://dist.ipfs.io/ipfs-cluster-service/${VERSION}/ipfs-cluster-service_${VERSION}_${OS}.tar.gz"
        wget "https://dist.ipfs.io/ipfs-cluster-ctl/${VERSION}/ipfs-cluster-ctl_${VERSION}_${OS}.tar.gz"
        wget "https://dist.ipfs.io/ipfs-cluster-follow/${VERSION}/ipfs-cluster-follow_${VERSION}_${OS}.tar.gz"
        tar zxvf "ipfs-cluster-service_${VERSION}_${OS}.tar.gz"
        tar zxvf "ipfs-cluster-ctl_${VERSION}_${OS}.tar.gz"
        tar zxvf "ipfs-cluster-follow_${VERSION}_${OS}.tar.gz"
        (cd ipfs-cluster-service && sudo cp ipfs-cluster-service /usr/local/bin)
        (cd ipfs-cluster-ctl && sudo cp ipfs-cluster-ctl /usr/local/bin)
        (cd ipfs-cluster-follow && sudo cp ipfs-cluster-follow /usr/local/bin)
        ;;
    *)
        echo "unsupported os"
        exit 2
        ;;
esac