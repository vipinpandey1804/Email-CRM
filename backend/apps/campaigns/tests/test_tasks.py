import pytest
from unittest.mock import patch, MagicMock
from apps.campaigns.tasks import dispatch_campaign
from apps.campaigns.tests.factories import CampaignFactory, CampaignRecipientFactory
from apps.organizations_app.tests.factories import OrganizationFactory
from apps.settings_app.models import SMTPConfig
from apps.templates_app.tests.factories import EmailTemplateFactory


@pytest.mark.django_db
def test_dispatch_campaign_sends_to_all_queued_recipients():
    org = OrganizationFactory()
    SMTPConfig.objects.create(
        organization=org, host='smtp.test.com', port=587,
        username='user', password='pass', use_tls=True
    )
    template = EmailTemplateFactory(organization=org, html_output='<p>Hello {{first_name}}</p>')
    campaign = CampaignFactory(
        organization=org,
        status='sending',
        subject_line='Test Subject',
        from_name='Maven',
        from_email='noreply@maven.com',
        template=template,
    )
    r1 = CampaignRecipientFactory(campaign=campaign, email='a@test.com', personalization={'first_name': 'Alice'})
    r2 = CampaignRecipientFactory(campaign=campaign, email='b@test.com', personalization={'first_name': 'Bob'})

    with patch('apps.campaigns.tasks.smtplib.SMTP') as mock_smtp:
        mock_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_instance
        dispatch_campaign(str(campaign.id))

    r1.refresh_from_db()
    r2.refresh_from_db()
    campaign.refresh_from_db()
    assert r1.status == 'sent'
    assert r2.status == 'sent'
    assert campaign.status == 'sent'


@pytest.mark.django_db
def test_dispatch_campaign_marks_failed_on_smtp_error():
    org = OrganizationFactory()
    SMTPConfig.objects.create(
        organization=org, host='bad-host', port=587,
        username='user', password='pass', use_tls=True
    )
    template = EmailTemplateFactory(organization=org, html_output='<p>Hello</p>')
    campaign = CampaignFactory(organization=org, status='sending', template=template)
    r = CampaignRecipientFactory(campaign=campaign)

    import smtplib
    with patch('apps.campaigns.tasks.smtplib.SMTP', side_effect=smtplib.SMTPException('connection failed')):
        dispatch_campaign(str(campaign.id))

    r.refresh_from_db()
    assert r.status == 'failed'
    assert 'connection failed' in r.error_message
