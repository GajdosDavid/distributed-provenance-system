from prov.model import ProvDocument, ProvBundle, ProvActivity, ProvAgent, QualifiedName, Namespace, ProvEntity
from distributed_prov_system.settings import config
from neomodel.match import Traversal, INCOMING, OUTGOING
from provenance.models import Entity, Activity, Agent

DEFAULT_NAMESPACE = config.fqdn

NAMESPACES = {
    "prov": Namespace("prov", "http://www.w3.org/ns/prov#"),
    "meta": Namespace("meta", DEFAULT_NAMESPACE + f"/api/v1/graphs/meta/"),
    "pav": Namespace("pav", "http://purl.org/pav/"),
    "cpm": Namespace("cpm", "https://www.commonprovenancemodel.org/cpm-namespace-v1-0/"),
    "connectors": Namespace("connectors", DEFAULT_NAMESPACE + "/api/v1/connectors/")
}


def convert_meta_to_prov(neo_bundle):
    def get_gen_entities(bundle):
        definition = dict(node_class=Entity, direction=OUTGOING,
                          relation_type="contains", model=None)
        traversal = Traversal(bundle, Entity.__label__, definition)

        g_entities = []
        for entity in traversal.all():
            if entity.identifier[-4:] == "_gen":
                g_entities.append(entity)

        return g_entities

    identifier = neo_bundle.identifier
    document = ProvDocument(namespaces=[NAMESPACES["meta"]])

    prov_bundle = ProvBundle(identifier=QualifiedName(NAMESPACES["meta"], identifier))
    prov_bundle.set_default_namespace(DEFAULT_NAMESPACE)

    # Retrieve gen entities first as I'll be able to create individual chains
    # by using the specialization_of relationship
    gen_entities = get_gen_entities(neo_bundle)
    for gen_entity in gen_entities:
        add_version_chain_to_bundle(prov_bundle, gen_entity)

    document.add_bundle(prov_bundle)

    return document


def convert_attributes_to_dict(neo_element):
    attributes = dict()
    for key, value in neo_element.attributes.items():
        ns, localpart = key.split(':')

        attributes.update({QualifiedName(NAMESPACES[ns], localpart): value})

    return attributes


def add_version_chain_to_bundle(bundle: ProvBundle, gen_entity: Entity):
    def get_sorted_specialized_entities_from_gen(g_entity):
        definition = dict(node_class=Entity, direction=INCOMING,
                          relation_type="specialization_of", model=None)
        traversal = Traversal(g_entity, Entity.__label__, definition)
        entities = list(traversal.all())
        entities.sort(key=lambda e: e.attributes['pav:version'])

        return entities

    def get_entity_qualified_name(entity: Entity):
        org, id = entity.identifier.split('_', 1)

        try:
            ns = NAMESPACES[org]
        except KeyError:
            ns = Namespace(org, config.fqdn + f"/api/v1/organizations/{org}/graphs/")
            NAMESPACES[org] = ns

        return QualifiedName(ns, id)

    def add_new_version_to_bundle(gen: ProvEntity, new_version_entity: Entity, prev_version_entity: ProvEntity = None):
        qn = get_entity_qualified_name(new_version_entity)
        attrs = convert_attributes_to_dict(new_version_entity)
        e = bundle.entity(qn, attrs)

        e.specializationOf(gen)
        if prev_version_entity is not None:
            attribute = {QualifiedName(NAMESPACES['prov'], "type"): "prov:Revision"}
            e.wasDerivedFrom(prev_version_entity, attributes=attribute)

        return e

    def add_signing_activity_to_bundle(neo_entity: Entity, trusted_party: ProvAgent, signed_version: Entity):
        neo_activity = list(neo_entity.used.all())[0]
        org, id = neo_activity.identifier.split('_', 1)
        attrs = convert_attributes_to_dict(neo_activity)

        a = bundle.activity(id, neo_activity.start_time, neo_activity.end_time, attrs)
        a.used(signed_version)
        a.wasAssociatedWith(trusted_party)

        return a

    def add_trusted_party_to_bundle(neo_entity: Entity):
        neo_activity = list(neo_entity.used.all())[0]
        neo_agent = list(neo_activity.was_associated_with.all())[0]
        agent = bundle.get_record(neo_agent.identifier)
        if len(agent) > 0:
            return agent[0]
        else:
            attrs = convert_attributes_to_dict(neo_agent)
            return bundle.agent(neo_agent.identifier, attrs)

    def add_token_to_bundle(neo_entity: Entity, activity: ProvActivity, tp: ProvAgent):
        neo_activity = list(neo_entity.used.all())[0]
        neo_token = list(neo_activity.was_generated_by.all())[0]

        t = bundle.entity(neo_token.identifier, convert_attributes_to_dict(neo_token))
        t.wasGeneratedBy(activity)
        t.wasAttributedTo(tp)

    gen_prov_entity = ProvEntity(bundle, get_entity_qualified_name(gen_entity),
                                 attributes=convert_attributes_to_dict(gen_entity))
    specialized_entities = get_sorted_specialized_entities_from_gen(gen_entity)
    previous_version_entity = None
    for neo_entity in specialized_entities:
        version_entity = add_new_version_to_bundle(gen_prov_entity, neo_entity, previous_version_entity)
        tp = add_trusted_party_to_bundle(neo_entity)
        activity = add_signing_activity_to_bundle(neo_entity, tp, version_entity)
        add_token_to_bundle(neo_entity, activity, tp)

        previous_version_entity = version_entity

    bundle.add_record(gen_prov_entity)


def convert_connector_table_to_prov(neo_bundle):
    def get_forward_connectors(bundle):
        connectors = []

        for conn in bundle.contains.all():
            for key, value in conn.attributes.items():
                if key == 'prov:type' and value == 'cpm:forwardConnectorBundle':
                    connectors.append(conn)

        return connectors

    def get_entity_qualified_name(entity: Entity):
        org, id, _ = entity.identifier.split('_', 2)

        try:
            ns = NAMESPACES[org]
        except KeyError:
            ns = Namespace(org, config.fqdn + f"/api/v1/organizations/{org}/graphs/")
            NAMESPACES[org] = ns

        return QualifiedName(ns, id)

    document = ProvDocument(namespaces=[NAMESPACES['connectors']])
    prov_bundle = ProvBundle(identifier=QualifiedName(NAMESPACES['connectors'], neo_bundle.identifier),
                             namespaces=[NAMESPACES['meta']])

    for forward_conn in get_forward_connectors(neo_bundle):
        forward_conn_entity = ProvEntity(prov_bundle, get_entity_qualified_name(forward_conn),
                                         attributes=convert_attributes_to_dict(forward_conn))
        prov_bundle.add_record(forward_conn_entity)

        definition = dict(node_class=Entity, direction=INCOMING,
                          relation_type="was_derived_from", model=None)
        traversal = Traversal(forward_conn, Entity.__label__, definition)
        for backward_conn in traversal.all():
            backward_conn_entity = ProvEntity(prov_bundle, get_entity_qualified_name(backward_conn),
                                              attributes=convert_attributes_to_dict(backward_conn))
            prov_bundle.add_record(backward_conn_entity)
            backward_conn_entity.wasDerivedFrom(forward_conn_entity)

    document.add_bundle(prov_bundle)

    return document

