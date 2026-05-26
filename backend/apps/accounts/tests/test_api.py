import pytest
from ninja.testing import TestClient
from apps.accounts.api import router
from apps.accounts.tests.factories import UserFactory
from apps.accounts.models import User
from organizations.models import Organization, OrganizationUser
from apps.organizations_app.models import OrganizationProfile, OrganizationUserProfile

client = TestClient(router)


_REGISTER_PAYLOAD = {
    'full_name': 'Ada Lovelace',
    'email': 'ada@maven.test',
    'password': 'supersecret1',
    'organization_name': 'Maven Labs',
}


@pytest.mark.django_db
def test_register_creates_user_org_and_membership():
    resp = client.post('/register', json=_REGISTER_PAYLOAD)
    assert resp.status_code == 200
    data = resp.json()
    assert 'access' in data and 'refresh' in data

    user = User.objects.get(email='ada@maven.test')
    assert user.full_name == 'Ada Lovelace'
    org = Organization.objects.get(slug='maven-labs')
    org_user = OrganizationUser.objects.get(user=user, organization=org)
    assert org_user.is_admin
    assert OrganizationProfile.objects.filter(organization=org).exists()
    assert OrganizationUserProfile.objects.filter(org_user=org_user, role='admin').exists()


@pytest.mark.django_db
def test_register_duplicate_email_returns_400():
    client.post('/register', json=_REGISTER_PAYLOAD)
    resp = client.post('/register', json=_REGISTER_PAYLOAD)
    assert resp.status_code == 400


@pytest.mark.django_db
def test_register_short_password_returns_400():
    payload = {**_REGISTER_PAYLOAD, 'password': 'short'}
    resp = client.post('/register', json=payload)
    assert resp.status_code == 400


@pytest.mark.django_db
def test_register_then_login_works():
    client.post('/register', json=_REGISTER_PAYLOAD)
    resp = client.post('/token', json={'email': 'ada@maven.test', 'password': 'supersecret1'})
    assert resp.status_code == 200


@pytest.mark.django_db
def test_register_unique_slug_on_duplicate_org_name():
    client.post('/register', json=_REGISTER_PAYLOAD)
    second = {**_REGISTER_PAYLOAD, 'email': 'grace@maven.test'}
    resp = client.post('/register', json=second)
    assert resp.status_code == 200
    slugs = set(Organization.objects.values_list('slug', flat=True))
    assert {'maven-labs', 'maven-labs-2'} <= slugs


@pytest.mark.django_db
def test_login_returns_jwt_tokens():
    UserFactory(email='login@test.com', password='pass1234')
    resp = client.post('/token', json={'email': 'login@test.com', 'password': 'pass1234'})
    assert resp.status_code == 200
    data = resp.json()
    assert 'access' in data
    assert 'refresh' in data


@pytest.mark.django_db
def test_login_wrong_password_returns_401():
    UserFactory(email='fail@test.com', password='correct')
    resp = client.post('/token', json={'email': 'fail@test.com', 'password': 'wrong'})
    assert resp.status_code == 401


@pytest.mark.django_db
def test_me_endpoint_requires_auth():
    resp = client.get('/me')
    assert resp.status_code == 401


@pytest.mark.django_db
def test_me_returns_user_info():
    UserFactory(email='me@test.com', password='testpass123')
    resp = client.post('/token', json={'email': 'me@test.com', 'password': 'testpass123'})
    token = resp.json()['access']
    resp2 = client.get('/me', headers={'Authorization': f'Bearer {token}'})
    assert resp2.status_code == 200
    assert resp2.json()['email'] == 'me@test.com'
