from OpenSSL import crypto
from distributed_prov_system.settings import config


class CertManager(object):
    _instance = None
    _primary_cert = None
    _secondary_certs = set()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CertManager, cls).__new__(
                cls, *args, **kwargs)
            cls._initialize(cls._instance)
        return cls._instance

    def _initialize(self):
        if config.primary_cert:
            self._primary_cert = crypto.load_certificate(crypto.FILETYPE_PEM, config.primary_cert)
        else:
            # Load from DB
            pass
        if config.secondary_certs:
            for cert in config.secondary_certs:
                self._secondary_certs.add(crypto.load_certificate(crypto.FILETYPE_PEM, cert))
        #load secondary from DB

    def add_trusted_cert(self):
        pass

    # def verify_certificate(self, cert_to_verify, intermediate_certs):
    #     user_cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_to_verify)
    #     intermediates_certs = [crypto.load_certificate(crypto.FILETYPE_PEM, cert) for cert in intermediate_certs]
    #
    #     store_ctx = crypto.X509StoreContext(self._store, user_cert, intermediates_certs)
    #     store_ctx.verify_certificate()

    def get_primary_cert(self):
        return self._primary_cert

    def get_all_certs(self):
        all_certs = [self._primary_cert]

        if self._secondary_certs:
            all_certs.append(self._secondary_certs)

        return all_certs


cert_manager = CertManager()
