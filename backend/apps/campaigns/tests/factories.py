import factory
from factory.django import DjangoModelFactory
from apps.campaigns.models import Campaign, CampaignRecipient
from apps.organizations_app.tests.factories import OrganizationFactory
from apps.accounts.tests.factories import UserFactory


class CampaignFactory(DjangoModelFactory):
    class Meta:
        model = Campaign

    organization = factory.SubFactory(OrganizationFactory)
    name = factory.Sequence(lambda n: f'Campaign {n}')
    created_by = factory.SubFactory(UserFactory)


class CampaignRecipientFactory(DjangoModelFactory):
    class Meta:
        model = CampaignRecipient

    campaign = factory.SubFactory(CampaignFactory)
    email = factory.Sequence(lambda n: f'recipient{n}@example.com')
    name = factory.Faker('name')
