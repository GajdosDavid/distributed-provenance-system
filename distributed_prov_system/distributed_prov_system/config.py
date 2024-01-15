import json


class Config:

    def __init__(self, config_path):
        self.primary_cert = ""
        self.secondary_certs = []

        self._load_config(config_path)

    def _load_config(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)

        if "primaryCertificate" in config:
            self.primary_cert = config['primaryCertificate']
        if "secondaryCertificates" in config:
            self.secondary_certs = config['secondaryCertificates']