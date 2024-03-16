import copy
import json
import requests

import provenance.controller as controller
from distributed_prov_system.settings import config
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET
from neomodel.exceptions import DoesNotExist
from prov2neomodel.prov2neomodel import import_graph

from .validators import (InputGraphChecker, graph_exists, check_graph_id_belongs_to_meta,
                         IncorrectPIDs, HasNoBundles, TooManyBundles, DocumentError, is_org_registered,
                         InvalidTrustedParty, UncheckedTrustedParty, OrganizationNotRegistered,
                         check_organization_is_registered)


def send_register_request_to_TP(payload, organization_id, is_post=True):
    tp_url = payload['TrustedPartyUri'] if 'TrustedPartyUri' in payload else config.tp_fqdn
    url = 'http://' + tp_url + '/register'
    payload['organizationId'] = organization_id

    if is_post:
        resp = requests.post(url, payload)
    else:
        resp = requests.put(url, payload)

    assert resp.ok, f'Could not register/modify organization with id [{organization_id}], status code={resp.status_code}'


def get_dummy_token():
    return {"data": {
                "originatorId": "MUNI",
                "authorityId": "iAmAuthority",
                "tokenTimestamp": 123,
                "messageTimestamp": 123,
                "graphImprint": "17fd7484d7cac628cfa43c348fe05a009a81d18c8a778e6488b707954addf2a3"
            },
            "signature": "bdysXEy2/sOSTN+Lh+v3x7cTdocMcndwuW5OT2wHpQOU/LM4os9Bow0sn4HTln9hRqFdCMukV6Cr6Nn8XvD96jlgEw9KqJj9I+cfBL81x9iqUJX/Wder3lkuIZXYUSeGsOOqUPdlqJAhapgr0V+vibAvPGoiRKqulNi/Xn0jn21lln1HEbHPsnOtM5Ca5wwXuTITJsiXCj+04y9V/XM9Uy9Ib4LLA1VYLCdifjg0ZuxJBcpS/HszlwW9B29rrkUGUsSrV9YU0ViYkeIMcS2bMXsur3EHi3/zSZ5IepUNOBDTu3BDUr33dbrgMOVraI8RU5DTZKmUOx8hzgtApZNotg=="
    }


@csrf_exempt
@require_http_methods(["POST", "PUT"])
def register(request, organization_id):
    if request.method == 'POST':
        return register_org(request, organization_id)
    else:
        return modify_org(request, organization_id)


def register_org(request, organization_id):
    if is_org_registered(organization_id):
        return JsonResponse({"error": f"Organization with id [{organization_id}] is already registered. "
                                      f"If you want to modify it, send PUT request!"}, status=404)

    json_data = json.loads(request.body)
    expected_json_fields = ('clientCertificate', 'intermediateCertificates')
    for field in expected_json_fields:
        if field not in json_data:
            return JsonResponse({"error": f"Mandatory field '{field}' not present in request!"}, status=400)

    controller.store_organization(organization_id,
                                  json_data['clientCertificate'],
                                  json_data['intermediateCertificates'],
                                  json_data['TrustedPartyUri'] if 'TrustedPartyUri' in json_data else None)

    send_register_request_to_TP(json_data, organization_id)

    return HttpResponse(status=201)


def modify_org(request, organization_id):
    if not is_org_registered(organization_id):
        return JsonResponse({"error": f"Organization with id [{organization_id}] is not registered!"}, status=404)

    json_data = json.loads(request.body)
    expected_json_fields = ('clientCertificate', 'intermediateCertificates')
    for field in expected_json_fields:
        if field not in json_data:
            return JsonResponse({"error": f"Mandatory field '{field}' not present in request!"}, status=400)

    controller.modify_organization(organization_id,
                                   json_data['clientCertificate'],
                                   json_data['intermediateCertificates'],
                                   json_data['TrustedPartyUri'] if 'TrustedPartyUri' in json_data else None)

    send_register_request_to_TP(json_data, organization_id, is_post=False)

    return HttpResponse(status=201)


@csrf_exempt
@require_http_methods(["GET", "POST", "PUT"])
def graph(request, organization_id, graph_id):
    if request.method == 'POST':
        return store_graph(request, organization_id, graph_id)
    elif request.method == "PUT":
        return store_graph(request, organization_id, graph_id, is_update=True)
    else:
        return get_graph(request, organization_id, graph_id)


def store_graph(request, organization_id, graph_id, is_update=False):
    try:
        check_organization_is_registered(organization_id)
    except (InvalidTrustedParty, UncheckedTrustedParty, OrganizationNotRegistered) as e:
        return JsonResponse({"error": str(e)}, status=404)

    json_data = json.loads(request.body)
    expected_json_fields = ('graph', 'signature', 'graphFormat')
    for field in expected_json_fields:
        if field not in json_data:
            return JsonResponse({"error": f"Mandatory field '{field}' not present in request!"}, status=400)

    validator = InputGraphChecker(json_data['graph'], json_data['graphFormat'])
    try:
        validator.parse_graph()
        if is_update:
            check_graph_id_belongs_to_meta(validator.get_meta_provenance_id(), graph_id, organization_id)
            if not graph_exists(organization_id, graph_id):
                return JsonResponse({"error": f"Graph with id={graph_id} does not exist. Please check whether the ID"
                                              f" you have given is correct."}, status=404)
        else:
            validator.check_ids_match(graph_id)
    except DoesNotExist:
        return JsonResponse({"error": f"Graph with id [{graph_id}] does not "
                                      f"exist under organization [{organization_id}]"}, status=404)
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
        validator.validate_graph()
    except (IncorrectPIDs, HasNoBundles, TooManyBundles, DocumentError) as e:
        return JsonResponse({"error": str(e)}, status=400)

    controller.store_connectors(validator.get_forward_connectors(), validator.get_backward_connectors(),
                                validator.get_bundle_id(), validator.get_meta_provenance_id(), organization_id)

    # TODO -- uncomment once TP is implemented and running
    # tp_url = get_TP_url_by_organization(organization_id)
    # token = controller.send_token_request_to_TP(json_data, tp_url)
    token = get_dummy_token()

    document = validator.get_document()
    import_graph(document, json_data, copy.deepcopy(token), graph_id, validator.get_meta_provenance_id(), is_update)
    controller.store_token_into_db(token, validator.get_bundle_id())

    return JsonResponse({"token": token}, status=200)


def get_graph(request, organization_id, graph_id):
    try:
        d = controller.get_provenance(organization_id, graph_id)
        t = controller.get_token(organization_id, graph_id, d)
    except DoesNotExist:
        return JsonResponse({"error": f"Graph with id [{graph_id}] does not "
                                      f"exist under organization [{organization_id}]"}, status=404)

    return JsonResponse({"graph": d.graph, "token": t})


@csrf_exempt
@require_GET
def graph_meta(request, meta_id):
    requested_format = request.GET.get('format', 'rdf').lower()
    organization_id = request.GET.get('organizationId', None)

    if requested_format not in ('rdf', 'json', 'xml', 'provn'):
        return JsonResponse({"error": f"Requested format [{requested_format}] is not supported!"}, status=400)

    try:
        g = controller.get_b64_encoded_meta_provenance(meta_id, requested_format)
    except DoesNotExist:
        return JsonResponse({"error": f"The meta-provenance with id [{meta_id}] does not exist"}, status=404)

    # TODO -- uncomment once TP is up and running
    # if organization_id is not None:
    #     tp_url = controller.get_TP_url_by_organization(organization_id)
    # else:
    #     tp_url = None
    # t = controller.send_token_request_to_TP({"graph": g}, tp_url)
    t = get_dummy_token()

    return JsonResponse({"graph": g, "token": t})


@csrf_exempt
@require_GET
def graph_domain_specific(request, organization_id, graph_id):
    return get_subgraph(request, organization_id, graph_id, True)


@csrf_exempt
@require_GET
def graph_backbone(request, organization_id, graph_id):
    return get_subgraph(request, organization_id, graph_id, False)


def get_subgraph(request, organization_id, graph_id, is_domain_specific):
    requested_format = request.GET.get('format', 'rdf')

    if requested_format not in ('rdf', 'json', 'xml', 'provn'):
        return JsonResponse({"error": f"Requested format [{requested_format}] is not supported!"}, status=400)

    found_in_db = False
    try:
        g, t = controller.query_db_for_subgraph(organization_id, graph_id, requested_format, is_domain_specific)
        found_in_db = True
    except DoesNotExist:
        try:
            g = controller.get_b64_encoded_subgraph(organization_id, graph_id, is_domain_specific, requested_format)

            # TODO -- uncomment once TP is up and running
            # tp_url = get_TP_url_by_organization(organization_id)
            # t = controller.send_token_request_to_TP({"graph": g}, tp_url)
            t = get_dummy_token()
        except DoesNotExist:
            return JsonResponse({"error": f"Graph with id [{graph_id}] does not "
                                          f"exist under organization [{organization_id}]"}, status=404)

    if not found_in_db:
        suffix = "domain" if is_domain_specific else "backbone"
        controller.store_subgraph_into_db(f"{organization_id}_{graph_id}_{suffix}", requested_format, g, t)

    return JsonResponse({"graph": g, "token": t})


@csrf_exempt
@require_GET
def connector_retrieve(request, connector_id):
    requested_format = request.GET.get('format', 'rdf').lower()

    if requested_format not in ('rdf', 'json', 'xml', 'provn'):
        return JsonResponse({"error": f"Requested format [{requested_format}] is not supported!"}, status=400)

    try:
        g = controller.get_b64_encoded_connector_bundle(connector_id, requested_format)
    except DoesNotExist:
        return JsonResponse({"error": f"The table for connector with id [{connector_id}] does not exist"}, status=404)

    return JsonResponse({"graph": g})