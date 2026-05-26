from ninja import Router
from ninja.errors import HttpError
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from django.conf import settings

from apps.accounts.models import User
from apps.accounts.auth import JWTAuth
from apps.accounts.schemas import LoginIn, TokenOut, GoogleAuthIn, MeOut

router = Router()


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
