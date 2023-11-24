from prov.model import ProvDocument, ProvElement, ProvRelation
from .mappers import prov2neo_mappers
from provenance.models import Bundle


def import_graph(document: ProvDocument):
    assert document.has_bundles(), 'No bundles inside the document!'

    for bundle in document.bundles:
        models = {}

        neo_bundle = Bundle()
        neo_bundle.identifier = bundle.identifier
        neo_bundle.save()

        # Generate nodes first
        for prov_elem in bundle.get_records(ProvElement):
            import_element(neo_bundle, prov_elem)

        # Now connect the nodes
        for prov_relation in bundle.get_records(ProvRelation):
            import_relations(bundle, prov_relation, models)

        # TODO -- do this only within a scope of bundle to avoid doing it for all nodes
        # query = ("MATCH (node) "
        #          "WHERE node.attributes IS NOT NULL "
        #          "SET node += apoc.convert.fromJsonMap(node.attributes) "
        #          "REMOVE node.attributes")
        # results, meta = db.cypher_query(query, None, resolve_objects=True)


def import_element(bundle, elem, models: dict):
    mapper_class = prov2neo_mappers.get(type(elem))
    mapper = mapper_class(elem)
    mapper.do_mapping()

    model = mapper.get_neomodel()
    model.save()
    model.bundled_in.connect(bundle)

    assert model.identifier not in models
    models[model.identifier] = model


def import_relations(bundle, relation, models: dict):
    pass