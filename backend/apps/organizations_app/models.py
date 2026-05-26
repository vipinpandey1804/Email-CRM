import uuid
from django.db import models
from django.conf import settings
from organizations.models import Organization, OrganizationUser
from core.fields import EncryptedTextField


class OrganizationProfile(models.Model):
    """Extends django-organizations' Organization with custom fields."""
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True,
    )
    logo_url = models.TextField(blank=True, default='')
    brand_colors = models.JSONField(default=dict, blank=True)
    plan = models.CharField(
        max_length=20,
        choices=[('internal', 'Internal'), ('saas', 'SaaS')],
        default='internal',
    )
    openai_api_key = EncryptedTextField(blank=True, default='')

    class Meta:
        verbose_name = 'Organization Profile'
        verbose_name_plural = 'Organization Profiles'

    def __str__(self) -> str:
        return f'Profile for {self.organization.name}'


class OrganizationUserProfile(models.Model):
    """Extends django-organizations' OrganizationUser with role + avatar."""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    ]
    org_user = models.OneToOneField(
        OrganizationUser,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True,
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='editor')
    avatar_url = models.TextField(blank=True, default='')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Organization User Profile'
        verbose_name_plural = 'Organization User Profiles'

    def __str__(self) -> str:
        return f'{self.org_user.user.email} @ {self.org_user.organization.name} ({self.role})'
