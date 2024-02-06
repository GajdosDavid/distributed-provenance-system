import json


class Config:

    def __init__(self, config_path):
        self.fqdn = ""
        self.tp_fqdn = ""

        self._load_config(config_path)

    def _load_config(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)

        required_config_fields = ("fqdn", "trustedPartyFqdn")
        for field in required_config_fields:
            assert field in config, f"{field} missing in config!"

        self.fqdn = config['fqdn']
        if self.fqdn[-1] == '/':
            self.fqdn = self.fqdn[:-1]

        self.tp_fqdn = config['trustedPartyFqdn']
        if self.tp_fqdn[-1] == '/':
            self.tp_fqdn = self.tp_fqdn[:-1]
