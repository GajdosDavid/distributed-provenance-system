from .models import Document, Entity, Bundle
from prov2neomodel.neomodel2prov import convert_to_prov


def get_provenance(organization_id, graph_id):
    d = Document.nodes.get(identifier=f"{organization_id}_{graph_id}")

    return d.graph


def get_token(organization_id, graph_id):
    t = Entity.nodes.get(identifier=f"{organization_id}_{graph_id}")

    return {"data": t.attributes['data'], "signature": t.attributes['signature']}


def get_meta_provenance(organization_id, meta_id):
    neo_bundle = Bundle.nodes.get(identifier=f"{organization_id}_{meta_id}")
    meta_document = convert_to_prov(neo_bundle)

    return meta_document
