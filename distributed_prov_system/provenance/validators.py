from prov.model import ProvDocument, ProvEntity, ProvActivity
from neomodel.match import Traversal, INCOMING
import base64
import requests
import concurrent.futures
from urllib.parse import urlparse
import socket
import json

from .models import Document, Organization, Entity, Bundle, ConnectorTable
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


class OrganizationNotRegistered(Exception):
    pass


class UncheckedTrustedParty(Exception):
    pass


class InvalidTrustedParty(Exception):
    pass


def is_org_registered(organization_id) -> bool:
    try:
        # check if organization already exists
        Organization.nodes.get(identifier=organization_id)

        return True
    except DoesNotExist:
        return False


def check_organization_is_registered(organization_id):
    if not is_org_registered(organization_id):
        raise OrganizationNotRegistered(f"Organization with id [{organization_id}] is not registered! "
                                        f"Please register your organization first.")

    org = Organization.nodes.get(identifier=organization_id)
    tp = list(org.trusts.all())[0]
    if not tp.checked:
        raise UncheckedTrustedParty(f"Trusted party for organization with id [{organization_id}] has not yet been "
                                    f"checked for its validity. Please be patient.")

    if not tp.valid:
        raise InvalidTrustedParty(f"Trusted party for organization with id [{organization_id}] has been checked "
                                  f"and is not considered valid. For more information contact administrator.")


def graph_exists(organization_id, graph_id) -> bool:
    try:
        # check if document already exists
        Document.nodes.get(identifier=f"{organization_id}_{graph_id}")

        return True
    except DoesNotExist:
        return False


def check_graph_id_belongs_to_meta(meta_provenance_id, graph_id, organization_id):
    entity = Entity.nodes.get(identifier=f'{organization_id}_{graph_id}')
    definition = dict(node_class=Entity, direction=INCOMING,
                      relation_type="was_derived_from", model=None)
    entity_traversal = Traversal(entity, Entity.__label__, definition)

    try:
        Bundle.nodes.get(identifier=meta_provenance_id)
    except DoesNotExist:
        raise DocumentError(f"Meta provenance with id [{meta_provenance_id}] does not exist!")

    if len(list(entity_traversal.all())) != 0:
        raise DocumentError(f"Graph with given id [{graph_id}] is not the latest version."
                            f" CPM does not allow version forks.")

    meta_bundle = list(entity.contains.all())
    assert len(meta_bundle) == 1, "Entity cannot be part of more than one meta bundles"

    if meta_bundle[0].identifier != meta_provenance_id:
        raise DocumentError(f"Graph with id [{graph_id}] is part of meta bundle with id [{meta_bundle[0].identifier}],"
                            f" however main_activity from given bundle is resolvable to different id [{meta_provenance_id}]")


def send_signature_verification_request(payload, organization_id):
    url = 'http://' + config.tp_fqdn + '/api/v1/verifySignature'

    payload['organizationId'] = organization_id
    resp = requests.post(url, json.dumps(payload))

    return resp


class InputGraphChecker:

    def __init__(self, graph, format):
        self._graph = base64.b64decode(graph)
        self._graph_format = format

        self._prov_document = None
        self._prov_bundle = None
        self._main_activity = None
        self._meta_provenance_id = None
        self._forward_connectors = None
        self._backward_connectors = None
        self._processed_forward_connectors = None
        self._processed_backward_connectors = None

    def get_document(self):
        assert self._prov_document is not None, "Graph not yet parsed"

        return self._prov_document

    def get_bundle_id(self):
        assert self._prov_bundle is not None, "Graph not yet parsed"

        return self._prov_bundle.identifier.localpart

    def get_meta_provenance_id(self):
        assert self._meta_provenance_id is not None, "Graph not yet parsed"

        return self._meta_provenance_id

    def get_forward_connectors(self):
        assert self._processed_forward_connectors is not None, "Graph not yet validated!"

        return self._processed_forward_connectors

    def get_backward_connectors(self):
        assert self._processed_backward_connectors is not None, "Graph not yet validated!"

        return self._processed_backward_connectors

    def parse_graph(self):
        self._prov_document = ProvDocument.deserialize(content=self._graph, format=self._graph_format)

        self._prov_bundle = list(self._prov_document.bundles)[0]
        self._main_activity = self._retrieve_main_activity()
        self._meta_provenance_id = self._check_resolvability_and_retrieve_meta_id()
        self._forward_connectors, self._backward_connectors = self._retrieve_connectors_from_graph()

    def check_ids_match(self, graph_id):
        if self._prov_bundle.identifier.localpart != graph_id:
            raise DocumentError(f'The bundle id [{self._prov_bundle.identifier.localpart}] does not match the '
                                f'specified id [{graph_id}] from query.')

    def validate_graph(self):
        assert self._prov_document is not None and self._prov_bundle is not None, 'Parse the graph first!'

        if not self._prov_document.has_bundles():
            raise HasNoBundles('There are no bundles inside the document!')

        if len(self._prov_document.bundles) != 1:
            raise TooManyBundles('Only one bundle expected in document!')

        if not self._is_graph_normalized():
            raise DocumentError(f'The bundle with id [{self._prov_bundle.identifier.localpart}] is not normalized.')

        are_resolvable, error_msg = self._are_pids_resolvable()
        if not are_resolvable:
            raise IncorrectPIDs(error_msg)

    def _is_graph_normalized(self):
        # TODO -- implement
        return True

    def _are_pids_resolvable(self):
        self._processed_forward_connectors = []
        self._processed_backward_connectors = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            backward_conns_futures = {executor.submit(self._ping_connector, connector): connector for connector in self._backward_connectors}
            forward_conns_futures = {executor.submit(self._ping_connector, connector): connector for connector in self._forward_connectors}

        for future in concurrent.futures.as_completed(backward_conns_futures):
            connector = backward_conns_futures[future]
            resp = future.result()
            if not resp.ok:
                return False, f'BackwardConnector with id [{connector.identifier.localpart}] has incorrectly resolvable PID'

            parsed_url = urlparse(resp.url)
            if self._contains_my_ip_addr(parsed_url):
                self._processed_backward_connectors.append(connector)

        for future in concurrent.futures.as_completed(forward_conns_futures):
            connector = forward_conns_futures[future]
            resp = future.result()
            parsed_url = urlparse(resp.url)
            if not self._contains_my_ip_addr(parsed_url):
                if not resp.ok:
                    return False, f'ForwardConnector with id [{connector.identifier.localpart}] has incorrectly resolvable PID'
            else:
                if "/api/v1/connectors/" not in parsed_url.path:
                    return False, f'ForwardConnector with id [{connector.identifier.localpart}] has incorrectly resolvable PID'

                self._processed_forward_connectors.append(connector)

        return True, ""

    def _contains_my_ip_addr(self, url):
        ip = url.netloc.split(':')[0]

        try:
            socket.inet_aton(ip)
        except socket.error:
            ip = socket.gethostbyname(ip)

        return ip in socket.gethostbyname_ex(socket.gethostname())[-1]

    def _ping_connector(self, connector):
        url = connector.identifier.uri
        resp = requests.get(url)

        return resp

    def _check_resolvability_and_retrieve_meta_id(self):
        meta_pid = None
        attrs = self._main_activity.attributes
        for (key, value) in self._main_activity.attributes:
            if str(key) == 'cpm:metabundle':
                meta_pid = value

        if meta_pid is None:
            raise DocumentError(f"MainActivity missing required attributes 'cpm:metabundle'.")

        resp = requests.get(meta_pid.uri)
        parsed_url = urlparse(resp.url)
        ip = parsed_url.netloc.split(':')[0]

        try:
            socket.inet_aton(ip)
        except socket.error:
            ip = socket.gethostbyname(ip)

        if ip not in socket.gethostbyname_ex(socket.gethostname())[-1]:
            raise DocumentError(f"MainActivity PID is expected to be resolvable to this server's "
                                f"IP address, however it resolved to [{ip}]")

        if "/api/v1/graphs/meta/" not in parsed_url.path:
            raise DocumentError(f"MainActivity PID resolves to incorrect path [{parsed_url.path}]. "
                                f"Expected: /api/v1/graphs/meta/")

        return parsed_url.path.split('/')[-1]

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
                                            f"[{self._prov_bundle.identifier.localpart}]")

                    main_activity = activity
                    break

        return main_activity

    def _retrieve_connectors_from_graph(self):
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
