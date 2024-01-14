from datetime import datetime
from prov.model import ProvDocument, ProvElement, ProvRelation
from .mappers import prov2neo_mappers
from provenance.models import Bundle, Entity


def import_graph(document: ProvDocument, json_data):
    assert document.has_bundles(), 'No bundles inside the document!'

    for bundle in document.bundles:
        models = {}

        neo_bundle = Bundle()
        neo_bundle.identifier = str(bundle.identifier) + '_v1'
        neo_bundle.graph = json_data['graph']['data']
        neo_bundle.signature = json_data['signature']
        neo_bundle.timestamp = datetime.fromtimestamp(json_data['timestamp'])
        neo_bundle.save()

        create_and_import_meta_provenance(str(bundle.identifier), json_data)

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


def create_and_import_meta_provenance(bundle_id, json_data):
    user_cert = json_data['certificates']['user_cert']
    intermediate_certs = json_data['certificates']['intermediate_certs']
    signature = json_data['signature']

    meta_bundle = Bundle()
    meta_bundle.identifier = bundle_id + '_meta'

    gen_entity = Entity()
    gen_entity.identifier = bundle_id + '_gen'
    gen_entity.attributes = {
        'prov:type': 'prov:bundle'
    }

    first_version = Entity()
    first_version.identifier = bundle_id + '_v1'
    first_version.attributes = {
        'prov:type': 'prov:bundle',
        'signature': signature,
        'user_certificate': user_cert,
        'intermediate_certificates': intermediate_certs
    }

    first_version.save()
    gen_entity.save()
    meta_bundle.save()

    gen_entity.bundled_in.connect(meta_bundle)
    first_version.bundled_in.connect(meta_bundle)
    first_version.specialization_of.connect(gen_entity)


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
