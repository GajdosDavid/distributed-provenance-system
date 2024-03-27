from django.urls import path

from . import views

urlpatterns = [
    path("info", views.info, name="information"),
    path("organizations", views.organizations, name="organizations"),
    path("organizations/<org_id>", views.retrieve_organization, name="retrieval_of_organization"),
    path("organizations/<org_id>/certs", views.certs, name="certificates"),
    path("organizations/<org_id>/certs/<cert_id>", views.specific_cert, name="specific_certificate"),
    path("generateToken", views.generate_token, name="token_generation"),
    path("organizations/<org_id>/documents/<doc_id>", views.retrieve_document, name="dokument_retrieval"),
    path("organizations/<org_id>/tokens", views.retrieve_all_tokens, name="all_token_retrieval"),
    path("organizations/<org_id>/tokens/<token_id>", views.retrieve_token, name="token_retrieval"),
]