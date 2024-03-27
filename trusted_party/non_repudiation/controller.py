from .models import Organization, Certificate


def retrieve_organizations():
    orgs = Organization.objects.all()

    out = []
    for org in orgs:
        cert, _ = get_sorted_certificates(org)
        o = {"id": org.org_name, "certificate": cert}

        out.append(o)

    return out


def retrieve_organization(org_id, include_revoked=False):
    org = Organization.objects.get(org_name=org_id)

    active_cert, revoked = get_sorted_certificates(org)

    out = {
        "id": org.org_name,
        "certificate": active_cert.cert
    }

    if include_revoked:
        out.update({"revokedCertificates": [r.cert for r in revoked]})

    return out


def get_sorted_certificates(organization: Organization):
    revoked_certs = []
    active_cert = []

    for cert in organization.certificates.all():
        if cert.is_revoked:
            revoked_certs.append(cert)
        else:
            active_cert.append(cert)

    assert len(active_cert) == 1, "Only one cert expected to be active at a time!"

    return active_cert[0], revoked_certs
