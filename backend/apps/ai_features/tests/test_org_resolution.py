"""
Tests for _get_org_for_user — the helper that resolves the authenticated
user's organization for AI SSE endpoints. Guards against the field-name
regression (org_user vs organization_user) that returned a 500.
"""
import pytest
from asgiref.sync import async_to_sync
from apps.ai_features.api import _get_org_for_user
from apps.accounts.tests.factories import UserFactory
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
