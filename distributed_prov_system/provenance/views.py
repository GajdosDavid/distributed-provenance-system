from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET
from neomodel.exceptions import DoesNotExist

from prov2neomodel.prov2neomodel import import_graph
import json

from .validators import (InputGraphChecker, send_signature_verification_request, graph_already_exists,
                         IncorrectPIDs, HasNoBundles, TooManyBundles, DocumentError)
import provenance.controller as controller


def send_token_request_to_TP():
    return {"data": {"originatorId": "jaJsemBuh"}, "signature": "abcdefghjk"}


@csrf_exempt
@require_http_methods(["GET", "POST", "PUT"])
def graph(request, organization_id, graph_id):
    if request.method == 'POST':
        return graphs_post(request, organization_id, graph_id)
    elif request.method == "PUT":
        # TODO -- check that graph_id exists and is from the same meta-prov
        return graphs_post(request, organization_id, graph_id, is_update=True)
    else:
        return graphs_get(request, organization_id, graph_id)


def graphs_post(request, organization_id, graph_id, is_update=False):
    json_data = json.loads(request.body)

    expected_json_fields = ('graph', 'signature')
    for field in expected_json_fields:
        if field not in json_data:
            return JsonResponse({"error": f"Mandatory field '{field}' not present in request!"}, status=400)

    validator = InputGraphChecker(json_data['graph'])
    validator.parse_graph()
    try:
        validator.check_ids_match(graph_id)
    except DocumentError as e:
        return JsonResponse({"error": str(e)}, status=400)

    if graph_already_exists(organization_id, graph_id):
        return JsonResponse({"error": f"Graph with id '{graph_id}' already "
                                      f"exists under organization '{organization_id}'."}, status=409)

    # TODO -- uncomment once Trusted party is implemented and running
    # resp = send_signature_verification_request(json_data)
    # if resp.status_code != 200:
    #     return JsonResponse({"error": "Unverifiable signature."
    #                                   " Make sure to register your certificate with trusted party first."}, status=401)

    try:
        validator.validate_graph(graph_id)
    except (IncorrectPIDs, HasNoBundles, TooManyBundles, DocumentError) as e:
        error_msg = str(e)
        return JsonResponse({"error": error_msg}, status=400)

    # TODO -- generate non-repudiation token
    token = send_token_request_to_TP()

    document = validator.get_document()
    import_graph(document, json_data, token.copy(), is_update)

    return JsonResponse({"token": token}, status=200)


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
    try:
        g = controller.get_subgraph(organization_id, graph_id, format=request.GET.get('format', 'rdf'))
    except DoesNotExist:
        return JsonResponse({"error": "Not good"}, status=404)

    # TODO -- obtain token from trusted party
    t = ""
    return JsonResponse({"graph": g, "token": t})


@csrf_exempt
@require_GET
def graph_backbone(request, organization_id, graph_id):
    try:
        g = controller.get_subgraph(organization_id, graph_id, is_domain_specific=False, format=request.GET.get('format', 'rdf'))
    except DoesNotExist:
        return JsonResponse({"error": "Not good"}, status=404)

    # TODO -- obtain token from trusted party
    t = ""
    return JsonResponse({"graph": g, "token": t})
