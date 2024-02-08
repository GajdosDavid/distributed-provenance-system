import base64

from .models import Document, Entity, Bundle, Token
from prov2neomodel.neomodel2prov import convert_to_prov
from prov.model import ProvDocument, ProvBundle
from base64 import b64decode, b64encode


def get_provenance(organization_id, graph_id):
    d = Document.nodes.get(identifier=f"{organization_id}_{graph_id}")

    return d.graph


def query_db_for_subgraph(organization_id, graph_id, requested_format):
    d = Document.nodes.get(identifier=f"{organization_id}_{graph_id}_domain", format=requested_format)
    tokens = list(d.belongs_to.all())

    assert len(tokens) == 1, "Only one token expected per document!"
    token = tokens[0]
    t = {
        "data": {
            "originatorId": token.originator_id,
            # TODO -- uncommenct once TP is up and running
            # "authorityId": token.authority_id,
            # "tokenTimestamp": token.token_timestamp,
            # "messageTimestamp": token.message_timestamp,
            # "graphImprint": token.hash
        },
        "signature": token.signature
    }

    return d.graph, t


def store_subgraph_into_db(document_id, format, graph, token):
    d = Document()
    d.identifier = document_id
    d.format = format
    d.graph = graph

    # TODO -- uncomment once TP is up and running
    t = Token()
    t.signature = token['signature']
    # t.hash = token['data']['graphImprint']
    t.originator_id = token['data']['originatorId']
    # t.authority_id = token['data']['authorityId']
    # t.token_timestamp = token['data']['tokenTimestamp']
    # t.message_timestamp = token['data']['messageTimestamp']

    t.save()
    d.save()

    t.belongs_to.connect(d)


def get_b64_encoded_subgraph(organization_id, graph_id, is_domain_specific=True, format='rdf'):
    d = Document.nodes.get(identifier=f"{organization_id}_{graph_id}")
    prov_subgraph = retrieve_subgraph(b64decode(d.graph), is_domain_specific)
    subgraph = prov_subgraph.serialize(format=format).encode('utf-8')

    return b64encode(subgraph).decode('utf-8')


def get_token(organization_id, graph_id):
    t = Entity.nodes.get(identifier=f"{organization_id}_{graph_id}")

    token_data = {
        "originatorId": t.attributes['originatorId'],
        "authorityId": t.attributes['authorityId'],
        "tokenTimestamp": t.attributes['tokenTimestamp'],
        "messageTimestamp": t.attributes['messageTimestamp'],
        "graphImprint": t.attributes['graphImprint']
    }
    return {"data": token_data, "signature": t.attributes['signature']}


def get_b64_encoded_meta_provenance(meta_id, requested_format):
    neo_bundle = Bundle.nodes.get(identifier=meta_id)
    meta_document = convert_to_prov(neo_bundle)

    g = meta_document.serialize(format=requested_format)

    return base64.b64encode(g.encode('utf-8')).decode('utf-8')


def retrieve_subgraph(graph, is_domain_specific=True):
    document = ProvDocument.deserialize(content=graph, format='rdf')
    bundle = None
    for b in document.bundles:
        bundle = b
    records = bundle.records

    new_records = []
    for record in records:
        should_be_added = is_domain_specific
        for (_, value) in record.attributes:
            if str(value) in ("cpm:backwardConnector", "cpm:forwardConnector", "cpm:mainActivity"):
                should_be_added = not is_domain_specific
                break

        if should_be_added:
            new_records.append(record)

    new_bundle = ProvBundle(identifier=bundle.identifier, records=new_records, namespaces=bundle.namespaces)
    new_doc = ProvDocument(namespaces=document.namespaces)
    new_doc.add_bundle(new_bundle)

    return new_doc
