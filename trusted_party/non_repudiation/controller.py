from .models import Organization, Certificate, Document, Token
from OpenSSL import crypto
from trusted_party.settings import config
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.primitives.asymmetric import padding


def retrieve_organizations():
    orgs = Organization.objects.all()

    out = []
    for org in orgs:
        cert, _ = get_sorted_certificates(org.org_name)
        o = {"id": org.org_name, "certificate": cert}

        out.append(o)

    return out


def retrieve_organization(org_id, include_revoked=False):
    org = Organization.objects.filter(org_name=org_id).first()

    active_cert, revoked = get_sorted_certificates(org.org_name)

    out = {
        "id": org.org_name,
        "certificate": active_cert.cert
    }

    if include_revoked:
        if len(revoked) != 0:
            out.update({"revokedCertificates": [r.cert for r in revoked]})

    return out


def get_sorted_certificates(org_id):
    revoked_certs = list(Certificate.objects.filter(organization=org_id, certificate_type="client", is_revoked=True).all())
    active_cert = Certificate.objects.filter(organization=org_id, certificate_type="client", is_revoked=False).first()

    return active_cert, revoked_certs


def verify_chain_of_trust(client_cert, intermediate_certs: list):
    serialized_client_cert = crypto.load_certificate(crypto.FILETYPE_PEM, client_cert)

    store = crypto.X509Store()

    serialized_intermediate_certs = []
    for cert in intermediate_certs:
        serialized_cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
        serialized_intermediate_certs.append(serialized_cert)

    for cert in config.trusted_certs:
        serialized_cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
        store.add_cert(serialized_cert)

    store_ctx = crypto.X509StoreContext(store, serialized_client_cert, serialized_intermediate_certs)
    store_ctx.verify_certificate()


def store_organization(org_id, client_cert, intermediate_certs):
    org = Organization()
    org.org_name = org_id
    org.save()

    serialized_client_cert = crypto.load_certificate(crypto.FILETYPE_PEM, client_cert)
    c = Certificate()
    c.cert_digest = serialized_client_cert.digest("sha256").decode('utf-8').replace(':', '')
    c.cert = client_cert
    c.certificate_type = "client"
    c.is_revoked = False
    c.received_on = datetime.now()
    c.organization = org
    c.save()

    for cert in intermediate_certs:
        serialized_cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert)

        c = Certificate()
        c.cert_digest = serialized_cert.digest("sha256").decode('utf-8').replace(':', '')
        c.cert = cert
        c.certificate_type = "intermediate"
        c.is_revoked = False
        c.received_on = datetime.now()
        c.organization = org
        c.save()


def update_certificate(org_id, client_cert, intermediate_certs):
    revoke_all_stored_certificates(org_id)

    org = Organization.objects.get(org_name=org_id)

    serialized_client_cert = crypto.load_certificate(crypto.FILETYPE_PEM, client_cert)
    c = Certificate()
    c.cert_digest = serialized_client_cert.digest("sha256").decode('utf-8').replace(':', '')
    c.cert = client_cert
    c.certificate_type = "client"
    c.is_revoked = False
    c.received_on = datetime.now()
    c.organization = org
    c.save()

    for cert in intermediate_certs:
        serialized_cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert)

        digest = serialized_cert.digest("sha256").decode('utf-8').replace(':', '')
        try:
            c = Certificate.objects.get(cert_digest=digest)
            c.is_revoked = False
            c.save()
        except ObjectDoesNotExist:
            c = Certificate()
            c.cert_digest = digest
            c.cert = cert
            c.certificate_type = "intermediate"
            c.is_revoked = False
            c.received_on = datetime.now()
            c.organization = org
            c.save()


def revoke_all_stored_certificates(org_id):
    client_certs = list(Certificate.objects.filter(organization=org_id, certificate_type="client").all())
    intermediate_certs = list(Certificate.objects.filter(organization=org_id, certificate_type="intermediate").all())

    for cert in client_certs:
        if not cert.is_revoked:
            cert.is_revoked = True
            cert.save()

    for cert in intermediate_certs:
        if not cert.is_revoked:
            cert.is_revoked = True
            cert.save()


def retrieve_document(org_id, doc_id):
    org = Organization.objects.filter(org_name=org_id)
    doc = Document.objects.filter(organization_id=org, document_id=doc_id)

    return doc


def retrieve_tokens(org_id):
    org = Organization.objects.filter(org_name=org_id).first()
    docs = Document.objects.filter(organization_id=org).all()

    tokens = {}
    for doc in docs:
        tokens[doc] = Token.objects.filter(document_id=doc).all()

    tokens_out = []
    for doc, tokens in tokens:
        for token in tokens:
            t = {
                "data": {
                    "originatorId": org.org_name,
                    "authorityId": config.id,
                    "tokenTimestamp": token.created_on,
                    "messageTimestamp": doc.created_on,
                    "graphImprint": token.hash
                },
                "signature": base64.b64encode(token.signature).decode('utf-8')
            }
            tokens_out.append(t)

    return tokens_out


def retrieve_specific_token(org_id, doc_id):
    org = Organization.objects.filter(org_name=org_id).first()
    doc = Document.objects.filter(organization_id=org, document_id=doc_id).first()
    tokens = Token.objects.filter(document_id=doc).all()

    tokens_out = []
    for token in tokens:
        t = {
            "data": {
                "originatorId": org.org_name,
                "authorityId": config.id,
                "tokenTimestamp": token.created_on,
                "messageTimestamp": doc.created_on,
                "graphImprint": token.hash
            },
            "signature": base64.b64encode(token.signature).decode('utf-8')
        }
        tokens_out.append(t)

    return tokens_out if len(tokens_out) > 1 else tokens_out[0]


def verify_signature(json_data):
    org_id = json_data['organizationId']
    graph = json_data['graph']
    signature = json_data['signature']

    org = Organization.objects.filter(org_name=org_id).first()
    cert = Certificate.objects.filter(organization=org, is_revoked=False).first()

    loaded_cert = load_pem_x509_certificate(cert.cert.encode('utf-8'), backend=default_backend())
    public_key = loaded_cert.public_key()

    public_key.verify(
        base64.b64decode(signature),
        base64.b64decode(graph),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    