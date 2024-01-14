from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
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

    def get_graph(self):
        return self._graph.decode('utf-8')

    def verify_token(self):
        # TODO -- try primary trusted party and then secondary
        cert = cert_manager.get_primary_ttp_cert().to_cryptography()
        pk = cert.public_key()
        print(self._signature)
        pk.verify(
            signature=self._signature,
            data=jcs.canonicalize(self._token['data']),
            padding=padding.PKCS1v15(),
            algorithm=hashes.SHA256()
        )

        print(self._token)

        if not self._hash_matches():
            raise IncorrectHash()

    def validate_graph(self):
        # TODO -- check that graph is normalized + contains resolvable PIDs
        pass

    def _hash_matches(self):
        digest = hashes.Hash(hashes.SHA256())
        digest.update(self._graph)

        return self._token['data']['graphImprint'] == digest.finalize().hex()
