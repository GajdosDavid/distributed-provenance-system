from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET
from django.core.exceptions import BadRequest
from neomodel.exceptions import DoesNotExist

from prov2neomodel.prov2neomodel import import_graph
import cryptography.exceptions
import json

from .validators import GraphInputValidator, InvalidGraph, IncorrectHash
import provenance.controller as controller


def confirm_store_to_trusted_party():
    pass


@csrf_exempt
@require_http_methods(["GET", "POST"])
def graph(request, organization_id, graph_id):
    if request.method == 'POST':
        return graphs_post(request, organization_id, graph_id)
    else:
        return graphs_get(request, organization_id, graph_id)


def graphs_post(request, organization_id, graph_id):
    json_data = json.loads(request.body)

    try:
        validator = GraphInputValidator(json_data)
        validator.verify_token()
        validator.validate_token(organization_id)
        validator.validate_graph(graph_id)
    except cryptography.exceptions.InvalidSignature:
        raise BadRequest("Invalid signature")
    except InvalidGraph:
        raise BadRequest("Incorrect graph")
    except IncorrectHash:
        raise BadRequest("Incorrect hash")

    document = validator.get_document()
    import_graph(document, json_data)

    confirm_store_to_trusted_party()

    return HttpResponse("Alles gut")


def graphs_get(request, organization_id, graph_id):
    try:
        g = controller.get_provenance(organization_id, graph_id)
        t = controller.get_token(organization_id, graph_id)
    except DoesNotExist:
        return JsonResponse({"error": "Not good"}, status=404)

    return JsonResponse({"graph": g, "token": t})


@csrf_exempt
@require_GET
def graph_meta(request, organization_id, meta_id):
    try:
        meta = controller.get_meta_provenance(organization_id, meta_id)
    except DoesNotExist:
        return JsonResponse({"error": "Not good"}, status=404)

    # TODO -- obtain token from trusted party
    t = ""
    g = meta.serialize(format=request.GET.get('format', 'rdf'))

    return JsonResponse({"meta-prov": g, "token": t})


@csrf_exempt
@require_GET
def graph_domain_specific(request, organization_id, graph_id):
    pass


@csrf_exempt
@require_GET
def graph_backbone(request, organization_id, graph_id):
    pass