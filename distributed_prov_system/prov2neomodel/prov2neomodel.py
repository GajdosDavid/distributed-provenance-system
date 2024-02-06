import uuid
from datetime import datetime
from prov.model import ProvDocument, ProvElement, ProvRelation, ProvActivity
from .mappers import prov2neo_mappers
from provenance.models import Bundle, Entity, Document
from neomodel.exceptions import DoesNotExist


def import_graph(document: ProvDocument, json_data, token, is_update=False):
    assert len(document.bundles) == 1, 'Only one bundle expected per document'
    organization_id = token['data']['originatorId']

    for bundle in document.bundles:
        identifier = f"{organization_id}_{bundle.identifier.localpart}"

        neo_document = Document()
        neo_document.identifier = identifier
        neo_document.graph = json_data['graph']
        neo_document.save()

        main_activity_id = get_main_activity_id(bundle)
        if is_update:
            update_meta_prov(main_activity_id, identifier, json_data)
        else:
            try:
                meta_bundle = Bundle.nodes.get(identifier=f"{organization_id}_{main_activity_id}")
            except DoesNotExist:
                meta_bundle = Bundle()
                meta_bundle.identifier = token['originatorId'] + '_' + main_activity_id
                meta_bundle.save()

            store_into_meta_prov(meta_bundle, identifier, token)


# leaving this here if some time in future it'd be necessary to split document into individual nodes
def __import_graph__(document: ProvDocument, json_data):
    assert document.has_bundles(), 'No bundles inside the document!'

    for bundle in document.bundles:
        models = {}

        neo_bundle = Bundle()
        neo_bundle.identifier = str(bundle.identifier) + '_v1'
        neo_bundle.graph = json_data['graph']['data']
        neo_bundle.signature = json_data['signature']
        neo_bundle.timestamp = datetime.fromtimestamp(json_data['timestamp'])
        neo_bundle.save()

        # create_and_import_meta_provenance(str(bundle.identifier), json_data)

        for prov_elem in bundle.get_records(ProvElement):
            import_element(neo_bundle, prov_elem, models)

        for prov_relation in bundle.get_records(ProvRelation):
            import_relation(neo_bundle, prov_relation, models)

        # TODO -- do this only within a scope of bundle to avoid doing it for all nodes
        # query = ("MATCH (node) "
        #          "WHERE node.attributes IS NOT NULL "
        #          "SET node += apoc.convert.fromJsonMap(node.attributes) "
        #          "REMOVE node.attributes")
        # results, meta = db.cypher_query(query, None, resolve_objects=True)


def store_into_meta_prov(meta_bundle, new_entity_id, token):
    gen_entity = Entity()
    gen_entity.identifier = str(uuid.uuid4()) + '_gen_entity'
    gen_entity.attributes = {
        'prov:type': 'prov:bundle'
    }

    attributes = token
    attributes.update({'prov:type': 'prov:bundle', 'pav:version': 1})
    first_version = Entity()
    first_version.identifier = new_entity_id
    first_version.attributes = attributes

    first_version.save()
    gen_entity.save()

    meta_bundle.contains.connect(gen_entity)
    meta_bundle.contains.connect(first_version)
    first_version.specialization_of.connect(gen_entity)


def update_meta_prov(main_activity_id, new_entity_id, json_data):
    token = json_data['token']['data']
    token['signature'] = json_data['token']['signature']

    meta_identifier = token['originatorId'] + '_' + main_activity_id

    meta_bundle = Bundle.nodes.get(identifier=meta_identifier)
    gen_entity = None
    latest_entity = None
    latest_version = 0

    for entity in meta_bundle.contains.all():
        if str(entity.identifier) == 'gen_entity':
            gen_entity = entity
            continue

        version = entity.attributes['prov:version']
        if latest_version < version:
            latest_version = version
            latest_entity = entity


    token.update({'prov:type': 'prov:bundle', 'prov:version': latest_version + 1})
    new_version = Entity()
    new_version.identifier = new_entity_id
    new_version.attributes = token

    new_version.save()

    meta_bundle.contains.connect(new_version)
    new_version.specialization_of.connect(gen_entity)
    new_version.was_derived_from.connect(latest_entity, {'attributes': {'prov:type': 'prov:Revision'}})


def get_main_activity_id(bundle):
    for activity in bundle.get_records(ProvActivity):
        for (_, value) in activity.attributes:
            if str(value) == "cpm:mainActivity":
                return activity.identifier.localpart

    return None


def import_element(bundle, elem, models: dict):
    mapper_class = prov2neo_mappers.get(type(elem))
    mapper = mapper_class(bundle, elem)
    mapper.save()

    model = mapper.get_neomodel()
    assert model.identifier not in models
    models[model.identifier] = model


def import_relation(bundle, relation, models: dict):
    mapper_class = prov2neo_mappers.get(type(relation))
    mapper = mapper_class(bundle, relation, models)
    mapper.save()
