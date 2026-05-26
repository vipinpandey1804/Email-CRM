import factory
from factory.django import DjangoModelFactory
from apps.templates_app.models import EmailTemplate
from apps.organizations_app.tests.factories import OrganizationFactory
from apps.accounts.tests.factories import UserFactory


class EmailTemplateFactory(DjangoModelFactory):
    class Meta:
        model = EmailTemplate

    organization = factory.SubFactory(OrganizationFactory)
    name = factory.Sequence(lambda n: f'Template {n}')
    category = 'promo'
    created_by = factory.SubFactory(UserFactory)
