import uuid
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from organizations.models import Organization
from apps.templates_app.models import EmailTemplate


class Campaign(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='campaigns'
    )
    template = models.ForeignKey(
        EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='campaigns'
    )
    name = models.CharField(max_length=200)
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    subject_line = models.CharField(max_length=300, blank=True, default='')
    preview_text = models.CharField(max_length=200, blank=True, default='')
    from_name = models.CharField(max_length=100, blank=True, default='')
    from_email = models.EmailField(blank=True, default='')
    reply_to = models.EmailField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_campaigns',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self) -> str:
        return self.name


class CampaignRecipient(models.Model):
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='recipients')
    email = models.EmailField()
    name = models.CharField(max_length=200, blank=True, default='')
    personalization = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, default='')

    class Meta:
        unique_together = [('campaign', 'email')]

    def __str__(self) -> str:
        return f'{self.email} -> {self.campaign.name}'
