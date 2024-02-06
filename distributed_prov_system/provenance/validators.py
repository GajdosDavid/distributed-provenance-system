from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from prov.model import ProvDocument, ProvEntity, ProvActivity
import base64
import jcs
import cryptography.exceptions
import requests

from .models import Document
from neomodel.exceptions import DoesNotExist
from distributed_prov_system.settings import config


class HasNoBundles(Exception):
    pass


class TooManyBundles(Exception):
    pass


class IncorrectPIDs(Exception):
    pass


class DocumentError(Exception):
    pass


def graph_already_exists(organization_id, graph_id) -> bool:
    try:
        # check if document already exists
        Document.nodes.get(identifier=f"{organization_id}_{graph_id}")

        return True
    except DoesNotExist:
        return False


def send_signature_verification_request(json_data):
    url = 'http://' + config.tp_fqdn + '/verify'

    resp = requests.post(url, json_data)

    return resp


class InputGraphChecker:

    def __init__(self, graph):
        self._graph = base64.b64decode(graph)

        self._prov_document = None
        self._prov_bundle = None

    def get_document(self):
        assert self._prov_document is not None, "Graph not yet parsed"

        return self._prov_document

    def parse_graph(self):
        # TODO -- find out format from the grpah
        self._prov_document = ProvDocument.deserialize(content=self._graph, format="rdf")

        # this will happen only once, however cannot be indexed, so it needs to be done inside loop
        for bundle in self._prov_document.bundles:
            self._prov_bundle = bundle

    def check_ids_match(self, graph_id):
        if self._prov_bundle.identifier.localpart != graph_id:
            raise DocumentError(f'The bundle id={self._prov_bundle.identifier.localpart} does not match the '
                                f'specified id={graph_id} from query.')

        return True

    def validate_graph(self, graph_id):
        assert self._prov_document is not None and self._prov_bundle is not None, 'Parse the graph first!s'

        if not self._prov_document.has_bundles():
            raise HasNoBundles('There are no bundles inside the document!')

        if len(self._prov_document.bundles) != 1:
            raise TooManyBundles('Only one bundle expected in document!')

        if not self._is_graph_normalized():
            raise DocumentError(f'The bundle with id={self._prov_bundle.identifier.localpart} is not normalized.')

        are_resolvable, error_msg = self._are_pids_resolvable()
        if not are_resolvable:
            raise IncorrectPIDs(error_msg)

    def _is_graph_normalized(self):
        # TODO -- implement
        return True

    def _are_pids_resolvable(self):
        forward_connectors, backward_connectors = self._retrieve_backward_and_forward_conns()
        main_activity = self._retrieve_main_activity()

        for connector in forward_connectors:
            if not self._is_pid_resolvable(connector):
                return False, f'ForwardConnector with id={connector.identifier.localpart} has incorrectly resolvable PID'

        for connector in backward_connectors:
            if not self._is_pid_resolvable(connector):
                return False, f'BackwardConnector with id={connector.identifier.localpart} has incorrectly resolvable PID'

        # Check for resolvability of MainActivity cannot be done as one meta-prov can contain multiple version chains
        # if not self._is_pid_resolvable(main_activity):
        #     return False, f'MainActivity with id={main_activity.identifier.localpar} has incorrectly resolvable PID'

        return True, ""

    def _is_pid_resolvable(self, element):
        url = element.identifier.uri

        resp = requests.get(url)

        return resp.status_code == 200

    def _retrieve_main_activity(self):
        main_activity = None

        for activity in self._prov_bundle.get_records(ProvActivity):
            prov_types = activity.get_asserted_types()

            if prov_types is None:
                continue

            for t in prov_types:
                if t.localpart == 'mainActivity':
                    if main_activity is not None:
                        raise DocumentError(f"Multiple 'mainActivity' activities specified inside of bundle "
                                            f"{self._prov_bundle.identifier.localpart}")

                    main_activity = activity
                    break

        return main_activity

    def _retrieve_backward_and_forward_conns(self):
        forward_connectors = []
        backward_connectors = []

        for entity in self._prov_bundle.get_records(ProvEntity):
            prov_types = entity.get_asserted_types()

            if prov_types is None:
                continue

            for t in prov_types:
                if t.localpart == 'forwardConnector':
                    forward_connectors.append(entity)
                elif t.localpart == 'backwardConnector':
                    backward_connectors.append(entity)

        return forward_connectors, backward_connectors
