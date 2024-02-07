from prov.model import ProvDocument, ProvBundle, QualifiedName, Namespace, ProvEntity
from distributed_prov_system.settings import config


def convert_to_prov(neo_bundle):
    identifier = neo_bundle.identifier
    bundle_ns = Namespace("meta", config.fqdn + f"/graphs/meta/")

    document = ProvDocument(namespaces=[bundle_ns])

    prov_bundle = ProvBundle(identifier=QualifiedName(bundle_ns, identifier))
    entity_namespaces = dict()

    for entity in neo_bundle.contains.all():
        e_id_split = entity.identifier.split('_', 1)
        e_id = e_id_split[1]
        e_org = e_id_split[0]

        try:
            entity_ns = entity_namespaces[e_org]
        except KeyError:
            entity_ns = Namespace(e_org, config.fqdn + f"/organizations/{e_org}/graphs/")
            entity_namespaces[e_org] = entity_ns

        e = ProvEntity(prov_bundle, QualifiedName(entity_ns, e_id))
        prov_bundle.add_record(e)

    document.add_bundle(prov_bundle)

    return document
