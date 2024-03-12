from django.apps import AppConfig
from distributed_prov_system.settings import config
from .models import DefaultTrustedParty
from neomodel.exceptions import DoesNotExist
import requests
import json


class ProvenanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'provenance'

    def ready(self):
        pass
        # TODO -- uncomment when TP is running
        # resp = requests.get(f'http://{config.tp_fqdn}/info')
        #
        # assert resp.ok, "Couldn't retrieve info from TP!"
        # info = json.loads(resp.content)
        #
        # try:
        #     DefaultTrustedParty.nodes.get(identifier=info['id'])
        # except DoesNotExist:
        #     # Only one DefaultTP expected!
        #     for node in DefaultTrustedParty.nodes.all():
        #         node.delete()
        #
        #     tp = DefaultTrustedParty()
        #     tp.identifier = info['id']
        #     tp.url = config.tp_fqdn
        #     tp.certificate = info['certificate']
        #     tp.save()
