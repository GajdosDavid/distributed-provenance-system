from prov.model import ProvDocument, ProvBundle, QualifiedName, Namespace, ProvEntity
from distributed_prov_system.settings import config


def convert_to_prov(neo_bundle):
    document = ProvDocument()

    identifier = neo_bundle.identifier.split('_')
    org_part = identifier[0]
    id_part = identifier[1]
    ns_bundle = Namespace("meta", config.fqdn + f"organizations/{org_part}/meta/")
    ns_entity = Namespace("graphs", config.fqdn + f"organizations/{org_part}/graphs/")

    prov_bundle = ProvBundle(identifier=QualifiedName(ns_bundle, id_part))

    for entity in neo_bundle.contains.all():
        e_id = entity.identifier.split('_')[1]
        e = ProvEntity(prov_bundle, QualifiedName(ns_entity, e_id))
        prov_bundle.add_record(e)

    document.add_bundle(prov_bundle)

    return document
