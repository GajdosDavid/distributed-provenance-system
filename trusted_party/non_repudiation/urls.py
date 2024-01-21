from django.urls import path

from . import views

urlpatterns = [
    path("organizations", views.organizations, name="organizations"),
    path("organizations/<org_id>/certs", views.certs, name="certificates"),
    path("organizations/<org_id>/certs/<cert_id>", views.specific_cert, name="specific_certificate"),
    path("ownCertificates", views.own_certs, name="own_certificates"),
    path("generateToken", views.generate_token, name="token_generation"),
    path("organizations/<org_id>/documents/<doc_id>", views.retrieve_document, name="dokument_retrieval"),
    path("organizations/<org_id>/tokens", views.retrieve_all_tokens, name="all_token_retrieval"),
    path("organizations/<org_id>/tokens/<token_id>", views.retrieve_token, name="token_retrieval"),
]