package nhi

import "strings"

type IdentityProvider struct{}

func NewIdentityProvider() *IdentityProvider {
	return &IdentityProvider{}
}

func (i *IdentityProvider) Verify(attestation string) bool {
	return strings.HasPrefix(attestation, "pqsig:") && len(attestation) > len("pqsig:")
}
