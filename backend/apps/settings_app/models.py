from django.db import models
from organizations.models import Organization
from core.fields import EncryptedTextField


class SMTPConfig(models.Model):
    organization = models.OneToOneField(
        Organization, on_delete=models.CASCADE, related_name='smtp_config', primary_key=True
    )
    host = models.CharField(max_length=255, blank=True, default='')
    port = models.IntegerField(default=587)
    username = models.CharField(max_length=255, blank=True, default='')
    password = EncryptedTextField(blank=True, default='')
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'SMTP config for {self.organization.name}'
