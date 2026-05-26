import uuid
from django.db import models
from django.conf import settings
from organizations.models import Organization


class AIJob(models.Model):
    JOB_TYPE_CHOICES = [
        ('subject_lines', 'Subject Lines'),
        ('copy_optimize', 'Copy Optimize'),
        ('spam_check', 'Spam Check'),
        ('cta_suggest', 'CTA Suggest'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='ai_jobs')
    campaign = models.ForeignKey(
        'campaigns.Campaign', on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_jobs'
    )
    job_type = models.CharField(max_length=30, choices=JOB_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='ai_jobs'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.job_type} ({self.status})'
