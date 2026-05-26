import pytest
from apps.campaigns.tests.factories import CampaignFactory, CampaignRecipientFactory


@pytest.mark.django_db
def test_campaign_default_status():
    c = CampaignFactory()
    assert c.status == 'draft'


@pytest.mark.django_db
def test_recipient_default_status():
    r = CampaignRecipientFactory()
    assert r.status == 'queued'
    assert r.personalization == {}
