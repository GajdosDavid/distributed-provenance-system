from django.urls import path

from . import views

urlpatterns = [
    path("info", views.info, name="information"),
    path("organizations", views.organizations, name="organizations"),
    path("organizations/<org_id>", views.specific_organization, name="retrieval_of_organization"),
    path("organizations/<org_id>/certs", views.certs, name="certificates"),
    path("organizations/<org_id>/documents/<doc_id>", views.retrieve_document, name="dokument_retrieval"),
    path("organizations/<org_id>/documents/<doc_id>/tokens", views.specific_token, name="token_retrieval"),
    path("organizations/<org_id>/tokens", views.retrieve_all_tokens, name="all_token_retrieval"),
    path("issueToken", views.issue_token, name="token_generation"),
    path("verifySignature", views.verify_signature, name="signature_verification"),
]
