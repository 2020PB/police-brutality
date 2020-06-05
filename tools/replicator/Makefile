.PHONY: cluster-first-start
cluster-first-start:
	ipfs-cluster-service init --consensus crdt
	ipfs-cluster-service daemon

.PHONY: follow-public-cluster
follow-public-cluster:
	ipfs-cluster-follow 2020pb-dataset run --init 2020pb.temporal.cloud