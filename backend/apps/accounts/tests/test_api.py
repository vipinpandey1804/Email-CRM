import pytest
from ninja.testing import TestClient
from apps.accounts.api import router
from apps.accounts.tests.factories import UserFactory

client = TestClient(router)


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
