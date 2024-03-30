from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET
from trusted_party.settings import config
from django.core.exceptions import ObjectDoesNotExist
from . import controller
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
def issue_token(request):
    pass


@csrf_exempt
@require_GET
def verify_signature(request):
    pass


@csrf_exempt
@require_GET
def retrieve_document(request, org_id, doc_id):
    pass


@csrf_exempt
@require_GET
def retrieve_all_tokens(request, org_id):
    pass


@csrf_exempt
@require_GET
def retrieve_token(request, org_id, token_id):
    pass
