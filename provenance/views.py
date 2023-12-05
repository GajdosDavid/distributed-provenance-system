from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import BadRequest

from prov2neomodel.prov2neomodel import import_graph
from OpenSSL import crypto
import cryptography.exceptions
import json

from .validators import GraphInputValidator, InvalidGraph
from .certificate_manager import cert_manager


@csrf_exempt
@require_http_methods(["GET", "POST"])
def graphs(request):
    if request.method == 'POST':
        return graphs_post(request)
    else:
        return graphs_get(request)


def graphs_post(request):
    json_data = json.loads(request.body)

    try:
        user_cert = json_data['certificates']['user_cert']
        intermediate_certs = json_data['certificates']['intermediate_certs']
        cert_manager.verify_certificate(user_cert, intermediate_certs)
    except crypto.X509StoreContextError:
        raise BadRequest("Bad certificate")

    try:
        validator = GraphInputValidator(json_data)
        validator.verify_signature()
        validator.validate_graph()
    except cryptography.exceptions.InvalidSignature:
        raise BadRequest("Invalid signature")
    except InvalidGraph:
        raise BadRequest("Incorrect graph")

    graph = validator.get_graph()
    import_graph(graph, json_data)

    #s = graph.serialize(format='rdf')
    #print(s)
    return HttpResponse("Alles gut")


def graphs_get(request):
    pass
