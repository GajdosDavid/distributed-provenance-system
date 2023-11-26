from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from prov.model import ProvDocument

from prov2neomodel.prov2neomodel import import_graph


@csrf_exempt
@require_POST
def index(request):
    graph = ProvDocument.deserialize(content=request.body, format="rdf")
    import_graph(graph)

    return HttpResponse("Hello, mon frere")
