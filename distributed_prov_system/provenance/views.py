from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET
from django.core.exceptions import BadRequest

from prov2neomodel.prov2neomodel import import_graph
import cryptography.exceptions
import json

from .validators import GraphInputValidator, InvalidGraph, IncorrectHash


def confirm_store_to_trusted_party():
    pass

@csrf_exempt
@require_http_methods(["GET", "POST"])
def graph(request, organization_id, graph_id):
    if request.method == 'POST':
        return graphs_post(request)
    else:
        return graphs_get(request)


def graphs_post(request):
    json_data = json.loads(request.body)

    try:
        validator = GraphInputValidator(json_data)
        validator.verify_token()
        validator.validate_graph()
    except cryptography.exceptions.InvalidSignature:
        raise BadRequest("Invalid signature")
    except InvalidGraph:
        raise BadRequest("Incorrect graph")
    except IncorrectHash:
        raise BadRequest("Incorrect hash")

    graph = validator.get_graph()
    import_graph(graph, json_data)

    confirm_store_to_trusted_party()

    return HttpResponse("Alles gut")


def graphs_get(request):
    pass


@csrf_exempt
@require_GET
def graph_meta(request, organization_id, graph_id):
    pass


@csrf_exempt
@require_GET
def graph_domain_specific(request, organization_id, graph_id):
    pass


@csrf_exempt
@require_GET
def graph_backbone(request, organization_id, graph_id):
    pass