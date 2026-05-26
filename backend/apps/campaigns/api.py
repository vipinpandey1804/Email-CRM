from ninja import Router, File
from ninja.errors import HttpError
from ninja.files import UploadedFile
from typing import List, Optional
from uuid import UUID
from organizations.models import OrganizationUser
from apps.accounts.auth import JWTAuth
from apps.campaigns.models import Campaign, CampaignRecipient
from apps.campaigns.schemas import (
    CampaignCreateIn, CampaignUpdateIn, CampaignOut, ScheduleIn, RecipientOut,
    RecipientsAddIn,
)
from apps.campaigns.services import parse_recipient_csv

router = Router(auth=JWTAuth())


def _get_org_or_403(user, org_slug: str):
    try:
        return OrganizationUser.objects.select_related('organization').get(
            organization__slug=org_slug, user=user
        ).organization
    except OrganizationUser.DoesNotExist:
        raise HttpError(403, 'Not a member of this organization')


@router.get('/', response=List[CampaignOut])
def list_campaigns(request, org_slug: str, status: Optional[str] = None):
    org = _get_org_or_403(request.auth, org_slug)
    qs = Campaign.objects.filter(organization=org)
    if status:
        qs = qs.filter(status=status)
    return [CampaignOut.from_orm(c) for c in qs]


@router.post('/', response=CampaignOut)
def create_campaign(request, org_slug: str, payload: CampaignCreateIn):
    org = _get_org_or_403(request.auth, org_slug)
    c = Campaign.objects.create(
        organization=org,
        name=payload.name,
        subject_line=payload.subject_line,
        preview_text=payload.preview_text,
        from_name=payload.from_name,
        from_email=payload.from_email,
        reply_to=payload.reply_to,
        tags=payload.tags,
        template_id=payload.template_id,
        created_by=request.auth,
    )
    return CampaignOut.from_orm(c)


@router.get('/{campaign_id}', response=CampaignOut)
def get_campaign(request, org_slug: str, campaign_id: UUID):
    org = _get_org_or_403(request.auth, org_slug)
    try:
        return CampaignOut.from_orm(Campaign.objects.get(id=campaign_id, organization=org))
    except Campaign.DoesNotExist:
        raise HttpError(404, 'Campaign not found')


@router.patch('/{campaign_id}', response=CampaignOut)
def update_campaign(request, org_slug: str, campaign_id: UUID, payload: CampaignUpdateIn):
    org = _get_org_or_403(request.auth, org_slug)
    try:
        c = Campaign.objects.get(id=campaign_id, organization=org)
    except Campaign.DoesNotExist:
        raise HttpError(404, 'Campaign not found')
    for field, value in payload.dict(exclude_none=True).items():
        setattr(c, field, value)
    c.save()
    return CampaignOut.from_orm(c)


@router.delete('/{campaign_id}')
def delete_campaign(request, org_slug: str, campaign_id: UUID):
    org = _get_org_or_403(request.auth, org_slug)
    try:
        c = Campaign.objects.get(id=campaign_id, organization=org)
    except Campaign.DoesNotExist:
        raise HttpError(404, 'Campaign not found')
    if c.status != 'draft':
        raise HttpError(400, 'Only draft campaigns can be deleted')
    c.delete()
    return {'detail': 'Deleted'}


@router.post('/{campaign_id}/schedule')
def schedule_campaign(request, org_slug: str, campaign_id: UUID, payload: ScheduleIn):
    from django_q.tasks import schedule as q_schedule
    org = _get_org_or_403(request.auth, org_slug)
    try:
        c = Campaign.objects.get(id=campaign_id, organization=org, status='draft')
    except Campaign.DoesNotExist:
        raise HttpError(404, 'Draft campaign not found')
    if not c.recipients.exists():
        raise HttpError(400, 'Add at least one recipient before scheduling')
    c.status = 'scheduled'
    c.scheduled_at = payload.scheduled_at
    c.save()
    q_schedule(
        'apps.campaigns.tasks.dispatch_campaign',
        str(campaign_id),
        schedule_type='O',
        next_run=payload.scheduled_at,
        name=f'campaign-{campaign_id}',
    )
    return {'detail': 'Campaign scheduled', 'scheduled_at': payload.scheduled_at.isoformat()}


@router.post('/{campaign_id}/send-now')
def send_campaign_now(request, org_slug: str, campaign_id: UUID):
    from django_q.tasks import async_task
    org = _get_org_or_403(request.auth, org_slug)
    try:
        c = Campaign.objects.get(id=campaign_id, organization=org, status='draft')
    except Campaign.DoesNotExist:
        raise HttpError(404, 'Draft campaign not found')
    if not c.recipients.exists():
        raise HttpError(400, 'Add at least one recipient before sending')
    c.status = 'sending'
    c.save()
    async_task('apps.campaigns.tasks.dispatch_campaign', str(campaign_id))
    return {'detail': 'Campaign queued for sending'}


@router.post('/{campaign_id}/recipients')
def upload_recipients(request, org_slug: str, campaign_id: UUID, file: UploadedFile = File(...)):
    org = _get_org_or_403(request.auth, org_slug)
    try:
        c = Campaign.objects.get(id=campaign_id, organization=org)
    except Campaign.DoesNotExist:
        raise HttpError(404, 'Campaign not found')
    content = file.read().decode('utf-8')
    recipients = parse_recipient_csv(content)
    created = 0
    for r in recipients:
        _, was_created = CampaignRecipient.objects.update_or_create(
            campaign=c,
            email=r['email'],
            defaults={'name': r['name'], 'personalization': r['personalization'], 'status': 'queued'},
        )
        if was_created:
            created += 1
    return {'total': len(recipients), 'created': created}


@router.post('/{campaign_id}/recipients/manual')
def add_recipients_manual(request, org_slug: str, campaign_id: UUID, payload: RecipientsAddIn):
    """Add recipients from a JSON list of {email, name} (no CSV needed)."""
    org = _get_org_or_403(request.auth, org_slug)
    try:
        c = Campaign.objects.get(id=campaign_id, organization=org)
    except Campaign.DoesNotExist:
        raise HttpError(404, 'Campaign not found')
    created = 0
    skipped = 0
    for r in payload.recipients:
        email = r.email.strip().lower()
        if not email or '@' not in email:
            skipped += 1
            continue
        _, was_created = CampaignRecipient.objects.update_or_create(
            campaign=c,
            email=email,
            defaults={'name': r.name.strip(), 'status': 'queued'},
        )
        if was_created:
            created += 1
    return {'created': created, 'skipped': skipped, 'total': c.recipients.count()}


@router.get('/{campaign_id}/recipients', response=List[RecipientOut])
def list_recipients(request, org_slug: str, campaign_id: UUID):
    org = _get_org_or_403(request.auth, org_slug)
    try:
        c = Campaign.objects.get(id=campaign_id, organization=org)
    except Campaign.DoesNotExist:
        raise HttpError(404, 'Campaign not found')
    return [RecipientOut.from_orm(r) for r in c.recipients.all()]


@router.delete('/{campaign_id}/recipients/{recipient_id}')
def delete_recipient(request, org_slug: str, campaign_id: UUID, recipient_id: UUID):
    org = _get_org_or_403(request.auth, org_slug)
    try:
        c = Campaign.objects.get(id=campaign_id, organization=org)
    except Campaign.DoesNotExist:
        raise HttpError(404, 'Campaign not found')
    deleted, _ = CampaignRecipient.objects.filter(campaign=c, id=recipient_id).delete()
    if not deleted:
        raise HttpError(404, 'Recipient not found')
    return {'detail': 'Recipient removed'}
