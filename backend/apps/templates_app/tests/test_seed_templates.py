"""
Tests for the seed_templates management command.
"""
import pytest
from collections import Counter
from io import StringIO
from django.core.management import call_command
from apps.templates_app.models import EmailTemplate

EXPECTED_CATEGORIES = {'promo', 'newsletter', 'announcement', 'webinar', 'onboarding', 'outreach'}
EXPECTED_TOTAL = 60  # 10 per category


@pytest.mark.django_db
def test_seed_creates_full_library():
    """Running seed_templates creates ~10 templates per category."""
    call_command('seed_templates', stdout=StringIO())
    assert EmailTemplate.objects.filter(is_system=True).count() == EXPECTED_TOTAL


@pytest.mark.django_db
def test_seed_ten_per_category():
    """Each category has exactly 10 system templates."""
    call_command('seed_templates', stdout=StringIO())
    counts = Counter(
        EmailTemplate.objects.filter(is_system=True).values_list('category', flat=True)
    )
    assert set(counts) == EXPECTED_CATEGORIES
    for category in EXPECTED_CATEGORIES:
        assert counts[category] == 10, f'{category} has {counts[category]} templates'


@pytest.mark.django_db
def test_seed_is_idempotent():
    """Running seed_templates twice doesn't duplicate templates."""
    call_command('seed_templates', stdout=StringIO())
    call_command('seed_templates', stdout=StringIO())
    assert EmailTemplate.objects.filter(is_system=True).count() == EXPECTED_TOTAL


@pytest.mark.django_db
def test_seed_clear_flag_removes_existing():
    """--clear flag deletes system templates before re-seeding."""
    call_command('seed_templates', stdout=StringIO())
    count_before = EmailTemplate.objects.filter(is_system=True).count()

    call_command('seed_templates', '--clear', stdout=StringIO())
    count_after = EmailTemplate.objects.filter(is_system=True).count()

    assert count_before == EXPECTED_TOTAL
    assert count_after == EXPECTED_TOTAL


@pytest.mark.django_db
def test_seed_templates_have_correct_categories():
    """Each seeded template has a valid category."""
    call_command('seed_templates', stdout=StringIO())
    categories = set(EmailTemplate.objects.filter(is_system=True).values_list('category', flat=True))
    assert categories == EXPECTED_CATEGORIES


@pytest.mark.django_db
def test_seed_templates_render_full_html():
    """Every seeded template renders a complete, personalizable HTML document."""
    call_command('seed_templates', stdout=StringIO())
    for tpl in EmailTemplate.objects.filter(is_system=True):
        assert tpl.html_output.lstrip().startswith('<!doctype html>'), tpl.name
        assert 'Maven Technosoft' in tpl.html_output, tpl.name
        assert len(tpl.html_output) > 500, tpl.name
