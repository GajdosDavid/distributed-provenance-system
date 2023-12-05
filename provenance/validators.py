from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64
from prov.model import ProvDocument


class InvalidGraph(Exception):
    pass


class GraphInputValidator:

    def __init__(self, json_data):
        self._graph = base64.b64decode(json_data['graph']['data'])
        self._signature = base64.b64decode(json_data['signature'])
        self._user_cert = json_data['certificates']['user_cert']

        self._prov_graph = None

    def get_graph(self):
        return self._prov_graph

    def verify_signature(self):
        cert = x509.load_pem_x509_certificate(bytes(self._user_cert, 'utf-8'))
        pk = cert.public_key()
        pk.verify(
            signature=self._signature,
            data=self._graph,
            padding=padding.PKCS1v15(),
            algorithm=hashes.SHA256()
        )

    def validate_graph(self):
        self._prov_graph = ProvDocument.deserialize(content=self._graph, format="rdf")
        pass