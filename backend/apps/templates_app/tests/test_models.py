import pytest
from apps.templates_app.tests.factories import EmailTemplateFactory


@pytest.mark.django_db
def test_email_template_str():
    t = EmailTemplateFactory(name='Welcome Email')
    assert str(t) == 'Welcome Email'


@pytest.mark.django_db
def test_email_template_defaults():
    t = EmailTemplateFactory()
    assert t.gjs_components == {}
    assert t.gjs_styles == {}
    assert t.is_system is False
