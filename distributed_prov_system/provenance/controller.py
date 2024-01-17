from .models import Document, Entity, Bundle
from prov2neomodel.neomodel2prov import convert_to_prov
from prov.model import ProvDocument, ProvBundle
from base64 import b64decode, b64encode


def get_provenance(organization_id, graph_id):
    d = Document.nodes.get(identifier=f"{organization_id}_{graph_id}")

    return d.graph


def get_subgraph(organization_id, graph_id, is_domain_specific=True, format='rdf'):
    d = Document.nodes.get(identifier=f"{organization_id}_{graph_id}")
    prov_subgraph = retrieve_subgraph(b64decode(d.graph), is_domain_specific)
    subgraph = prov_subgraph.serialize(format=format).encode('utf-8')

    return b64encode(subgraph).decode('utf-8')


def get_token(organization_id, graph_id):
    t = Entity.nodes.get(identifier=f"{organization_id}_{graph_id}")

    token = {
        "originatorId": t.attributes['originatorId'],
        "authorityId": t.attributes['authorityId'],
        "tokenTimestamp": t.attributes['tokenTimestamp'],
        "messageTimestamp": t.attributes['messageTimestamp'],
        "graphImprint": t.attributes['graphImprint']
    }
    return {"data": token, "signature": t.attributes['signature']}


def get_meta_provenance(organization_id, meta_id):
    neo_bundle = Bundle.nodes.get(identifier=f"{organization_id}_{meta_id}")
    meta_document = convert_to_prov(neo_bundle)

    return meta_document


def retrieve_subgraph(graph, is_domain_specific=True):
    document = ProvDocument.deserialize(content=graph, format='rdf')
    bundle = None
    for b in document.bundles:
        bundle = b
    records = bundle.records

    records_new = []
    for record in records:
        should_be_added = is_domain_specific
        for (_, value) in record.attributes:
            if str(value) in ("cpm:backwardConnector", "cpm:forwardConnector", "cpm:mainActivity"):
                should_be_added = not is_domain_specific
                break

        if should_be_added:
            records_new.append(record)

    new_bundle = ProvBundle(identifier=bundle.identifier, records=records_new, namespaces=bundle.namespaces)
    new_doc = ProvDocument(namespaces=document.namespaces)
    new_doc.add_bundle(new_bundle)

    return new_doc
