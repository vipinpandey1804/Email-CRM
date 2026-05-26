import uuid
from django.db import models
from django.conf import settings
from organizations.models import Organization


class EmailTemplate(models.Model):
    CATEGORY_CHOICES = [
        ('promo', 'Promotion'),
        ('newsletter', 'Newsletter'),
        ('announcement', 'Announcement'),
        ('webinar', 'Webinar'),
        ('onboarding', 'Onboarding'),
        ('outreach', 'Outreach'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='email_templates'
    )
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='promo')
    thumbnail_url = models.TextField(blank=True, default='')
    gjs_components = models.JSONField(default=dict, blank=True)
    gjs_styles = models.JSONField(default=dict, blank=True)
    mjml_source = models.TextField(blank=True, default='')
    html_output = models.TextField(blank=True, default='')
    is_system = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_templates',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self) -> str:
        return self.name
