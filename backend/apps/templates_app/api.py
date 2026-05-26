from ninja import Router
from ninja.errors import HttpError
from typing import List, Optional
from uuid import UUID
from organizations.models import OrganizationUser
from apps.accounts.auth import JWTAuth
from apps.templates_app.models import EmailTemplate
from apps.templates_app.schemas import TemplateCreateIn, TemplateSaveIn, TemplateOut

router = Router(auth=JWTAuth())


def _get_org_or_403(user, org_slug: str):
    try:
        ou = OrganizationUser.objects.select_related('organization').get(
            organization__slug=org_slug, user=user
        )
        return ou.organization
    except OrganizationUser.DoesNotExist:
        raise HttpError(403, 'Not a member of this organization')


@router.get('/', response=List[TemplateOut])
def list_templates(request, org_slug: str, category: Optional[str] = None, is_system: Optional[bool] = None):
    org = _get_org_or_403(request.auth, org_slug)
    qs = EmailTemplate.objects.filter(organization=org)
    if category:
        qs = qs.filter(category=category)
    if is_system is not None:
        qs = qs.filter(is_system=is_system)
    return [TemplateOut.from_orm(t) for t in qs]


@router.post('/', response=TemplateOut)
def create_template(request, org_slug: str, payload: TemplateCreateIn):
    org = _get_org_or_403(request.auth, org_slug)
    t = EmailTemplate.objects.create(
        organization=org,
        name=payload.name,
        category=payload.category,
        created_by=request.auth,
    )
    return TemplateOut.from_orm(t)


@router.get('/{template_id}', response=TemplateOut)
def get_template(request, org_slug: str, template_id: UUID):
    org = _get_org_or_403(request.auth, org_slug)
    try:
        t = EmailTemplate.objects.get(id=template_id, organization=org)
    except EmailTemplate.DoesNotExist:
        raise HttpError(404, 'Template not found')
    return TemplateOut.from_orm(t)


@router.patch('/{template_id}', response=TemplateOut)
def save_template(request, org_slug: str, template_id: UUID, payload: TemplateSaveIn):
    org = _get_org_or_403(request.auth, org_slug)
    try:
        t = EmailTemplate.objects.get(id=template_id, organization=org)
    except EmailTemplate.DoesNotExist:
        raise HttpError(404, 'Template not found')
    for field, value in payload.dict(exclude_none=True).items():
        setattr(t, field, value)
    t.save()
    return TemplateOut.from_orm(t)


@router.delete('/{template_id}')
def delete_template(request, org_slug: str, template_id: UUID):
    org = _get_org_or_403(request.auth, org_slug)
    try:
        t = EmailTemplate.objects.get(id=template_id, organization=org, is_system=False)
    except EmailTemplate.DoesNotExist:
        raise HttpError(404, 'Template not found or cannot be deleted')
    t.delete()
    return {'detail': 'Deleted'}


@router.post('/{template_id}/duplicate', response=TemplateOut)
def duplicate_template(request, org_slug: str, template_id: UUID):
    org = _get_org_or_403(request.auth, org_slug)
    try:
        t = EmailTemplate.objects.get(id=template_id, organization=org)
    except EmailTemplate.DoesNotExist:
        raise HttpError(404, 'Template not found')
    t.pk = None
    t.id = None
    t.name = f'{t.name} (Copy)'
    t.is_system = False
    t.created_by = request.auth
    t.save()
    return TemplateOut.from_orm(t)
