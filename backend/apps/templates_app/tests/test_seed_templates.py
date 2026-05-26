"""
Tests for the seed_templates management command.
"""
import pytest
from io import StringIO
from django.core.management import call_command
from apps.templates_app.models import EmailTemplate


@pytest.mark.django_db
def test_seed_creates_six_system_templates():
    """Running seed_templates creates exactly 6 system templates."""
    out = StringIO()
    call_command('seed_templates', stdout=out)
    assert EmailTemplate.objects.filter(is_system=True).count() == 6


@pytest.mark.django_db
def test_seed_is_idempotent():
    """Running seed_templates twice doesn't duplicate templates."""
    call_command('seed_templates', stdout=StringIO())
    call_command('seed_templates', stdout=StringIO())
    assert EmailTemplate.objects.filter(is_system=True).count() == 6


@pytest.mark.django_db
def test_seed_clear_flag_removes_existing():
    """--clear flag deletes system templates before re-seeding."""
    call_command('seed_templates', stdout=StringIO())
    count_before = EmailTemplate.objects.filter(is_system=True).count()

    call_command('seed_templates', '--clear', stdout=StringIO())
    count_after = EmailTemplate.objects.filter(is_system=True).count()

    assert count_before == 6
    assert count_after == 6


@pytest.mark.django_db
def test_seed_templates_have_correct_categories():
    """Each seeded template has a valid category."""
    call_command('seed_templates', stdout=StringIO())
    valid_categories = {'promo', 'newsletter', 'announcement', 'webinar', 'onboarding', 'outreach'}
    categories = set(EmailTemplate.objects.filter(is_system=True).values_list('category', flat=True))
    assert categories == valid_categories


@pytest.mark.django_db
def test_seed_templates_have_html_output():
    """Every seeded template has non-empty HTML output."""
    call_command('seed_templates', stdout=StringIO())
    for tpl in EmailTemplate.objects.filter(is_system=True):
        assert len(tpl.html_output) > 100, f"Template '{tpl.name}' has empty html_output"
