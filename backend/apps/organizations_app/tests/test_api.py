import pytest
from ninja.testing import TestClient
from apps.organizations_app.api import router
from apps.accounts.tests.factories import UserFactory
from apps.organizations_app.tests.factories import (
    OrganizationFactory, OrganizationUserFactory, OrgProfileFactory
)

client = TestClient(router)


def auth_headers(user):
    from rest_framework_simplejwt.tokens import RefreshToken
    token = str(RefreshToken.for_user(user).access_token)
    return {'Authorization': f'Bearer {token}'}


@pytest.mark.django_db
def test_list_orgs_returns_only_user_orgs():
    user = UserFactory()
    org1 = OrganizationFactory(name='Org Alpha')
    org2 = OrganizationFactory(name='Org Beta')
    OrgProfileFactory(organization=org1)
    OrganizationUserFactory(organization=org1, user=user)
    # user is NOT in org2
    resp = client.get('/', headers=auth_headers(user))
    assert resp.status_code == 200
    names = [o['name'] for o in resp.json()]
    assert 'Org Alpha' in names
    assert 'Org Beta' not in names


@pytest.mark.django_db
def test_get_org_returns_404_if_not_member():
    user = UserFactory()
    org = OrganizationFactory(slug='secret-org')
    resp = client.get('/secret-org', headers=auth_headers(user))
    assert resp.status_code == 404


@pytest.mark.django_db
def test_invite_user_requires_admin():
    user = UserFactory()
    org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user, is_admin=False)
    resp = client.post(
        f'/{org.slug}/invite',
        json={'email': 'newuser@test.com', 'role': 'editor'},
        headers=auth_headers(user),
    )
    assert resp.status_code == 403
