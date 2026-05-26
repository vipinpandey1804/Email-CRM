from ninja import Router
from ninja.errors import HttpError
from typing import List
from organizations.models import Organization, OrganizationUser
from apps.accounts.auth import JWTAuth
from apps.organizations_app.models import OrganizationProfile, OrganizationUserProfile
from apps.organizations_app.schemas import OrgOut, OrgUpdateIn, OrgUserOut, InviteIn

router = Router(auth=JWTAuth())


def _org_to_out(org: Organization) -> OrgOut:
    profile = getattr(org, 'profile', None)
    return OrgOut(
        id=org.id,
        name=org.name,
        slug=org.slug,
        is_active=org.is_active,
        plan=profile.plan if profile else 'internal',
        logo_url=profile.logo_url if profile else '',
    )


@router.get('/', response=List[OrgOut])
def list_orgs(request):
    user = request.auth
    org_ids = OrganizationUser.objects.filter(user=user).values_list('organization_id', flat=True)
    orgs = Organization.objects.filter(id__in=org_ids, is_active=True)
    return [_org_to_out(o) for o in orgs]


@router.get('/{slug}', response=OrgOut)
def get_org(request, slug: str):
    user = request.auth
    try:
        OrganizationUser.objects.get(organization__slug=slug, user=user)
    except OrganizationUser.DoesNotExist:
        raise HttpError(404, 'Organization not found')
    org = Organization.objects.get(slug=slug)
    return _org_to_out(org)


@router.patch('/{slug}', response=OrgOut)
def update_org(request, slug: str, payload: OrgUpdateIn):
    user = request.auth
    try:
        ou = OrganizationUser.objects.get(organization__slug=slug, user=user)
    except OrganizationUser.DoesNotExist:
        raise HttpError(404, 'Organization not found')
    if not ou.is_admin:
        raise HttpError(403, 'Admin access required')
    org = ou.organization
    if payload.name:
        org.name = payload.name
        org.save()
    profile, _ = OrganizationProfile.objects.get_or_create(organization=org)
    if payload.logo_url is not None:
        profile.logo_url = payload.logo_url
    if payload.brand_colors is not None:
        profile.brand_colors = payload.brand_colors
    profile.save()
    return _org_to_out(org)


@router.get('/{slug}/users', response=List[OrgUserOut])
def list_org_users(request, slug: str):
    user = request.auth
    try:
        OrganizationUser.objects.get(organization__slug=slug, user=user)
    except OrganizationUser.DoesNotExist:
        raise HttpError(404, 'Organization not found')
    org_users = OrganizationUser.objects.filter(
        organization__slug=slug
    ).select_related('user', 'profile')
    result = []
    for ou in org_users:
        profile = getattr(ou, 'profile', None)
        result.append(OrgUserOut(
            user_email=ou.user.email,
            user_full_name=ou.user.full_name,
            role=profile.role if profile else ('admin' if ou.is_admin else 'viewer'),
            is_admin=ou.is_admin,
        ))
    return result


@router.post('/{slug}/invite')
def invite_user(request, slug: str, payload: InviteIn):
    user = request.auth
    try:
        ou = OrganizationUser.objects.get(organization__slug=slug, user=user)
    except OrganizationUser.DoesNotExist:
        raise HttpError(404, 'Organization not found')
    if not ou.is_admin:
        raise HttpError(403, 'Admin access required')
    from apps.accounts.models import User as AppUser
    invited_user, created = AppUser.objects.get_or_create(
        email=payload.email,
        defaults={'is_active': True}
    )
    new_ou, ou_created = OrganizationUser.objects.get_or_create(
        organization=ou.organization,
        user=invited_user,
        defaults={'is_admin': payload.role == 'admin'}
    )
    if ou_created:
        OrganizationUserProfile.objects.create(org_user=new_ou, role=payload.role)
    return {'detail': f'User {payload.email} invited', 'created': ou_created}


@router.delete('/{slug}/users/{user_id}')
def remove_user(request, slug: str, user_id: int):
    user = request.auth
    try:
        ou = OrganizationUser.objects.get(organization__slug=slug, user=user)
    except OrganizationUser.DoesNotExist:
        raise HttpError(404, 'Organization not found')
    if not ou.is_admin:
        raise HttpError(403, 'Admin access required')
    OrganizationUser.objects.filter(organization__slug=slug, user_id=user_id).delete()
    return {'detail': 'User removed'}
