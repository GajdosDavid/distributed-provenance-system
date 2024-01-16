from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from prov.model import ProvDocument
import base64
import jcs
import cryptography.exceptions

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

        self._prov_document = None

    def get_document(self):
        if self._prov_document is None:
            raise ValueError("Prov graph not yet validated")
        return self._prov_document

    def verify_token(self):
        if not self._verify_signature():
            raise cryptography.exceptions.InvalidSignature()

    def validate_token(self, organization_id):
        # TODO -- assert all the mandatory fields are present in token
        if self._token['data']['originatorId'] != organization_id:
            raise ValueError()

        if not self._hash_matches():
            raise IncorrectHash()

    def validate_graph(self, graph_id):
        # TODO -- check that graph is normalized + contains resolvable PIDs
        # TODO -- find out format from the grpah
        self._prov_document = ProvDocument.deserialize(content=self._graph, format="rdf")

        assert self._prov_document.has_bundles(), 'No bundles inside the document!'
        assert len(self._prov_document.bundles) == 1, 'Only one bundle allowed in document!'

        for bundle in self._prov_document.bundles:
            if bundle.identifier.localpart != graph_id:
                raise ValueError()

    def _hash_matches(self):
        digest = hashes.Hash(hashes.SHA256())
        digest.update(self._graph)

        return self._token['data']['graphImprint'] == digest.finalize().hex()

    def _verify_signature(self):
        for cert in cert_manager.get_all_certs():
            try:
                pk = cert.to_cryptography().public_key()
                pk.verify(
                    signature=self._signature,
                    data=jcs.canonicalize(self._token['data']),
                    padding=padding.PKCS1v15(),
                    algorithm=hashes.SHA256()
                )

                return True
            except cryptography.exceptions.InvalidSignature:
                pass

        return False
