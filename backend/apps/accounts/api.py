from ninja import Router
from ninja.errors import HttpError
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils.text import slugify
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from django.conf import settings
from organizations.models import Organization, OrganizationUser, OrganizationOwner

from apps.accounts.models import User
from apps.accounts.auth import JWTAuth
from apps.accounts.schemas import LoginIn, RegisterIn, TokenOut, GoogleAuthIn, MeOut
from apps.organizations_app.models import OrganizationProfile, OrganizationUserProfile

router = Router()


@router.post('/register', response=TokenOut, auth=None)
def register(request, payload: RegisterIn):
    email = payload.email.strip().lower()
    if not email or '@' not in email:
        raise HttpError(400, 'A valid email is required')
    if len(payload.password) < 8:
        raise HttpError(400, 'Password must be at least 8 characters')
    if not payload.organization_name.strip():
        raise HttpError(400, 'Organization name is required')
    if User.objects.filter(email__iexact=email).exists():
        raise HttpError(400, 'An account with this email already exists')

    with transaction.atomic():
        user = User.objects.create_user(
            email=email,
            password=payload.password,
            full_name=payload.full_name.strip(),
        )

        # Generate a unique slug from the organization name.
        base_slug = slugify(payload.organization_name) or 'org'
        slug = base_slug
        suffix = 2
        while Organization.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{suffix}'
            suffix += 1

        org = Organization.objects.create(name=payload.organization_name.strip(), slug=slug)
        org_user = OrganizationUser.objects.create(user=user, organization=org, is_admin=True)
        OrganizationOwner.objects.create(organization=org, organization_user=org_user)
        OrganizationProfile.objects.create(organization=org)
        OrganizationUserProfile.objects.create(org_user=org_user, role='admin')

    refresh = RefreshToken.for_user(user)
    return TokenOut(access=str(refresh.access_token), refresh=str(refresh))


@router.post('/token', response=TokenOut, auth=None)
def login(request, payload: LoginIn):
    user = authenticate(request, username=payload.email, password=payload.password)
    if not user:
        raise HttpError(401, 'Invalid email or password')
    refresh = RefreshToken.for_user(user)
    return TokenOut(access=str(refresh.access_token), refresh=str(refresh))


@router.post('/token/refresh', response=TokenOut, auth=None)
def refresh_token(request, payload: dict):
    try:
        refresh = RefreshToken(payload.get('refresh', ''))
        return TokenOut(access=str(refresh.access_token), refresh=str(refresh))
    except TokenError as e:
        raise HttpError(401, str(e))


@router.post('/google', response=TokenOut, auth=None)
def google_auth(request, payload: GoogleAuthIn):
    try:
        idinfo = google_id_token.verify_oauth2_token(
            payload.id_token,
            google_requests.Request(),
            settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id'],
        )
    except ValueError:
        raise HttpError(401, 'Invalid Google token')

    email = idinfo.get('email')
    full_name = idinfo.get('name', '')
    if not email:
        raise HttpError(400, 'Google account has no email')

    user, _ = User.objects.get_or_create(
        email=email,
        defaults={'full_name': full_name, 'is_active': True},
    )
    refresh = RefreshToken.for_user(user)
    return TokenOut(access=str(refresh.access_token), refresh=str(refresh))


@router.post('/logout', auth=JWTAuth())
def logout(request, payload: dict):
    try:
        token = RefreshToken(payload.get('refresh', ''))
        token.blacklist()
    except TokenError:
        pass
    return {'detail': 'Logged out'}


@router.get('/me', response=MeOut, auth=JWTAuth())
def me(request):
    user = request.auth
    return MeOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_staff=user.is_staff,
    )
