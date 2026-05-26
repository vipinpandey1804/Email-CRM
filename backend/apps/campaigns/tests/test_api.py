import pytest
from ninja.testing import TestClient
from apps.campaigns.api import router
from apps.campaigns.tests.factories import CampaignFactory
from apps.organizations_app.tests.factories import OrganizationFactory, OrganizationUserFactory
from apps.accounts.tests.factories import UserFactory
from rest_framework_simplejwt.tokens import RefreshToken

client = TestClient(router)


def auth_headers(user):
    token = str(RefreshToken.for_user(user).access_token)
    return {'Authorization': f'Bearer {token}'}


@pytest.mark.django_db
def test_create_campaign():
    user = UserFactory()
    org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user)
    resp = client.post(
        f'/?org_slug={org.slug}',
        json={'name': 'Test Campaign', 'subject_line': 'Hello World'},
        headers=auth_headers(user),
    )
    assert resp.status_code == 200
    assert resp.json()['status'] == 'draft'


@pytest.mark.django_db
def test_list_campaigns_scoped_to_org():
    user = UserFactory()
    org = OrganizationFactory()
    other_org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user)
    CampaignFactory(organization=org, name='Mine')
    CampaignFactory(organization=other_org, name='Other')
    resp = client.get(f'/?org_slug={org.slug}', headers=auth_headers(user))
    assert resp.status_code == 200
    names = [c['name'] for c in resp.json()]
    assert 'Mine' in names
    assert 'Other' not in names


@pytest.mark.django_db
def test_cannot_delete_sent_campaign():
    user = UserFactory()
    org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user)
    c = CampaignFactory(organization=org, status='sent')
    resp = client.delete(f'/{c.id}?org_slug={org.slug}', headers=auth_headers(user))
    assert resp.status_code == 400


@pytest.mark.django_db
def test_update_campaign():
    user = UserFactory()
    org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user)
    c = CampaignFactory(organization=org, name='Old Name')
    resp = client.patch(
        f'/{c.id}?org_slug={org.slug}',
        json={'name': 'New Name', 'subject_line': 'Updated Subject'},
        headers=auth_headers(user),
    )
    assert resp.status_code == 200
    assert resp.json()['name'] == 'New Name'
