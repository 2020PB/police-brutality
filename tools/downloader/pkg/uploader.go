package pkg

import (
	ipfsapi "github.com/RTradeLtd/go-ipfs-api/v3"
)

// Uploader specifies the interface for an uploader client
type Uploader interface {
	Upload(path string) (string, error)
}

// IPFSUploader allows uploading videos to an ipfs endpoint
type IPFSUploader struct {
	sh *ipfsapi.Shell
}

// NewIPFSUploader returns an IPFS uploader, authenticated with a JWT if required
// JWT authentication is only very useful for third-party endpoitns
func NewIPFSUploader(endpoint, authToken string) (Uploader, error) {
	sh := ipfsapi.NewDirectShell(endpoint)
	if authToken != "" {
		sh = sh.WithAuthorization(authToken, nil)
	}
	// if this fails, the IPFS API is not enabled
	if _, err := sh.NewObject(""); err != nil {
		return nil, err
	}
	return &IPFSUploader{sh}, nil
}

// Upload stores the given data at path onto IPFS
func (iu *IPFSUploader) Upload(path string) (string, error) {
	return iu.sh.AddDir(path)
}
