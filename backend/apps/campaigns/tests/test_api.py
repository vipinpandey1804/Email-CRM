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


@pytest.mark.django_db
def test_send_now_without_recipients_returns_400():
    user = UserFactory()
    org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user)
    c = CampaignFactory(organization=org, status='draft')
    resp = client.post(f'/{c.id}/send-now?org_slug={org.slug}', headers=auth_headers(user))
    assert resp.status_code == 400
    c.refresh_from_db()
    assert c.status == 'draft'  # unchanged — not queued


@pytest.mark.django_db
def test_add_recipients_manual_then_send(monkeypatch):
    # Avoid touching the real task queue
    monkeypatch.setattr('django_q.tasks.async_task', lambda *a, **k: 'fake-task-id')

    user = UserFactory()
    org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user)
    c = CampaignFactory(organization=org, status='draft')

    add = client.post(
        f'/{c.id}/recipients/manual?org_slug={org.slug}',
        json={'recipients': [
            {'email': 'a@test.com', 'name': 'A'},
            {'email': 'b@test.com', 'name': 'B'},
            {'email': 'not-an-email', 'name': 'skip'},
        ]},
        headers=auth_headers(user),
    )
    assert add.status_code == 200
    body = add.json()
    assert body['created'] == 2
    assert body['skipped'] == 1
    assert body['total'] == 2

    resp = client.post(f'/{c.id}/send-now?org_slug={org.slug}', headers=auth_headers(user))
    assert resp.status_code == 200
    c.refresh_from_db()
    assert c.status == 'sending'


@pytest.mark.django_db
def test_add_recipients_manual_is_idempotent_on_email():
    user = UserFactory()
    org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user)
    c = CampaignFactory(organization=org, status='draft')
    payload = {'recipients': [{'email': 'dup@test.com', 'name': 'First'}]}
    client.post(f'/{c.id}/recipients/manual?org_slug={org.slug}', json=payload, headers=auth_headers(user))
    second = client.post(
        f'/{c.id}/recipients/manual?org_slug={org.slug}',
        json={'recipients': [{'email': 'dup@test.com', 'name': 'Second'}]},
        headers=auth_headers(user),
    )
    assert second.status_code == 200
    assert second.json()['total'] == 1  # not duplicated


@pytest.mark.django_db
def test_delete_recipient():
    user = UserFactory()
    org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user)
    c = CampaignFactory(organization=org, status='draft')
    client.post(
        f'/{c.id}/recipients/manual?org_slug={org.slug}',
        json={'recipients': [{'email': 'gone@test.com', 'name': 'X'}]},
        headers=auth_headers(user),
    )
    rid = client.get(f'/{c.id}/recipients?org_slug={org.slug}', headers=auth_headers(user)).json()[0]['id']
    resp = client.delete(f'/{c.id}/recipients/{rid}?org_slug={org.slug}', headers=auth_headers(user))
    assert resp.status_code == 200
    remaining = client.get(f'/{c.id}/recipients?org_slug={org.slug}', headers=auth_headers(user)).json()
    assert remaining == []
