from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from prov.model import ProvDocument, ProvEntity, ProvActivity
import base64
import jcs
import cryptography.exceptions
import requests

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
        self._prov_bundle = None

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

    def validate_graph(self, graph_id, is_post=True):
        # TODO -- find out format from the grpah
        self._prov_document = ProvDocument.deserialize(content=self._graph, format="rdf")

        assert self._prov_document.has_bundles(), 'No bundles inside the document!'
        assert len(self._prov_document.bundles) == 1, 'Only one bundle allowed in document!'

        for bundle in self._prov_document.bundles:
            self._prov_bundle = bundle

        if not self._are_pids_resolvable() or not self._is_graph_normalized():
            raise ValueError()

        if is_post and self._prov_bundle.identifier.localpart != graph_id:
            raise ValueError()

    def _is_graph_normalized(self):
        # TODO -- implement
        return True

    def _are_pids_resolvable(self):
        forward_connectors = []
        backward_connectors = []
        main_activity = None

        for entity in self._prov_bundle.get_records(ProvEntity):
            prov_types = entity.get_asserted_types()

            if prov_types is None:
                continue

            for t in prov_types:
                if t.localpart == 'forwardConnector':
                    forward_connectors.append(entity)
                elif t.localpart == 'backwardConnector':
                    backward_connectors.append(entity)

        for activity in self._prov_bundle.get_records(ProvActivity):
            prov_types = activity.get_asserted_types()

            if prov_types is None:
                continue

            for t in prov_types:
                if t.localpart == 'mainActivity':
                    if main_activity is not None:
                        # Only one main_activity allowed
                        return False

                    main_activity = activity
                    break

        for connector in forward_connectors:
            if not self._is_pid_resolvable(connector):
                return False

        for connector in backward_connectors:
            if not self._is_pid_resolvable(connector):
                return False

        # TODO -- uncomment once the question about mainActivity is resolved with Wittner
#        if not self._is_pid_resolvable(main_activity):
 #           return False

        return True

    def _is_pid_resolvable(self, connector):
        url = connector.identifier.uri

        resp = requests.get(url)

        return resp.status_code == 200

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
