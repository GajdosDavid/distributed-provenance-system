from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET
from trusted_party.settings import config
from django.core.exceptions import ObjectDoesNotExist
from . import controller
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
    return JsonResponse(controller.retrieve_organizations(), safe=False)


@csrf_exempt
@require_GET
def retrieve_organization(request, org_id):
    try:
        org = controller.retrieve_organization(org_id)
    except ObjectDoesNotExist:
        return JsonResponse({"error": f"Organization with id [{org_id}] does not exist!"}, status=404)

    return JsonResponse(org)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def certs(request, org_id):
    if request.method == "GET":
        return retrieve_all_certs(request, org_id)
    else:
        return store_cert_for_verification(request, org_id)


def retrieve_all_certs(request, org_id):
    try:
        org = controller.retrieve_organization(org_id, True)
    except ObjectDoesNotExist:
        return JsonResponse({"error": f"Organization with id [{org_id}] does not exist!"}, status=404)

    return JsonResponse(org)


def store_cert_for_verification(request, org_id):
    pass


@csrf_exempt
@require_http_methods(["GET", "DELETE"])
def specific_cert(request, org_id, cert_id):
    return JsonResponse({"hello": "world"})


@csrf_exempt
@require_GET
def generate_token(request):
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
