from django.db import models


class Certificate(models.Model):
    CERTIFICATE_TYPES = [("root", "root"), ("intermediate", "intermediate"), ("leaf", "leaf")]

    cert_id = models.CharField(max_length=40, primary_key=True)
    cert = models.TextField()
    certificate_type = models.CharField(max_length=20, choices=CERTIFICATE_TYPES)
    is_verified = models.BooleanField(default=False)
    is_revoked = models.BooleanField(default=False)
    received_on = models.DateTimeField()
    confirmed_on = models.DateTimeField()

    superior_cert = models.ForeignKey('self', on_delete=models.RESTRICT, default=None)


class Organization(models.Model):
    certificate_id = models.ForeignKey(Certificate, on_delete=models.RESTRICT)
    org_name = models.CharField(max_length=40)


class Document(models.Model):
    certificate_id = models.ForeignKey(Certificate, on_delete=models.RESTRICT)
    organization_id = models.ForeignKey(Organization, on_delete=models.RESTRICT)
    document_text = models.TextField()
    created_on = models.DateTimeField()
    signature = models.BinaryField()


class Token(models.Model):
    HASH_FUNCTIONS = [("SHA256", "SHA256"),
                      ("SHA512", "SHA512"),
                      ("SHA3-256", "SHA3-256"),
                      ("SHA3-512", "SHA3-512")]

    document_id = models.ForeignKey(Document, on_delete=models.RESTRICT)
    hash = models.CharField(max_length=128)
    hash_function = models.CharField(max_length=15, choices=HASH_FUNCTIONS)
    created_on = models.DateTimeField()
    signature = models.BinaryField()
