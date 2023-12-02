from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import BadRequest

from prov.model import ProvDocument
from prov2neomodel.prov2neomodel import import_graph
from OpenSSL import crypto
import json
import base64

from .certificate_manager import cert_manager


@csrf_exempt
@require_POST
def index(request):
    json_data = json.loads(request.body)

    try:
        user_cert = json_data['certificates']['user_cert']
        intermediate_certs = json_data['certificates']['intermediate_certs']
        cert_manager.verify_certificate(user_cert, intermediate_certs)
    except crypto.X509StoreContextError:
        raise BadRequest("Bad certificate")

    graph = base64.b64decode(json_data['graph']['data'])
    prov_doc = ProvDocument.deserialize(content=graph, format="rdf")
    import_graph(prov_doc)

    return HttpResponse("Hello, mon frere")
