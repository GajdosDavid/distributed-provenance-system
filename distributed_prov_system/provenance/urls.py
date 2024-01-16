from django.urls import path

from . import views

urlpatterns = [
    path("organizations/<organization_id>/graphs/<graph_id>/", views.graph, name="graphs"),
    path("organizations/<organization_id>/graphs/meta/<meta_id>/", views.graph_meta, name="meta_prov"),
#    path("organizations/<organization_id>/graphs/<graph_id>/meta-provenance", views.graph_meta, name="meta_prov"),
    path("organizations/<organization_id>/graphs/<graph_id>/domain-specific", views.graph_domain_specific, name="domain_specific_part"),
    path("organizations/<organization_id>/graphs/<graph_id>/backbone", views.graph_backbone, name="backbone"),
]