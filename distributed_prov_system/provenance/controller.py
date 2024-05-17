import base64
import json

from .models import Document, Entity, Bundle, Token, Organization, TrustedParty, DefaultTrustedParty
from .neomodel2prov import convert_meta_to_prov, convert_connector_table_to_prov
from prov.model import ProvDocument, ProvBundle
from base64 import b64decode, b64encode
from neomodel.match import Traversal, INCOMING
from neomodel.exceptions import DoesNotExist
from neomodel import db
from distributed_prov_system.settings import config
from .validators import is_org_registered
import requests


def send_token_request_to_TP(payload, tp_url=None):
    if tp_url is None:
        tp_url = config.tp_fqdn

    url = 'http://' + tp_url + '/api/v1/issueToken'
    resp = requests.post(url, json.dumps(payload))

    assert resp.ok, (f'Could not issue token, status code={resp.status_code},'
                     f'content={resp.content}')
    return json.loads(resp.content)


def get_provenance(organization_id, graph_id):
    d = Document.nodes.get(identifier=f"{organization_id}_{graph_id}")

    return d


def query_db_for_subgraph(organization_id, graph_id, requested_format, is_domain_specific):
    suffix = "domain" if is_domain_specific else "backbone"

    d = Document.nodes.get(identifier=f"{organization_id}_{graph_id}_{suffix}", format=requested_format)

    if not config.disable_tp:
        tokens = list(d.belongs_to.all())

        assert len(tokens) == 1, "Only one token expected per document!"
        token = tokens[0]
        t = {
            "data": {
                "originatorId": token.originator_id,
                "authorityId": token.authority_id,
                "tokenTimestamp": token.token_timestamp,
                "documentCreationTimestamp": token.message_timestamp,
                "documentDigest": token.hash,
                "additionalData": token.additional_data
            },
            "signature": token.signature
        }
    else:
        t = None

    return d.graph, t


def store_subgraph_into_db(document_id, format, graph, token):
    d = Document()
    d.identifier = document_id
    d.format = format
    d.graph = graph
    d.save()

    if token is not None:
        store_token_into_db(token, None, d)


def store_token_into_db(token, document_id=None, neo_document=None):
    assert document_id is not None or neo_document is not None

    t = Token()
    t.signature = token['signature']
    t.hash = token['data']['documentDigest']
    t.originator_id = token['data']['originatorId']
    t.authority_id = token['data']['authorityId']
    t.token_timestamp = token['data']['tokenTimestamp']
    t.message_timestamp = token['data']['documentCreationTimestamp']
    t.additional_data = token['data']['additionalData']

    t.save()

    if neo_document is None:
        neo_document = Document.nodes.get(identifier=f"{token['data']['originatorId']}_{document_id}")

    trusted_party = TrustedParty.nodes.get(identifier=token['data']['authorityId'])

    t.belongs_to.connect(neo_document)
    t.was_issued_by.connect(trusted_party)

    return t


def get_b64_encoded_subgraph(organization_id, graph_id, is_domain_specific=True, format='rdf'):
    d = Document.nodes.get(identifier=f"{organization_id}_{graph_id}")
    prov_subgraph = retrieve_subgraph(b64decode(d.graph), d.format, is_domain_specific)
    subgraph = prov_subgraph.serialize(format=format).encode('utf-8')

    return b64encode(subgraph).decode('utf-8')


def get_token(organization_id, graph_id, document):
    registered = is_org_registered(organization_id)
    if registered:
        query = """
                MATCH (org:Organization) WHERE org.identifier=$organization_id 
                MATCH (org)-[:trusts]->(tp:TrustedParty)<-[:was_issued_by]-(token:Token)-[:belongs_to]->(doc:Document) 
                WHERE doc.identifier=$doc_id 
                RETURN token
                """
    else:
        query = """
                MATCH (tp:DefaultTrustedParty)<-[:was_issued_by]-(token:Token)-[:belongs_to]->(doc:Document) 
                WHERE doc.identifier=$doc_id 
                RETURN token
                """

    results, meta = db.cypher_query(query, {"organization_id": organization_id, "doc_id": f"{organization_id}_{graph_id}"},
                                    resolve_objects=True)

    if len(results) > 0:
        t = results[0][0]
    else:
        if registered:
            tp_url = get_TP_url_by_organization(organization_id)
        else:
            tp_url = config.tp_fqdn

        token = send_token_request_to_TP({"graph": document.graph}, tp_url)
        t = store_token_into_db(token, None, document)

    token_data = {
        "originatorId": t.originator_id,
        "authorityId": t.authority_id,
        "tokenTimestamp": t.token_timestamp,
        "documentCreationTimestamp": t.message_timestamp,
        "documentDigest": t.hash,
        "additionalData": t.additional_data
    }
    return {"data": token_data, "signature": t.signature}


def get_b64_encoded_meta_provenance(meta_id, requested_format):
    neo_bundle = Bundle.nodes.get(identifier=meta_id)
    meta_document = convert_meta_to_prov(neo_bundle)

    g = meta_document.serialize(format=requested_format)

    return base64.b64encode(g.encode('utf-8')).decode('utf-8')


def get_b64_encoded_connector_bundle(connector_id, requested_format):
    neo_bundle = Bundle.nodes.get(identifier=connector_id)
    meta_document = convert_connector_table_to_prov(neo_bundle)

    g = meta_document.serialize(format=requested_format)

    return base64.b64encode(g.encode('utf-8')).decode('utf-8')


def retrieve_subgraph(graph, graph_format, is_domain_specific=True):
    document = ProvDocument.deserialize(content=graph, format=graph_format)
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


def store_organization(organization_id, client_cert, intermediate_certs, tp_uri=None):
    org = Organization()
    org.identifier = organization_id
    org.client_cert = client_cert
    org.intermediate_certs = intermediate_certs

    org.save()
    tp = get_TP(tp_uri)

    org.trusts.connect(tp)


def store_connectors(forward_connectors, backward_connectors, source_bundle, source_meta, organization_id):
    for connector in forward_connectors:
        try:
            conn_bundle = Bundle.nodes.get(identifier=connector.identifier.localpart)
        except DoesNotExist:
            conn_bundle = Bundle()
            conn_bundle.identifier = connector.identifier.localpart
            conn_bundle.save()

        try:
            conn_bundle.contains.get(identifier=f"{organization_id}_{source_bundle}_fc")
        except DoesNotExist:
            receiver_bundle_id = None
            for key, value in connector.attributes:
                if key.localpart == "receiverBundleId":
                    receiver_bundle_id = value
                    break

            attrs = {"prov:type": "cpm:forwardConnector"}
            if receiver_bundle_id is not None:
                try:
                    ent = Entity.nodes.get(identifier__contains=f"{receiver_bundle_id.localpart}")

                    attrs["cpm:receiverBundleId"] = str(receiver_bundle_id)
                    definition = dict(node_class=Bundle, direction=INCOMING,
                                      relation_type="contains", model=None)
                    traversal = Traversal(ent, Bundle.__label__, definition)
                    meta = traversal.all()[0]

                    attrs["cpm:metabundle"] = "meta:" + meta.identifier
                except DoesNotExist:
                    pass

            e = Entity()
            e.identifier = f"{organization_id}_{source_bundle}_fc"
            e.attributes = attrs
            e.save()

            conn_bundle.contains.connect(e)

    for (ip, connector) in backward_connectors:
        sender_bundle_id = None
        #sender_meta_id = None
        for key, value in connector.attributes:
            if key.localpart == "senderBundleId":
                sender_bundle_id = value.localpart

           # if key.localpart == "metabundle":
           #     sender_meta_id = value.localpart

        if len(ip) > 0:
            payload = {"senderBundleId": sender_bundle_id,
                       "organizationId": organization_id,
                       "senderMetaId": source_meta,
                       "sourceBundle": source_bundle}
            send_store_connector_request_to_remote(ip, payload, connector.identifier.localpart)
            continue

        store_backward_connector(connector.identifier.localpart, sender_bundle_id,
                                 organization_id, source_bundle, source_meta)


def send_store_connector_request_to_remote(ip, payload, connector_id):
    url = 'http://' + ip + '/api/v1/connectors/' + connector_id
    resp = requests.post(url, json.dumps(payload))

    if not resp.ok:
        print(f"Couldn't store backward connector at url {url}. Response: {resp.content}")


def modify_organization(organization_id, client_cert, intermediate_certs, tp_uri=None):
    org = Organization.nodes.get(identifier=organization_id)
    org.identifier = organization_id
    org.client_cert = client_cert
    org.intermediate_certs = intermediate_certs

    org.save()
    tp = get_TP(tp_uri)

    org.trusts.connect(tp)


def get_TP(url):
    if url is None:
        default_tp = list(DefaultTrustedParty.nodes.all())
        assert len(default_tp) == 1

        tp = TrustedParty.nodes.get(identifier=default_tp[0].identifier)

        return tp

    resp = requests.get(f'http://{url}/api/v1/info')

    assert resp.ok, "Couldn't retrieve info from TP!"
    info = json.loads(resp.content)

    try:
        tp = TrustedParty.nodes.get(identifier=info['id'])
    except DoesNotExist:
        tp = TrustedParty()
        tp.identifier = info['id']
        tp.url = url
        tp.certificate = info['certificate']
        tp.save()

    return tp


def get_TP_url_by_organization(organization_id):
    try:
        org = Organization.nodes.get(identifier=organization_id)

        trusted_parties = list(org.trusts.all())
        return trusted_parties[0].url
    except DoesNotExist:
        return None


def store_backward_connector(connector_bundle_id, sender_bundle_id, org_id, source_bundle, source_meta):
    conn_bundle = Bundle.nodes.get(identifier=connector_bundle_id)

    assert sender_bundle_id is not None

    ent = Entity.nodes.get(identifier__contains=f"_{sender_bundle_id}_gen")
    definition = dict(node_class=Bundle, direction=INCOMING,
                      relation_type="contains", model=None)
    traversal = Traversal(ent, Bundle.__label__, definition)
    meta = traversal.all()[0]

    print(source_meta)
    sender_bundle_org = ent.identifier.split('_')
    attrs = {"prov:type": "cpm:backwardConnector",
             "cpm:senderBundleId": f"{sender_bundle_org[0]}:{sender_bundle_id}",
             "cpm:metabundle": "meta:" + meta.identifier}

    e = Entity()
    e.identifier = f"{org_id}_{source_bundle}_bc"
    e.attributes = attrs
    e.save()

    conn_bundle.contains.connect(e)

    forward_conn = conn_bundle.contains.get(identifier__contains=f"_{sender_bundle_id}_fc")
    attrs = forward_conn.attributes
    attrs["cpm:receiverBundleId"] = f"{org_id}:{source_bundle}"
    attrs["cpm:metabundle"] = "meta:" + source_meta
    forward_conn.attributes = attrs
    forward_conn.save()
