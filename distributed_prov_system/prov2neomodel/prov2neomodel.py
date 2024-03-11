import uuid
from datetime import datetime
from prov.model import ProvDocument, ProvElement, ProvRelation, ProvActivity
from .mappers import prov2neo_mappers
from provenance.models import Bundle, Entity, Document, Activity, Agent
from neomodel.exceptions import DoesNotExist
from neomodel.match import Traversal, OUTGOING


def import_graph(document: ProvDocument, json_data, token, graph_id, is_update=False):
    assert len(document.bundles) == 1, 'Only one bundle expected per document'
    signature = token['signature']
    token = token['data']
    token['signature'] = signature
    organization_id = token['originatorId']

    for bundle in document.bundles:
        identifier = f"{organization_id}_{bundle.identifier.localpart}"

        neo_document = Document()
        neo_document.identifier = identifier
        neo_document.graph = json_data['graph']
        neo_document.signature = json_data['signature']
        neo_document.save()

        main_activity_id = get_main_activity_id(bundle)
        if is_update:
            update_meta_prov(graph_id, identifier, token, main_activity_id)
        else:
            try:
                meta_bundle = Bundle.nodes.get(identifier=main_activity_id)
            except DoesNotExist:
                meta_bundle = Bundle()
                meta_bundle.identifier = main_activity_id
                meta_bundle.save()

            store_into_meta_prov(meta_bundle, identifier, token)


def store_into_meta_prov(meta_bundle, new_entity_id, token):
    gen_entity = Entity()
    gen_entity.identifier = new_entity_id + '_gen'
    gen_entity.attributes = {
        'prov:type': 'prov:bundle'
    }

    first_version = Entity()
    first_version.identifier = new_entity_id
    first_version.attributes = {'prov:type': 'prov:bundle', 'pav:version': 1}

    first_version.save()
    gen_entity.save()

    meta_bundle.contains.connect(gen_entity)
    meta_bundle.contains.connect(first_version)
    first_version.specialization_of.connect(gen_entity)

    store_token(meta_bundle, first_version, token)


def update_meta_prov(graph_id, new_entity_id, token, main_activity_id):
    meta_bundle = Bundle.nodes.get(identifier=main_activity_id)
    latest_entity = Entity.nodes.get(identifier=token['originatorId'] + '_' + graph_id)
    gen_entities = list(latest_entity.specialization_of.all())
    assert len(gen_entities) == 1, "Only one gen entity can be specified for version chain!"
    gen_entity = gen_entities[0]

    latest_version = latest_entity.attributes['pav:version']

    new_version = Entity()
    new_version.identifier = new_entity_id
    new_version.attributes = {'prov:type': 'prov:bundle', 'pav:version': latest_version + 1}

    new_version.save()

    meta_bundle.contains.connect(new_version)
    new_version.specialization_of.connect(gen_entity)
    new_version.was_derived_from.connect(latest_entity, {'attributes': {'prov:type': 'prov:Revision'}})

    store_token(meta_bundle, new_version, token)


def store_token(meta_bundle, entity, token):
    token_attributes = dict()
    for key, value in token.items():
        token_attributes[f"cpm:{key}"] = value
    token_attributes["prov:type"] = "cpm:token"

    e = Entity()
    e.identifier = f"{entity.identifier}_token"
    e.attributes = token_attributes

    agent = get_TP_agent(meta_bundle, token['authorityId'])

    activity = Activity()
    activity.identifier = f"{entity.identifier}_signing"
    activity.start_time = datetime.fromtimestamp(token['tokenTimestamp'])
    activity.end_time = activity.start_time
    activity.attributes = {"prov:type": 'cpm:signing'}

    activity.save()
    e.save()

    meta_bundle.contains.connect(e)
    meta_bundle.contains.connect(activity)
    activity.used.connect(entity)
    activity.was_associated_with.connect(agent)
    e.was_generated_by.connect(activity)
    e.was_attributed_to.connect(agent)


def get_TP_agent(meta_bundle, authority_id):
    definition = dict(node_class=Agent, direction=OUTGOING,
                      relation_type="contains", model=None)
    traversal = Traversal(meta_bundle, Agent.__label__, definition)
    agent = None

    for a in traversal.all():
        if a.identifier == authority_id:
            agent = a
            break

    if agent is None:
        agent = Agent()
        agent.identifier = authority_id
        agent.attributes = {"prov:type": 'cpm:trustedParty'}

        agent.save()
        meta_bundle.contains.connect(agent)

    return agent


def get_main_activity_id(bundle):
    for activity in bundle.get_records(ProvActivity):
        for (_, value) in activity.attributes:
            if str(value) == "cpm:mainActivity":
                return activity.identifier.localpart

    return None


# leaving this here if some time in future it'd be necessary to split document into individual nodes
# def __import_graph__(document: ProvDocument, json_data):
#     assert document.has_bundles(), 'No bundles inside the document!'
#
#     for bundle in document.bundles:
#         models = {}
#
#         neo_bundle = Bundle()
#         neo_bundle.identifier = str(bundle.identifier) + '_v1'
#         neo_bundle.graph = json_data['graph']['data']
#         neo_bundle.signature = json_data['signature']
#         neo_bundle.timestamp = datetime.fromtimestamp(json_data['timestamp'])
#         neo_bundle.save()
#
#         # create_and_import_meta_provenance(str(bundle.identifier), json_data)
#
#         for prov_elem in bundle.get_records(ProvElement):
#             import_element(neo_bundle, prov_elem, models)
#
#         for prov_relation in bundle.get_records(ProvRelation):
#             import_relation(neo_bundle, prov_relation, models)
#
#         # TODO -- do this only within a scope of bundle to avoid doing it for all nodes
#         # query = ("MATCH (node) "
#         #          "WHERE node.attributes IS NOT NULL "
#         #          "SET node += apoc.convert.fromJsonMap(node.attributes) "
#         #          "REMOVE node.attributes")
#         # results, meta = db.cypher_query(query, None, resolve_objects=True)
#
#
# def import_element(bundle, elem, models: dict):
#     mapper_class = prov2neo_mappers.get(type(elem))
#     mapper = mapper_class(bundle, elem)
#     mapper.save()
#
#     model = mapper.get_neomodel()
#     assert model.identifier not in models
#     models[model.identifier] = model
#
#
# def import_relation(bundle, relation, models: dict):
#     mapper_class = prov2neo_mappers.get(type(relation))
#     mapper = mapper_class(bundle, relation, models)
#     mapper.save()
