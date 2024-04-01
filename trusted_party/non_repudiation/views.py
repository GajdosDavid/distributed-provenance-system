import datetime

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from trusted_party.settings import config
from django.core.exceptions import ObjectDoesNotExist
from . import controller
from .controller import IsNotSubgraph
from cryptography.exceptions import InvalidSignature
from OpenSSL.crypto import X509StoreContextError
from .models import Organization
import json


@csrf_exempt
@require_GET
def info(request):
    return JsonResponse({
        "id": config.id,
        "certificate": config.cert
    })


@csrf_exempt
@require_GET
def organizations(request):
    org = controller.retrieve_organizations()

    if len(org) == 0:
        return JsonResponse({"info": "No organizations registered yet."})

    return JsonResponse(org, safe=False)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def specific_organization(request, org_id):
    if request.method == "GET":
        try:
            org = controller.retrieve_organization(org_id)
        except ObjectDoesNotExist:
            return JsonResponse({"error": f"Organization with id [{org_id}] does not exist!"}, status=404)

        return JsonResponse(org)
    else:
        return store_cert(request, org_id)


def store_cert(request, org_id):
    json_data = json.loads(request.body)

    expected_json_fields = ('id', 'clientCertificate', 'intermediateCerts')
    for field in expected_json_fields:
        if field not in json_data:
            return JsonResponse({"error": f"Mandatory field [{field}] not present in request!"}, status=400)

    if org_id != json_data['id']:
        return JsonResponse({"error": f"Org ID from URI [{org_id}] does not match the one from request [{json_data['id']}]!"}, status=400)

    try:
        Organization.objects.get(org_name=org_id)

        return JsonResponse({"error": f"Organization with id [{org_id}] is already registered!"}, status=409)
    except ObjectDoesNotExist:
        try:
            controller.verify_chain_of_trust(json_data['clientCertificate'], json_data['intermediateCerts'])
        except X509StoreContextError:
            return JsonResponse({"error": f"Could not verify the chain of trust!"}, status=401)

    controller.store_organization(org_id, json_data['clientCertificate'], json_data['intermediateCerts'])

    return HttpResponse(status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT"])
def certs(request, org_id):
    if request.method == "GET":
        return retrieve_all_certs(request, org_id)
    else:
        return update_certificate(request, org_id)


def retrieve_all_certs(request, org_id):
    try:
        org = controller.retrieve_organization(org_id, True)
    except ObjectDoesNotExist:
        return JsonResponse({"error": f"Organization with id [{org_id}] does not exist!"}, status=404)

    return JsonResponse(org)


def update_certificate(request, org_id):
    json_data = json.loads(request.body)

    expected_json_fields = ('clientCertificate', 'intermediateCerts')
    for field in expected_json_fields:
        if field not in json_data:
            return JsonResponse({"error": f"Mandatory field [{field}] not present in request!"}, status=400)

    try:
        Organization.objects.get(org_name=org_id)
        controller.verify_chain_of_trust(json_data['clientCertificate'], json_data['intermediateCerts'])
    except ObjectDoesNotExist:
        return JsonResponse({"error": f"Organization with id [{org_id}] does not exist!"})
    except X509StoreContextError:
        return JsonResponse({"error": f"Could not verify the chain of trust!"}, status=401)

    controller.update_certificate(org_id, json_data['clientCertificate'], json_data['intermediateCerts'])

    return HttpResponse(status=201)


@csrf_exempt
@require_GET
def retrieve_document(request, org_id, doc_id):
    try:
        doc = controller.retrieve_document(org_id, doc_id)
    except ObjectDoesNotExist:
        return JsonResponse({"error": f"No document wih id [{doc_id}] exists for organization [{org_id}]"}, status=404)

    return JsonResponse({"graph": doc.document_text, "signature": doc.signature})


@csrf_exempt
@require_GET
def retrieve_all_tokens(request, org_id):
    try:
        tokens = controller.retrieve_tokens(org_id)
    except ObjectDoesNotExist:
        return JsonResponse({"error": f"Organization with id [{org_id}] does not exist!"}, status=404)

    if len(tokens) == 0:
        return JsonResponse({"error": f"No tokens have been issued for organization with id [{org_id}]"}, status=404)

    return JsonResponse(tokens, safe=True)


@csrf_exempt
@require_GET
def specific_token(request, org_id, doc_id):
    try:
        Organization.objects.get(org_name=org_id)
    except ObjectDoesNotExist:
        return JsonResponse({"error": f"Organization with id [{org_id}] does not exist!"})

    try:
        token = controller.retrieve_specific_token(org_id, doc_id)
    except ObjectDoesNotExist:
        return JsonResponse({"error": f"No document found with id [{doc_id}] under organization [{org_id}]!"}, status=404)

    return JsonResponse(token, safe=True)


@csrf_exempt
@require_POST
def issue_token(request):
    json_data = json.loads(request.body)
    expected_json_fields = ('organizationId', 'graph', 'signature', 'graphFormat', 'type', 'createdOn')
    for field in expected_json_fields:
        if field not in json_data:
            return JsonResponse({"error": f"Mandatory field [{field}] not present in request!"}, status=400)

    if json_data['type'] not in ('domain_specific', 'backbone', 'meta', 'graph'):
        return JsonResponse({"error": f"Incorrect type [{json_data['type']}, must be one of [subgraph|meta|graph]!"}, status=400)

    if datetime.datetime.fromtimestamp(json_data['createdOn']) >= datetime.datetime.now():
        return JsonResponse({"error": f"Incorrect timestamp for the document!"}, status=400)

    try:
        Organization.objects.get(org_name=json_data['organizationId'])
    except ObjectDoesNotExist:
        return JsonResponse({"error": f"Organization with id [{json_data['organizationId']}] does not exist!"}, status=400)

    try:
        controller.verify_signature(json_data)
        token = controller.issue_token_and_store_doc(json_data)
    except InvalidSignature:
        return JsonResponse({"error": f"Invalid signature to the graph!"}, status=400)
    except (ObjectDoesNotExist, IsNotSubgraph) as e:
        return JsonResponse({"error": str(e)})

    return JsonResponse(token, safe=False)


@csrf_exempt
@require_POST
def verify_signature(request):
    json_data = json.loads(request.body)
    expected_json_fields = ('organizationId', 'graph', 'signature')
    for field in expected_json_fields:
        if field not in json_data:
            return JsonResponse({"error": f"Mandatory field [{field}] not present in request!"}, status=400)

    try:
        Organization.objects.get(org_name=json_data['organizationId'])
    except ObjectDoesNotExist:
        return JsonResponse({"error": f"Organization with id [{json_data['organizationId']}] does not exist!"})

    try:
        controller.verify_signature(json_data)
    except InvalidSignature:
        return JsonResponse({"error": f"Invalid signature to the graph!"}, status=400)

    return HttpResponse(status=200)
