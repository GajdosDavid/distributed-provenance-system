from datetime import datetime
from prov.model import ProvDocument
from .models import Bundle, Entity, Document, Activity, Agent
from neomodel.exceptions import DoesNotExist
from neomodel.match import Traversal, OUTGOING


def import_graph(document: ProvDocument, json_data, token, graph_id, meta_id, is_update=False):
    assert len(document.bundles) == 1, 'Only one bundle expected per document'
    signature = token['signature']
    token = token['data']
    token['signature'] = signature
    organization_id = token['originatorId']

    for bundle in document.bundles:
        identifier = f"{organization_id}_{bundle.identifier.localpart}"

        neo_document = Document()
        neo_document.identifier = identifier
        neo_document.graph = json_data['document']
        neo_document.format = json_data['documentFormat']
        neo_document.save()

        if is_update:
            update_meta_prov(graph_id, identifier, token, meta_id)
        else:
            try:
                meta_bundle = Bundle.nodes.get(identifier=meta_id)
            except DoesNotExist:
                meta_bundle = Bundle()
                meta_bundle.identifier = meta_id
                meta_bundle.save()

            store_into_meta_prov(meta_bundle, identifier, token)


def store_into_meta_prov(meta_bundle, new_entity_id, token):
    gen_entity = Entity()
    gen_entity.identifier = new_entity_id + '_gen'
    gen_entity.attributes = {
        'prov:type': 'prov:bundle'
    }

    first_version = Entity()
    first_version.identifier = new_entity_id
    first_version.attributes = {'prov:type': 'prov:bundle', 'pav:version': 1}

    first_version.save()
    gen_entity.save()

    meta_bundle.contains.connect(gen_entity)
    meta_bundle.contains.connect(first_version)
    first_version.specialization_of.connect(gen_entity)

    store_token_into_meta(meta_bundle, first_version, token)


def update_meta_prov(graph_id, new_entity_id, token, meta_id):
    meta_bundle = Bundle.nodes.get(identifier=meta_id)
    latest_entity = Entity.nodes.get(identifier=token['originatorId'] + '_' + graph_id)
    gen_entities = list(latest_entity.specialization_of.all())
    assert len(gen_entities) == 1, "Only one gen entity can be specified for version chain!"
    gen_entity = gen_entities[0]

    latest_version = latest_entity.attributes['pav:version']

    new_version = Entity()
    new_version.identifier = new_entity_id
    new_version.attributes = {'prov:type': 'prov:bundle', 'pav:version': latest_version + 1}

    new_version.save()

    meta_bundle.contains.connect(new_version)
    new_version.specialization_of.connect(gen_entity)
    new_version.was_derived_from.connect(latest_entity, {'attributes': {'prov:type': 'prov:Revision'}})

    store_token_into_meta(meta_bundle, new_version, token)


def store_token_into_meta(meta_bundle, entity, token):
    token_attributes = dict()
    for key, value in token.items():
        if key == "additionalData":
            for k, v in value.items():
                token_attributes[f"cpm:{k}"] = v
            continue

        token_attributes[f"cpm:{key}"] = value
    token_attributes["prov:type"] = "cpm:token"

    e = Entity()
    e.identifier = f"{entity.identifier}_token"
    e.attributes = token_attributes

    agent = get_TP_agent(meta_bundle, token)

    activity = Activity()
    activity.identifier = f"{entity.identifier}_tokenGeneration"
    activity.start_time = datetime.fromtimestamp(token['tokenTimestamp'])
    activity.end_time = activity.start_time
    activity.attributes = {"prov:type": 'cpm:tokenGeneration'}

    activity.save()
    e.save()

    meta_bundle.contains.connect(e)
    meta_bundle.contains.connect(activity)
    activity.used.connect(entity)
    activity.was_associated_with.connect(agent)
    e.was_generated_by.connect(activity)
    e.was_attributed_to.connect(agent)


def get_TP_agent(meta_bundle, token):
    authority_id = token['authorityId']
    definition = dict(node_class=Agent, direction=OUTGOING,
                      relation_type="contains", model=None)
    traversal = Traversal(meta_bundle, Agent.__label__, definition)
    agent = None

    for a in traversal.all():
        if a.identifier == authority_id:
            agent = a
            break

    if agent is None:
        agent = Agent()
        agent.identifier = authority_id
        attrs = {"prov:type": 'cpm:trustedParty',
                            "cpm:trustedPartyUri": token['additionalData']['trustedPartyUri']}
        if 'trustedPartyCertificate' in token['additionalData']:
            attrs.update({"cpm:trustedPartyCertificate": token['additionalData']['trustedPartyCertificate']})

        agent.attributes = attrs
        agent.save()
        meta_bundle.contains.connect(agent)

    return agent
