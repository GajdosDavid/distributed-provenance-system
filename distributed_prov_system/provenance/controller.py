from .models import Document, Entity


def get_provenance(organization_id, graph_id):
    d = Document.nodes.get(identifier=f"{organization_id}_{graph_id}")

    return d.graph


def get_token(organization_id, graph_id):
    t = Entity.nodes.get(identifier=f"{organization_id}_{graph_id}")

    return {"data": t.attributes['data'], "signature": t.attributes['signature']}
