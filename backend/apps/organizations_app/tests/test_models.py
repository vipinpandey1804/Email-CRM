import pytest
from organizations.models import Organization, OrganizationUser
from apps.organizations_app.tests.factories import OrgProfileFactory, OrgUserProfileFactory


@pytest.mark.django_db
def test_org_profile_created_with_org():
    profile = OrgProfileFactory()
    assert profile.organization is not None
    assert profile.plan == 'internal'
    assert profile.brand_colors == {}


@pytest.mark.django_db
def test_org_user_profile_has_role():
    profile = OrgUserProfileFactory()
    assert profile.role in ('admin', 'editor', 'viewer')


@pytest.mark.django_db
def test_org_profile_str():
    profile = OrgProfileFactory(organization__name='Acme Corp')
    assert 'Acme Corp' in str(profile)
