from .models import Organization, Certificate
from OpenSSL import crypto
from trusted_party.settings import config
from datetime import datetime


def retrieve_organizations():
    orgs = Organization.objects.all()

    out = []
    for org in orgs:
        cert, _ = get_sorted_certificates(org.org_name)
        o = {"id": org.org_name, "certificate": cert}

        out.append(o)

    return out


def retrieve_organization(org_id, include_revoked=False):
    org = Organization.objects.get(org_name=org_id)

    active_cert, revoked = get_sorted_certificates(org.org_name)

    out = {
        "id": org.org_name,
        "certificate": active_cert.cert
    }

    if include_revoked:
        out.update({"revokedCertificates": [r.cert for r in revoked]})

    return out


def get_sorted_certificates(org_id):
    revoked_certs = list(Certificate.objects.get(organization=org_id, certificate_type="client", is_revoked=True))
    active_cert = Certificate.objects.get(organization=org_id, certificate_type="client", is_revoked=False)

    return active_cert, revoked_certs


def verify_chain_of_trust(client_cert, intermediate_certs: list):
    store = crypto.X509Store()
    for cert in config.trusted_certs:
        store.add_cert(cert)

    store_ctx = crypto.X509StoreContext(store, client_cert, intermediate_certs)
    store_ctx.verify_certificate()


def store_organization(json_data):
    org = Organization()
    org.org_name = json_data['id']

    c = Certificate()
    c.cert = json_data['clientCertificate']
    c.certificate_type = "client"
    c.is_revoked = False
    c.received_on = datetime.now()
    c.organization = org.org_name

    for cert in json_data['intermediateCerts']:
        c = Certificate()
        c.cert = cert
        c.certificate_type = "intermediate"
        c.is_revoked = False
        c.received_on = datetime.now()
        c.organization = org.org_name
