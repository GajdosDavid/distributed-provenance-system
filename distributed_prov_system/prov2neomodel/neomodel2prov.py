from prov.model import ProvDocument, ProvBundle, QualifiedName, Namespace, ProvEntity
from distributed_prov_system.settings import config
from neomodel.match import Traversal, INCOMING
from provenance.models import Entity

NAMESPACES = {
    "prov": Namespace("prov", "http://www.w3.org/ns/prov#"),
    "meta": Namespace("meta", config.fqdn + f"/graphs/meta/"),
    "pav": Namespace("pav", "http://purl.org/pav/"),
}


def convert_to_prov(neo_bundle):
    def create_prov_entity(neo_entity):
        org, id = neo_entity.identifier.split('_', 1)

        try:
            entity_ns = entity_namespaces[org]
        except KeyError:
            entity_ns = Namespace(org, config.fqdn + f"/organizations/{org}/graphs/")
            entity_namespaces[org] = entity_ns

        attributes = dict()
        for key, value in neo_entity.attributes.items():
            ns, localpart = key.split(':')

            attributes.update({QualifiedName(NAMESPACES[ns], localpart): value})

        return ProvEntity(prov_bundle, QualifiedName(entity_ns, id), attributes=attributes)

    def get_sorted_specialized_entities_from_gen(g_entity):
        definition = dict(node_class=Entity, direction=INCOMING,
                          relation_type="specialization_of", model=None)
        traversal = Traversal(g_entity, Entity.__label__, definition)
        entities = list(traversal.all())
        entities.sort(key=lambda e: e.attributes['pav:version'])

        return entities

    identifier = neo_bundle.identifier
    document = ProvDocument(namespaces=[NAMESPACES["meta"]])

    prov_bundle = ProvBundle(identifier=QualifiedName(NAMESPACES["meta"], identifier))
    entity_namespaces = dict()

    gen_entities = []
    # Retrieve gen entities first as I'll be able to create individual chains
    # by using the specialization_of relationship
    for entity in neo_bundle.contains.all():
        if entity.identifier[-4:] == "_gen":
            gen_entities.append(entity)

    for gen_entity in gen_entities:
        gen = create_prov_entity(gen_entity)

        specialized_entities = get_sorted_specialized_entities_from_gen(gen_entity)
        prov_specialized_entities = [create_prov_entity(e) for e in specialized_entities]
        for i, entity in enumerate(prov_specialized_entities):
            entity.specializationOf(gen)
            if i > 0:
                attribute = {QualifiedName(NAMESPACES['prov'], "type"): "prov:Revision"}
                entity.wasDerivedFrom(prov_specialized_entities[i-1], attributes=attribute)

            prov_bundle.add_record(entity)

        prov_bundle.add_record(gen)

    document.add_bundle(prov_bundle)

    return document
