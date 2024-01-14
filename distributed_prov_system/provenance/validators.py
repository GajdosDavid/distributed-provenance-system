from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from prov.model import ProvDocument
import base64
import jcs

from .certificate_manager import cert_manager


class InvalidGraph(Exception):
    pass


class IncorrectHash(Exception):
    pass


class GraphInputValidator:

    def __init__(self, json_data):
        self._graph = base64.b64decode(json_data['graph'])
        self._token = json_data['token']
        self._signature = base64.b64decode(self._token['signature'])

        self._prov_graph = None

    def get_graph(self):
        if self._prov_graph is None:
            raise ValueError("Prov graph not yet validated")
        return self._prov_graph

    def verify_token(self):
        # TODO -- try primary trusted party and then secondary
        cert = cert_manager.get_primary_ttp_cert().to_cryptography()
        pk = cert.public_key()
        pk.verify(
            signature=self._signature,
            data=jcs.canonicalize(self._token['data']),
            padding=padding.PKCS1v15(),
            algorithm=hashes.SHA256()
        )

        if not self._hash_matches():
            raise IncorrectHash()

    def validate_graph(self):
        # TODO -- check that graph is normalized + contains resolvable PIDs
        # TODO -- find out format from the grpah
        self._prov_graph = ProvDocument.deserialize(content=self._graph, format="rdf")

        assert self._prov_graph.has_bundles(), 'No bundles inside the document!'

    def _hash_matches(self):
        digest = hashes.Hash(hashes.SHA256())
        digest.update(self._graph)

        return self._token['data']['graphImprint'] == digest.finalize().hex()
