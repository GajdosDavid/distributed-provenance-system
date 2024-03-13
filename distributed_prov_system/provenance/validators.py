from prov.model import ProvDocument, ProvEntity, ProvActivity
from neomodel.match import Traversal, INCOMING
import base64
import requests
import concurrent.futures

from .models import Document, Organization, Entity
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


def is_org_registered_at_TP(organization_id) -> bool:
    # resp = requests.get(f'http://{config.tp_fqdn}/organizations/{organization_id}')

    # TODO -- change once TP is up and running
    # return resp.ok

    return True


def is_org_registered(organization_id) -> bool:
    try:
        # check if organization already exists
        Organization.nodes.get(identifier=organization_id)

        return True
    except DoesNotExist:
        return False


def check_organization_is_registered(organization_id):
    if is_org_registered_at_TP(organization_id):
        return

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


def check_graph_id_belongs_to_meta(main_activity_id, graph_id, organization_id):
    entity = Entity.nodes.get(identifier=f'{organization_id}_{graph_id}')
    definition = dict(node_class=Entity, direction=INCOMING,
                      relation_type="was_derived_from", model=None)
    entity_traversal = Traversal(entity, Entity.__label__, definition)
    if len(list(entity_traversal.all())) != 0:
        raise DocumentError(f"Graph with given id={graph_id} is not the latest version."
                            f" CPM does not allow version forks.")

    meta_bundle = list(entity.contains.all())
    assert len(meta_bundle) == 1, "Entity cannot be part of more than one meta bundles"

    if meta_bundle[0].identifier != main_activity_id:
        raise DocumentError(f"Graph with id={graph_id} is part of meta bundle with id={meta_bundle[0].identifier},"
                            f" however main_activity from given bundle is resolvable to different id={main_activity_id}")


def send_signature_verification_request(payload, organization_id):
    url = 'http://' + config.tp_fqdn + '/verify'

    payload['organizationId'] = organization_id
    resp = requests.post(url, payload)

    return resp


class InputGraphChecker:

    def __init__(self, graph, format):
        self._graph = base64.b64decode(graph)
        self._graph_format = format

        self._prov_document = None
        self._prov_bundle = None
        self._main_activity = None

    def get_document(self):
        assert self._prov_document is not None, "Graph not yet parsed"

        return self._prov_document

    def get_bundle_id(self):
        assert self._prov_bundle is not None, "Graph not yet parsed"

        return self._prov_bundle.identifier.localpart

    def get_main_activity_id(self):
        assert self._prov_bundle is not None, "Graph not yet parsed"

        return self._main_activity.identifier.localpart

    def parse_graph(self):
        self._prov_document = ProvDocument.deserialize(content=self._graph, format=self._graph_format)

        self._prov_bundle = list(self._prov_document.bundles)[0]
        self._main_activity = self._retrieve_main_activity()

    def check_ids_match(self, graph_id):
        if self._prov_bundle.identifier.localpart != graph_id:
            raise DocumentError(f'The bundle id={self._prov_bundle.identifier.localpart} does not match the '
                                f'specified id={graph_id} from query.')

    def validate_graph(self):
        assert self._prov_document is not None and self._prov_bundle is not None, 'Parse the graph first!'

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
        connectors = self._retrieve_connectors_from_graph()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self._is_pid_resolvable, connector): connector for connector in connectors}

        for future in concurrent.futures.as_completed(futures):
            connector = futures[future]
            if not future.result():
                return False, f'ForwardConnector/BackwardConnector with id=[{connector.identifier.localpart}] has incorrectly resolvable PID'

        # Check for resolvability of MainActivity cannot be done as one meta-prov can contain multiple version chains
        # plus it might not exist yet if it's the first chain in meta-prov
        # if not self._is_pid_resolvable(main_activity):
        #     return False, f'MainActivity with id={main_activity.identifier.localpar} has incorrectly resolvable PID'

        return True, ""

    def _is_pid_resolvable(self, element):
        url = element.identifier.uri

        resp = requests.get(url)

        return resp.ok

    def _retrieve_main_activity(self):
        # TODO -- rather retrieve what this resolves to and not the id of activity
        # TODO -- check that this resolves to my IP
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

    def _retrieve_connectors_from_graph(self):
        connectors = []

        for entity in self._prov_bundle.get_records(ProvEntity):
            prov_types = entity.get_asserted_types()

            if prov_types is None:
                continue

            for t in prov_types:
                if t.localpart == 'forwardConnector' or t.localpart == 'backwardConnector':
                    connectors.append(entity)

        return connectors
