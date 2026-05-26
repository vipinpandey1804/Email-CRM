import pytest
from ninja.testing import TestClient
from apps.templates_app.api import router
from apps.templates_app.models import EmailTemplate
from apps.templates_app.tests.factories import EmailTemplateFactory
from apps.organizations_app.tests.factories import OrganizationFactory, OrganizationUserFactory
from apps.accounts.tests.factories import UserFactory
from rest_framework_simplejwt.tokens import RefreshToken

client = TestClient(router)


def auth_headers(user):
    token = str(RefreshToken.for_user(user).access_token)
    return {'Authorization': f'Bearer {token}'}


@pytest.mark.django_db
def test_list_templates_only_returns_org_templates():
    user = UserFactory()
    org = OrganizationFactory()
    other_org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user)
    EmailTemplateFactory(organization=org, name='Mine')
    EmailTemplateFactory(organization=other_org, name='Other')
    resp = client.get(f'/?org_slug={org.slug}', headers=auth_headers(user))
    assert resp.status_code == 200
    names = [t['name'] for t in resp.json()]
    assert 'Mine' in names
    assert 'Other' not in names


@pytest.mark.django_db
def test_create_template():
    user = UserFactory()
    org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user)
    resp = client.post(
        f'/?org_slug={org.slug}',
        json={'name': 'New Template', 'category': 'promo'},
        headers=auth_headers(user),
    )
    assert resp.status_code == 200
    assert resp.json()['name'] == 'New Template'


@pytest.mark.django_db
def test_get_template_returns_gjs_data():
    user = UserFactory()
    org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user)
    t = EmailTemplateFactory(
        organization=org,
        gjs_components={'type': 'mj-body'},
        gjs_styles={'font': 'sans-serif'},
    )
    resp = client.get(f'/{t.id}?org_slug={org.slug}', headers=auth_headers(user))
    assert resp.status_code == 200
    assert resp.json()['gjs_components'] == {'type': 'mj-body'}


@pytest.mark.django_db
def test_duplicate_template():
    user = UserFactory()
    org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user)
    t = EmailTemplateFactory(organization=org, name='Original')
    resp = client.post(f'/{t.id}/duplicate?org_slug={org.slug}', headers=auth_headers(user))
    assert resp.status_code == 200
    assert resp.json()['name'] == 'Original (Copy)'
    assert resp.json()['is_system'] is False


@pytest.mark.django_db
def test_system_templates_visible_across_orgs():
    user = UserFactory()
    org = OrganizationFactory()
    system_org = OrganizationFactory(name='Maven System')
    OrganizationUserFactory(organization=org, user=user)
    EmailTemplateFactory(organization=org, name='Mine')
    EmailTemplateFactory(organization=system_org, name='Cloud Promo', is_system=True)
    resp = client.get(f'/?org_slug={org.slug}', headers=auth_headers(user))
    assert resp.status_code == 200
    names = {t['name'] for t in resp.json()}
    assert {'Mine', 'Cloud Promo'} <= names


@pytest.mark.django_db
def test_duplicate_system_template_lands_in_user_org():
    user = UserFactory()
    org = OrganizationFactory()
    system_org = OrganizationFactory(name='Maven System')
    OrganizationUserFactory(organization=org, user=user)
    sys_tpl = EmailTemplateFactory(organization=system_org, name='Webinar', is_system=True)
    resp = client.post(f'/{sys_tpl.id}/duplicate?org_slug={org.slug}', headers=auth_headers(user))
    assert resp.status_code == 200
    assert resp.json()['is_system'] is False
    dup = EmailTemplate.objects.get(id=resp.json()['id'])
    assert dup.organization_id == org.id


@pytest.mark.django_db
def test_get_system_template_from_other_org():
    user = UserFactory()
    org = OrganizationFactory()
    system_org = OrganizationFactory(name='Maven System')
    OrganizationUserFactory(organization=org, user=user)
    sys_tpl = EmailTemplateFactory(organization=system_org, name='Onboarding', is_system=True)
    resp = client.get(f'/{sys_tpl.id}?org_slug={org.slug}', headers=auth_headers(user))
    assert resp.status_code == 200
    assert resp.json()['name'] == 'Onboarding'
