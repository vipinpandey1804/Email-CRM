from ninja import Router
from ninja.errors import HttpError
from organizations.models import OrganizationUser
from apps.accounts.auth import JWTAuth
from apps.settings_app.models import SMTPConfig
from apps.settings_app.schemas import SMTPConfigIn, SMTPConfigOut, TestEmailIn, AIKeyIn
from apps.settings_app.services import test_smtp_connection
from apps.organizations_app.models import OrganizationProfile

router = Router(auth=JWTAuth())


def _get_org_or_403(user, org_slug: str):
    try:
        return OrganizationUser.objects.select_related('organization').get(
            organization__slug=org_slug, user=user
        ).organization
    except OrganizationUser.DoesNotExist:
        raise HttpError(403, 'Not a member of this organization')


def _get_admin_org(user, org_slug: str):
    try:
        ou = OrganizationUser.objects.select_related('organization').get(
            organization__slug=org_slug, user=user
        )
        if not ou.is_admin:
            raise HttpError(403, 'Admin access required')
        return ou.organization
    except OrganizationUser.DoesNotExist:
        raise HttpError(403, 'Not a member of this organization')


@router.get('/smtp', response=SMTPConfigOut)
def get_smtp(request, org_slug: str):
    org = _get_org_or_403(request.auth, org_slug)
    try:
        cfg = SMTPConfig.objects.get(organization=org)
        return SMTPConfigOut(
            host=cfg.host, port=cfg.port, username=cfg.username,
            use_tls=cfg.use_tls, use_ssl=cfg.use_ssl, is_verified=cfg.is_verified
        )
    except SMTPConfig.DoesNotExist:
        raise HttpError(404, 'SMTP config not configured')


@router.put('/smtp', response=SMTPConfigOut)
def save_smtp(request, org_slug: str, payload: SMTPConfigIn):
    org = _get_admin_org(request.auth, org_slug)
    cfg, _ = SMTPConfig.objects.update_or_create(
        organization=org,
        defaults={
            'host': payload.host, 'port': payload.port,
            'username': payload.username, 'password': payload.password,
            'use_tls': payload.use_tls, 'use_ssl': payload.use_ssl,
            'is_verified': False,
        }
    )
    return SMTPConfigOut(
        host=cfg.host, port=cfg.port, username=cfg.username,
        use_tls=cfg.use_tls, use_ssl=cfg.use_ssl, is_verified=cfg.is_verified
    )


@router.post('/smtp/test')
def test_smtp(request, org_slug: str, payload: TestEmailIn):
    org = _get_admin_org(request.auth, org_slug)
    try:
        cfg = SMTPConfig.objects.get(organization=org)
    except SMTPConfig.DoesNotExist:
        raise HttpError(404, 'SMTP config not found')
    result = test_smtp_connection(
        host=cfg.host, port=cfg.port, username=cfg.username,
        password=cfg.password, use_tls=cfg.use_tls, use_ssl=cfg.use_ssl,
        to_email=payload.to_email,
    )
    if result['success']:
        cfg.is_verified = True
        cfg.save(update_fields=['is_verified'])
    return result


@router.put('/ai-key')
def update_ai_key(request, org_slug: str, payload: AIKeyIn):
    org = _get_admin_org(request.auth, org_slug)
    profile, _ = OrganizationProfile.objects.get_or_create(organization=org)
    profile.openai_api_key = payload.openai_api_key
    profile.save(update_fields=['openai_api_key'])
    return {'detail': 'API key updated'}
