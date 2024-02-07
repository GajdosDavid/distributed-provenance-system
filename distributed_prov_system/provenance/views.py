from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET
from neomodel.exceptions import DoesNotExist

from prov2neomodel.prov2neomodel import import_graph
import json
import copy

from .validators import (InputGraphChecker, send_signature_verification_request, graph_exists, check_graph_id_belongs_to_meta,
                         IncorrectPIDs, HasNoBundles, TooManyBundles, DocumentError)
import provenance.controller as controller
from distributed_prov_system.settings import config
import requests


def send_token_request_to_TP(payload):
    url = 'http://' + config.tp_fqdn + '/issueToken'

    resp = requests.post(url, payload)

    assert resp.ok, f'Could not issue token, status code={resp.status_code}'
    return json.loads(resp.content)


def get_dummy_token():
    return {"data": {"originatorId": "jaJsemBuh"}, "signature": "abcdefu"}


@csrf_exempt
@require_http_methods(["GET", "POST", "PUT"])
def graph(request, organization_id, graph_id):
    if request.method == 'POST':
        return store_graph(request, organization_id, graph_id)
    elif request.method == "PUT":
        return store_graph(request, organization_id, graph_id, is_update=True)
    else:
        return graphs_get(request, organization_id, graph_id)


def store_graph(request, organization_id, graph_id, is_update=False):
    json_data = json.loads(request.body)

    expected_json_fields = ('graph', 'signature')
    for field in expected_json_fields:
        if field not in json_data:
            return JsonResponse({"error": f"Mandatory field '{field}' not present in request!"}, status=400)

    validator = InputGraphChecker(json_data['graph'])
    validator.parse_graph()
    try:
        if is_update:
            check_graph_id_belongs_to_meta(validator.get_main_activity_id(), graph_id, organization_id)
            if not graph_exists(organization_id, graph_id):
                return JsonResponse({"error": f"Graph with id={graph_id} does not exist. Please check whether the ID"
                                              f" you have given is correct."}, status=404)
        else:
            validator.check_ids_match(graph_id)
    except DoesNotExist:
        return JsonResponse({"error": f"The graph with id [{graph_id}] does not "
                                      f"exist under organization [{organization_id}]"}, status=400)
    except DocumentError as e:
        return JsonResponse({"error": str(e)}, status=400)

    if graph_exists(organization_id, validator.get_bundle_id()):
        return JsonResponse({"error": f"Graph with id '{graph_id}' already "
                                      f"exists under organization '{organization_id}'."}, status=409)

    # TODO -- uncomment once Trusted party is implemented and running
    # resp = send_signature_verification_request(json_data.copy(), organization_id)
    # if not resp.ok:
    #     return JsonResponse({"error": "Unverifiable signature."
    #                                   " Make sure to register your certificate with trusted party first."}, status=401)

    try:
        validator.validate_graph(graph_id)
    except (IncorrectPIDs, HasNoBundles, TooManyBundles, DocumentError) as e:
        error_msg = str(e)
        return JsonResponse({"error": error_msg}, status=400)

    # TODO -- uncomment once TP is implemented and running
    # token = send_token_request_to_TP(json_data)
    token = get_dummy_token()

    document = validator.get_document()
    import_graph(document, json_data, copy.deepcopy(token), graph_id, is_update)

    return JsonResponse({"token": token}, status=200)


def graphs_get(request, organization_id, graph_id):
    try:
        g = controller.get_provenance(organization_id, graph_id)
        t = controller.get_token(organization_id, graph_id)
    except DoesNotExist:
        return JsonResponse({"error": f"Could not retrieve a resource with id [{graph_id}] "
                                      f"under organization [{organization_id}]"}, status=404)

    return JsonResponse({"graph": g, "token": t})


@csrf_exempt
@require_GET
def graph_meta(request, meta_id):
    requested_format = request.GET.get('format', 'rdf').lower()

    if requested_format not in ('rdf', 'json', 'xml', 'provn'):
        return JsonResponse({"error": f"Requested format [{requested_format}] is not supported!"}, status=400)

    try:
        g = controller.get_b64_encoded_meta_provenance(meta_id, requested_format)
    except DoesNotExist:
        return JsonResponse({"error": f"The meta-provenance with id [{meta_id}] does not exist"}, status=404)

    # TODO -- uncomment once TP is up and running
    # t = send_token_request_to_TP({"graph": g})
    t = get_dummy_token()

    return JsonResponse({"graph": g, "token": t})


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
