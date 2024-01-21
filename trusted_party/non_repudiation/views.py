from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET

@csrf_exempt
@require_GET
def organizations(request):
    retrieve_organizations(request)

    return JsonResponse({"hello": "world"})


def retrieve_organizations(request):
    pass


@csrf_exempt
@require_http_methods(["GET", "POST"])
def certs(request, org_id):
    if request.method == "GET":
        retrieve_all_certs(request, org_id)
    else:
        store_cert_for_verification(request, org_id)


def retrieve_all_certs(request, org_id):
    pass


def store_cert_for_verification(request, org_id):
    pass

@csrf_exempt
@require_http_methods(["GET", "DELETE"])
def specific_cert(request, org_id, cert_id):
    return JsonResponse({"hello": "world"})


@csrf_exempt
@require_GET
def own_certs(request):
    pass


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
