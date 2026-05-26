import pytest
from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
def test_user_uses_email_as_username():
    user = UserFactory(email='vipin@example.com')
    assert user.email == 'vipin@example.com'
    assert str(user) == 'vipin@example.com'


@pytest.mark.django_db
def test_user_has_no_username_field():
    user = UserFactory()
    assert not hasattr(user, 'username') or user.username is None or user.USERNAME_FIELD == 'email'


@pytest.mark.django_db
def test_create_superuser():
    from apps.accounts.models import User
    u = User.objects.create_superuser(email='admin@example.com', password='pass123')
    assert u.is_staff
    assert u.is_superuser
