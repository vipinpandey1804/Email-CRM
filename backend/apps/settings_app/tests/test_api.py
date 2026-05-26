import pytest
from ninja.testing import TestClient
from apps.settings_app.api import router
from apps.organizations_app.tests.factories import OrganizationFactory, OrganizationUserFactory
from apps.accounts.tests.factories import UserFactory
from rest_framework_simplejwt.tokens import RefreshToken

client = TestClient(router)


def auth_headers(user):
    token = str(RefreshToken.for_user(user).access_token)
    return {'Authorization': f'Bearer {token}'}


@pytest.mark.django_db
def test_save_smtp_config():
    user = UserFactory()
    org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user, is_admin=True)
    resp = client.put(
        f'/smtp?org_slug={org.slug}',
        json={
            'host': 'smtp.gmail.com', 'port': 587,
            'username': 'test@gmail.com', 'password': 'secret',
            'use_tls': True, 'use_ssl': False,
        },
        headers=auth_headers(user),
    )
    assert resp.status_code == 200
    assert resp.json()['host'] == 'smtp.gmail.com'
    assert 'password' not in resp.json()


@pytest.mark.django_db
def test_get_smtp_does_not_return_password():
    from apps.settings_app.models import SMTPConfig
    user = UserFactory()
    org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user)
    SMTPConfig.objects.create(organization=org, host='smtp.test.com', port=587, password='secret')
    resp = client.get(f'/smtp?org_slug={org.slug}', headers=auth_headers(user))
    assert resp.status_code == 200
    data = resp.json()
    assert data['host'] == 'smtp.test.com'
    assert 'password' not in data


@pytest.mark.django_db
def test_update_ai_key():
    user = UserFactory()
    org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user, is_admin=True)
    resp = client.put(
        f'/ai-key?org_slug={org.slug}',
        json={'openai_api_key': 'sk-test-key'},
        headers=auth_headers(user),
    )
    assert resp.status_code == 200
    assert resp.json()['detail'] == 'API key updated'
