"""
Tests for _get_org_for_user — the helper that resolves the authenticated
user's organization for AI SSE endpoints. Guards against the field-name
regression (org_user vs organization_user) that returned a 500.
"""
import pytest
from asgiref.sync import async_to_sync
from django.test import override_settings
from apps.ai_features.api import _get_org_for_user, _get_api_key
from apps.accounts.tests.factories import UserFactory
from apps.organizations_app.models import OrganizationProfile
from apps.organizations_app.tests.factories import (
    OrganizationFactory,
    OrganizationUserFactory,
    OrgUserProfileFactory,
)


@pytest.mark.django_db
def test_resolves_org_via_user_profile():
    user = UserFactory()
    org = OrganizationFactory()
    org_user = OrganizationUserFactory(organization=org, user=user)
    OrgUserProfileFactory(org_user=org_user)

    result = async_to_sync(_get_org_for_user)(user)

    assert result is not None
    assert result.id == org.id


@pytest.mark.django_db
def test_returns_none_when_user_has_no_profile():
    user = UserFactory()
    result = async_to_sync(_get_org_for_user)(user)
    assert result is None


@pytest.mark.django_db
@override_settings(OPENAI_API_KEY='sk-env-fallback')
def test_api_key_falls_back_to_env_when_org_has_none():
    org = OrganizationFactory()
    OrganizationProfile.objects.create(organization=org)  # empty per-org key
    assert async_to_sync(_get_api_key)(org) == 'sk-env-fallback'


@pytest.mark.django_db
@override_settings(OPENAI_API_KEY='sk-env-fallback')
def test_api_key_prefers_org_specific_key():
    org = OrganizationFactory()
    OrganizationProfile.objects.create(organization=org, openai_api_key='sk-org-specific')
    assert async_to_sync(_get_api_key)(org) == 'sk-org-specific'


@pytest.mark.django_db
@override_settings(OPENAI_API_KEY='')
def test_api_key_empty_when_neither_configured():
    org = OrganizationFactory()
    OrganizationProfile.objects.create(organization=org)
    assert async_to_sync(_get_api_key)(org) == ''
