from django.urls import path

from . import views

urlpatterns = [
    path("organization/<organization_id>/graphs/<graph_id>/", views.graph, name="graphs"),
    path("organization/<organization_id>/graphs/<graph_id>/meta-provenance", views.graph_meta, name="meta_prov"),
    path("organization/<organization_id>/graphs/<graph_id>/domain-specific", views.graph_domain_specific, name="domain_specific_part"),
    path("organization/<organization_id>/graphs/<graph_id>/backbone", views.graph_backbone, name="backbone"),
]