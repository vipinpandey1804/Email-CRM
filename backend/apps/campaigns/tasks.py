import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone

from apps.campaigns.models import Campaign, CampaignRecipient
from apps.campaigns.services import render_personalized_html

logger = logging.getLogger(__name__)


def dispatch_campaign(campaign_id: str) -> None:
    """Django-Q2 task: sends all queued recipients for a campaign."""
    try:
        campaign = Campaign.objects.select_related(
            'organization', 'template', 'organization__smtp_config'
        ).get(id=campaign_id)
    except Campaign.DoesNotExist:
        logger.error(f'Campaign {campaign_id} not found')
        return

    try:
        smtp_config = campaign.organization.smtp_config
    except Exception:
        logger.error(f'No SMTP config for org {campaign.organization.id}')
        campaign.status = 'failed'
        campaign.save(update_fields=['status'])
        return

    html_template = ''
    if campaign.template:
        html_template = campaign.template.html_output

    recipients = CampaignRecipient.objects.filter(campaign=campaign, status='queued')

    for recipient in recipients:
        personalized_html = render_personalized_html(html_template, recipient.personalization)
        try:
            _send_single_email(
                smtp_config=smtp_config,
                to_email=recipient.email,
                to_name=recipient.name,
                subject=campaign.subject_line,
                from_name=campaign.from_name,
                from_email=campaign.from_email,
                html_body=personalized_html,
            )
            recipient.status = 'sent'
            recipient.sent_at = datetime.now(tz=timezone.utc)
            recipient.error_message = ''
        except Exception as e:
            logger.exception(f'Failed to send to {recipient.email}: {e}')
            recipient.status = 'failed'
            recipient.error_message = str(e)
        recipient.save(update_fields=['status', 'sent_at', 'error_message'])

    all_recipients = CampaignRecipient.objects.filter(campaign=campaign)
    failed_count = all_recipients.filter(status='failed').count()
    total_count = all_recipients.count()
    campaign.status = 'failed' if failed_count == total_count and total_count > 0 else 'sent'
    campaign.sent_at = datetime.now(tz=timezone.utc)
    campaign.save(update_fields=['status', 'sent_at'])


def _send_single_email(
    smtp_config,
    to_email: str,
    to_name: str,
    subject: str,
    from_name: str,
    from_email: str,
    html_body: str,
) -> None:
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f'{from_name} <{from_email}>' if from_name else from_email
    msg['To'] = f'{to_name} <{to_email}>' if to_name else to_email
    msg.attach(MIMEText(html_body, 'html'))

    smtp_class = smtplib.SMTP_SSL if smtp_config.use_ssl else smtplib.SMTP

    with smtp_class(smtp_config.host, smtp_config.port) as server:
        if smtp_config.use_tls and not smtp_config.use_ssl:
            server.starttls()
        if smtp_config.username:
            server.login(smtp_config.username, smtp_config.password)
        server.sendmail(from_email, [to_email], msg.as_string())
