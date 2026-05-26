import factory
from factory.django import DjangoModelFactory
from organizations.models import Organization, OrganizationUser
from apps.accounts.tests.factories import UserFactory
from apps.organizations_app.models import OrganizationProfile, OrganizationUserProfile


class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = Organization

    name = factory.Sequence(lambda n: f'Org {n}')
    slug = factory.Sequence(lambda n: f'org-{n}')
    is_active = True


class OrgProfileFactory(DjangoModelFactory):
    class Meta:
        model = OrganizationProfile

    organization = factory.SubFactory(OrganizationFactory)
    plan = 'internal'
    brand_colors = factory.LazyFunction(dict)


class OrganizationUserFactory(DjangoModelFactory):
    class Meta:
        model = OrganizationUser

    organization = factory.SubFactory(OrganizationFactory)
    user = factory.SubFactory(UserFactory)
    is_admin = False


class OrgUserProfileFactory(DjangoModelFactory):
    class Meta:
        model = OrganizationUserProfile

    org_user = factory.SubFactory(OrganizationUserFactory)
    role = 'editor'
