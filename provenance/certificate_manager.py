from OpenSSL import crypto

root_cert = b"""
-----BEGIN CERTIFICATE-----
MIIDHDCCAgSgAwIBAgIBAjANBgkqhkiG9w0BAQsFADAdMQswCQYDVQQGEwJDWjEO
MAwGA1UEAwwFR2FqZGEwHhcNMjMxMjAyMTM1MjU0WhcNMzMxMDEzMTM1MjU0WjAd
MQswCQYDVQQGEwJDWjEOMAwGA1UEAwwFR2FqZGEwggEiMA0GCSqGSIb3DQEBAQUA
A4IBDwAwggEKAoIBAQDI4KlsARI8dYzeXVRpQdlLlSfwYAql4Px2XrRdigV2DMDG
n90A08dRwhBoUiPW0gF/g1G/itSYixkWLQzg2tWS4l8H/QVxzx4AU7MNx9OUqzeu
5xDjQEyI4TARXT2oDNqDLRygay/cMLhUz/Ihw5HGsxO2ANk5awancoaM0nujFM3L
NVBNbzMElDhs+GfPWB4+4gN2yJ2r02CtY705MW8v4QqWRFPiyIDQNulkmDknsSCg
PopnFfXNo1PHNdwZKToMvxh8I7vJUM44knOnHf/+qRYcGkpCF96sr5wlCVh8bEuN
aEgOtR1AjUEBWq2iCzWSJ4eZG7F+tCEjZplDOnoHAgMBAAGjZzBlMA8GA1UdEwEB
/wQFMAMBAf8wDgYDVR0PAQH/BAQDAgIEMCMGA1UdEQEB/wQZMBeGFXVybjp1dWlk
OkRhdmlkLUdhamRvczAdBgNVHQ4EFgQUBtxnI1te16lJhty/O5ZSW9O72V0wDQYJ
KoZIhvcNAQELBQADggEBAEkqDIL79UKmCpeef+G7jaTBgUmbzxdXjE+codtVvjdo
99dhJyLSxVPcWwVG2h9/M0oOWTTcodrPEHAQ7+cpMhdCHiFziB6R2syGOHxLRktn
FAgVV1JYtVYEnmPaFC/kSDXmAcjDFJrHBNOFbcfJhj+DOzVZ7vq6MbMl8b9vKdHE
cOdQn0v7KKB1ZnxbEjPhJezIbnP8LGTGIF9SOXGrjcwh0JJIZGGzKIlujgKIHiNJ
xLPsTjgBg5P91Z7j2b4kgRczg/kq5Bl9ijRC7ogfEVveSzBC1YoHneALSf71EsEp
iF1GosspRq0Su6ag97loUUj3J/SVNmxAbhK5PGRaHw0=
-----END CERTIFICATE-----
"""


class CertManager(object):
    _instance = None
    _store = crypto.X509Store()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CertManager, cls).__new__(
                cls, *args, **kwargs)
            cls._initialize_store(cls._instance)
        return cls._instance

    def _initialize_store(self):
        self._store.add_cert(crypto.load_certificate(crypto.FILETYPE_PEM, root_cert))

    def add_trusted_cert(self):
        pass

    def verify_certificate(self, cert_to_verify, intermediate_certs):
        user_cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_to_verify)
        intermediates_certs = [crypto.load_certificate(crypto.FILETYPE_PEM, cert) for cert in intermediate_certs]

        store_ctx = crypto.X509StoreContext(self._store, user_cert, intermediates_certs)
        store_ctx.verify_certificate()


cert_manager = CertManager()
