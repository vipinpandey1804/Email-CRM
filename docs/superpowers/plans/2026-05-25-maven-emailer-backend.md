# Maven Technosoft Emailer — Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the complete Django backend for the Maven Technosoft Enterprise Emailer — async REST API, multi-tenant auth, email template storage, campaign management, SMTP dispatch via Django-Q2, and 4 LangGraph AI agents streamed over SSE.

**Architecture:** Django 6.0 + Django Ninja provides async REST; django-organizations (OneToOne extension) handles multi-tenancy; simplejwt handles JWT; google-auth verifies Google ID tokens; LangGraph StateGraph agents stream via Django async SSE; Django-Q2 uses PostgreSQL as broker for email dispatch and scheduling.

**Tech Stack:** Python 3.12, Django 6.0, django-ninja 1.3, djangorestframework-simplejwt 5.x, django-allauth, django-organizations 2.x, django-q2, django-fernet-fields, LangGraph 0.2, langchain-openai 0.2, google-auth, psycopg 3.x, pytest-django, factory-boy

---

## File Map

```
backend/
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── development.py
│   ├── urls.py
│   └── asgi.py
├── apps/
│   ├── accounts/
│   │   ├── models.py        # Custom User (AbstractBaseUser + email login)
│   │   ├── api.py           # /auth/ router: token, refresh, google, logout, me
│   │   ├── schemas.py       # LoginIn, TokenOut, MeOut
│   │   ├── auth.py          # JWTAuth HttpBearer class
│   │   └── tests/
│   │       ├── factories.py
│   │       ├── test_models.py
│   │       └── test_api.py
│   ├── organizations_app/
│   │   ├── models.py        # OrganizationProfile, OrganizationUserProfile
│   │   ├── api.py           # /orgs/ router
│   │   ├── schemas.py
│   │   └── tests/
│   │       ├── factories.py
│   │       └── test_api.py
│   ├── templates_app/
│   │   ├── models.py        # EmailTemplate
│   │   ├── api.py           # /templates/ router
│   │   ├── schemas.py
│   │   └── tests/
│   │       ├── factories.py
│   │       └── test_api.py
│   ├── campaigns/
│   │   ├── models.py        # Campaign, CampaignRecipient
│   │   ├── api.py           # /campaigns/ router
│   │   ├── schemas.py
│   │   ├── services.py      # CSV parse, personalization render
│   │   ├── tasks.py         # Django-Q2: dispatch_campaign
│   │   └── tests/
│   │       ├── factories.py
│   │       └── test_api.py
│   ├── ai_features/
│   │   ├── models.py        # AIJob
│   │   ├── api.py           # /ai/ router with SSE
│   │   ├── schemas.py
│   │   ├── agents/
│   │   │   ├── base.py      # get_llm() provider factory
│   │   │   ├── subject_line.py
│   │   │   ├── copy_optimizer.py
│   │   │   ├── spam_checker.py
│   │   │   └── cta_optimizer.py
│   │   └── tests/
│   │       └── test_agents.py
│   └── settings_app/
│       ├── models.py        # SMTPConfig
│       ├── api.py           # /settings/ router
│       ├── schemas.py
│       ├── services.py      # SMTP test connection
│       └── tests/
│           └── test_api.py
├── core/
│   ├── middleware.py        # OrgScopedMiddleware
│   ├── permissions.py       # require_role decorator
│   └── pagination.py
├── conftest.py
├── pytest.ini
├── manage.py
└── requirements.txt
```

---

## Task 1: Scaffold Django Project

**Files:**
- Create: `backend/` (all structure above)
- Create: `backend/requirements.txt`
- Create: `backend/config/settings/base.py`
- Create: `backend/config/settings/development.py`
- Create: `backend/config/urls.py`
- Create: `backend/pytest.ini`
- Create: `backend/conftest.py`

- [ ] **Step 1: Create project skeleton and virtualenv**

```bash
cd "E:/career247/New folder (2)/project 1"
python -m venv .venv
# Windows activation:
.venv\Scripts\activate
pip install django==6.0.*
django-admin startproject config backend
```

- [ ] **Step 2: Create all Django app directories**

```bash
cd backend
mkdir -p apps/accounts/tests
mkdir -p apps/organizations_app/tests
mkdir -p apps/templates_app/tests
mkdir -p apps/campaigns/tests
mkdir -p apps/ai_features/agents
mkdir -p apps/ai_features/tests
mkdir -p apps/settings_app/tests
mkdir -p core
```

Create `__init__.py` in each:
```bash
touch apps/__init__.py
touch apps/accounts/__init__.py apps/accounts/tests/__init__.py
touch apps/organizations_app/__init__.py apps/organizations_app/tests/__init__.py
touch apps/templates_app/__init__.py apps/templates_app/tests/__init__.py
touch apps/campaigns/__init__.py apps/campaigns/tests/__init__.py
touch apps/ai_features/__init__.py apps/ai_features/agents/__init__.py apps/ai_features/tests/__init__.py
touch apps/settings_app/__init__.py apps/settings_app/tests/__init__.py
touch core/__init__.py
```

- [ ] **Step 3: Create `backend/requirements.txt`**

```text
django>=6.0,<7.0
django-ninja==1.3.*
djangorestframework-simplejwt==5.*
django-allauth[google]==65.*
django-organizations==2.*
django-q2==1.7.*
django-fernet-fields==0.9.*
django-cors-headers==4.*
psycopg[binary]==3.*
google-auth==2.*
langgraph==0.2.*
langchain-openai==0.2.*
langchain-core==0.3.*
pandas==2.*
python-dotenv==1.*

# dev/test
pytest-django==4.*
pytest-asyncio==0.24.*
factory-boy==3.*
```

- [ ] **Step 4: Install requirements**

```bash
pip install -r requirements.txt
```

Expected: all packages install without errors.

- [ ] **Step 5: Create `backend/config/settings/base.py`**

```python
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # Third-party
    'corsheaders',
    'organizations',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django_q',
    # Local
    'apps.accounts',
    'apps.organizations_app',
    'apps.templates_app',
    'apps.campaigns',
    'apps.ai_features',
    'apps.settings_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'maven_emailer'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

# django-allauth
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
            'secret': os.environ.get('GOOGLE_CLIENT_SECRET', ''),
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

# simplejwt
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}

# Django-Q2
Q_CLUSTER = {
    'name': 'maven_emailer',
    'workers': 2,
    'timeout': 120,
    'retry': 180,
    'queue_limit': 50,
    'bulk': 10,
    'orm': 'default',
}

# CORS
CORS_ALLOWED_ORIGINS = []
CORS_ALLOW_CREDENTIALS = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'

# Fernet encryption key for SMTPConfig.password
FERNET_KEYS = [os.environ.get('FERNET_KEY', 'RqgUkzXLpMxb46dGLkGJZ6jRv6OeD4pxYF1BI3RFfJQ=')]
```

- [ ] **Step 6: Create `backend/config/settings/development.py`**

```python
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

DATABASES['default']['NAME'] = os.environ.get('DB_NAME', 'maven_emailer_dev')
```

- [ ] **Step 7: Update `backend/config/settings/__init__.py`**

```python
# empty — settings module selected via DJANGO_SETTINGS_MODULE env var
```

- [ ] **Step 8: Update `backend/config/urls.py`**

```python
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from apps.accounts.api import router as auth_router
from apps.organizations_app.api import router as orgs_router
from apps.templates_app.api import router as templates_router
from apps.campaigns.api import router as campaigns_router
from apps.ai_features.api import router as ai_router
from apps.settings_app.api import router as settings_router

api = NinjaAPI(title='Maven Emailer API', version='1.0.0', docs_url='/api/docs')

api.add_router('/auth/', auth_router, tags=['Auth'])
api.add_router('/orgs/', orgs_router, tags=['Organizations'])
api.add_router('/templates/', templates_router, tags=['Templates'])
api.add_router('/campaigns/', campaigns_router, tags=['Campaigns'])
api.add_router('/ai/', ai_router, tags=['AI'])
api.add_router('/settings/', settings_router, tags=['Settings'])

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api.urls),
]
```

- [ ] **Step 9: Create `backend/pytest.ini`**

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.development
django_db_setup_show_pdb = false
asyncio_mode = auto
```

- [ ] **Step 10: Create `backend/conftest.py`**

```python
import pytest
from django.test import Client


@pytest.fixture
def client():
    return Client()
```

- [ ] **Step 11: Create `backend/.env` (gitignored)**

```bash
cat > backend/.env << 'EOF'
SECRET_KEY=dev-only-secret-key-change-in-prod
DB_NAME=maven_emailer_dev
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
OPENAI_API_KEY=your-openai-key
FERNET_KEY=RqgUkzXLpMxb46dGLkGJZ6jRv6OeD4pxYF1BI3RFfJQ=
EOF
```

- [ ] **Step 12: Add `.env` to `.gitignore`**

```bash
cd "E:/career247/New folder (2)/project 1"
cat >> .gitignore << 'EOF'
.venv/
__pycache__/
*.pyc
*.pyo
.env
*.env
*.sqlite3
.superpowers/
node_modules/
dist/
EOF
```

- [ ] **Step 13: Commit**

```bash
cd "E:/career247/New folder (2)/project 1"
git add backend/ .gitignore
git commit -m "chore: scaffold Django project structure and settings"
```

---

## Task 2: Custom User Model

**Files:**
- Create: `backend/apps/accounts/models.py`
- Create: `backend/apps/accounts/admin.py`
- Create: `backend/apps/accounts/apps.py`
- Create: `backend/apps/accounts/tests/test_models.py`
- Create: `backend/apps/accounts/tests/factories.py`

- [ ] **Step 1: Write failing test**

```python
# backend/apps/accounts/tests/test_models.py
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
```

- [ ] **Step 2: Run test — expect failure**

```bash
cd backend
python -m pytest apps/accounts/tests/test_models.py -v
```

Expected: `ModuleNotFoundError` or `ImportError` — factories not defined yet.

- [ ] **Step 3: Create `backend/apps/accounts/models.py`**

```python
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email: str, password: str = None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200, blank=True, default='')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self) -> str:
        return self.email
```

- [ ] **Step 4: Create `backend/apps/accounts/apps.py`**

```python
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'apps.accounts'
    label = 'accounts'
    default_auto_field = 'django.db.models.UUIDField'
```

- [ ] **Step 5: Create `backend/apps/accounts/tests/factories.py`**

```python
import factory
from factory.django import DjangoModelFactory
from apps.accounts.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f'user{n}@example.com')
    full_name = factory.Faker('name')
    is_active = True
    is_staff = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop('password', 'testpass123')
        user = super()._create(model_class, *args, **kwargs)
        user.set_password(password)
        user.save()
        return user
```

- [ ] **Step 6: Update `backend/apps/accounts/__init__.py`**

```python
default_app_config = 'apps.accounts.apps.AccountsConfig'
```

- [ ] **Step 7: Create and run migrations**

```bash
cd backend
python manage.py makemigrations accounts
python manage.py migrate
```

Expected: migrations created and applied without errors.

- [ ] **Step 8: Run tests — expect pass**

```bash
python -m pytest apps/accounts/tests/test_models.py -v
```

Expected: 3 tests PASSED.

- [ ] **Step 9: Commit**

```bash
git add backend/apps/accounts/ backend/config/
git commit -m "feat: custom User model with email-as-username"
```

---

## Task 3: django-organizations Extension

**Files:**
- Create: `backend/apps/organizations_app/models.py`
- Create: `backend/apps/organizations_app/apps.py`
- Create: `backend/apps/organizations_app/tests/factories.py`
- Create: `backend/apps/organizations_app/tests/test_models.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/apps/organizations_app/tests/test_models.py
import pytest
from organizations.models import Organization, OrganizationUser
from apps.organizations_app.tests.factories import OrgProfileFactory, OrgUserProfileFactory


@pytest.mark.django_db
def test_org_profile_created_with_org():
    profile = OrgProfileFactory()
    assert profile.organization is not None
    assert profile.plan == 'internal'
    assert profile.brand_colors == {}


@pytest.mark.django_db
def test_org_user_profile_has_role():
    profile = OrgUserProfileFactory()
    assert profile.role in ('admin', 'editor', 'viewer')


@pytest.mark.django_db
def test_org_profile_str():
    profile = OrgProfileFactory(organization__name='Acme Corp')
    assert 'Acme Corp' in str(profile)
```

- [ ] **Step 2: Run — expect failure**

```bash
python -m pytest apps/organizations_app/tests/test_models.py -v
```

Expected: `ImportError` — factories not defined.

- [ ] **Step 3: Create `backend/apps/organizations_app/models.py`**

```python
import uuid
from django.db import models
from django.conf import settings
from organizations.models import Organization, OrganizationUser
from django_fernet_fields import EncryptedTextField


class OrganizationProfile(models.Model):
    """Extends django-organizations' Organization with custom fields."""
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True,
    )
    logo_url = models.TextField(blank=True, default='')
    brand_colors = models.JSONField(default=dict, blank=True)
    plan = models.CharField(
        max_length=20,
        choices=[('internal', 'Internal'), ('saas', 'SaaS')],
        default='internal',
    )
    openai_api_key = EncryptedTextField(blank=True, default='')

    class Meta:
        verbose_name = 'Organization Profile'
        verbose_name_plural = 'Organization Profiles'

    def __str__(self) -> str:
        return f'Profile for {self.organization.name}'


class OrganizationUserProfile(models.Model):
    """Extends django-organizations' OrganizationUser with role + avatar."""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    ]
    org_user = models.OneToOneField(
        OrganizationUser,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True,
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='editor')
    avatar_url = models.TextField(blank=True, default='')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Organization User Profile'
        verbose_name_plural = 'Organization User Profiles'

    def __str__(self) -> str:
        return f'{self.org_user.user.email} @ {self.org_user.organization.name} ({self.role})'
```

- [ ] **Step 4: Create `backend/apps/organizations_app/tests/factories.py`**

```python
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
```

- [ ] **Step 5: Create `backend/apps/organizations_app/apps.py`**

```python
from django.apps import AppConfig


class OrganizationsAppConfig(AppConfig):
    name = 'apps.organizations_app'
    label = 'organizations_app'
```

- [ ] **Step 6: Run migrations and tests**

```bash
python manage.py makemigrations organizations_app
python manage.py migrate
python -m pytest apps/organizations_app/tests/test_models.py -v
```

Expected: 3 tests PASSED.

- [ ] **Step 7: Commit**

```bash
git add backend/apps/organizations_app/
git commit -m "feat: OrganizationProfile and OrganizationUserProfile extensions"
```

---

## Task 4: Core Models — EmailTemplate, Campaign, CampaignRecipient, SMTPConfig, AIJob

**Files:**
- Create: `backend/apps/templates_app/models.py`
- Create: `backend/apps/campaigns/models.py`
- Create: `backend/apps/settings_app/models.py`
- Create: `backend/apps/ai_features/models.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/apps/templates_app/tests/test_models.py
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
```

```python
# backend/apps/campaigns/tests/test_models.py
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
```

- [ ] **Step 2: Run — expect failure**

```bash
python -m pytest apps/templates_app/tests/ apps/campaigns/tests/ -v
```

Expected: `ImportError`.

- [ ] **Step 3: Create `backend/apps/templates_app/models.py`**

```python
import uuid
from django.db import models
from django.conf import settings
from organizations.models import Organization


class EmailTemplate(models.Model):
    CATEGORY_CHOICES = [
        ('promo', 'Promotion'),
        ('newsletter', 'Newsletter'),
        ('announcement', 'Announcement'),
        ('webinar', 'Webinar'),
        ('onboarding', 'Onboarding'),
        ('outreach', 'Outreach'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='email_templates'
    )
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='promo')
    thumbnail_url = models.TextField(blank=True, default='')
    gjs_components = models.JSONField(default=dict, blank=True)
    gjs_styles = models.JSONField(default=dict, blank=True)
    mjml_source = models.TextField(blank=True, default='')
    html_output = models.TextField(blank=True, default='')
    is_system = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_templates',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self) -> str:
        return self.name
```

- [ ] **Step 4: Create `backend/apps/campaigns/models.py`**

```python
import uuid
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from organizations.models import Organization
from apps.templates_app.models import EmailTemplate


class Campaign(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='campaigns'
    )
    template = models.ForeignKey(
        EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='campaigns'
    )
    name = models.CharField(max_length=200)
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    subject_line = models.CharField(max_length=300, blank=True, default='')
    preview_text = models.CharField(max_length=200, blank=True, default='')
    from_name = models.CharField(max_length=100, blank=True, default='')
    from_email = models.EmailField(blank=True, default='')
    reply_to = models.EmailField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_campaigns',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self) -> str:
        return self.name


class CampaignRecipient(models.Model):
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='recipients')
    email = models.EmailField()
    name = models.CharField(max_length=200, blank=True, default='')
    personalization = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, default='')

    class Meta:
        unique_together = [('campaign', 'email')]

    def __str__(self) -> str:
        return f'{self.email} -> {self.campaign.name}'
```

- [ ] **Step 5: Create `backend/apps/settings_app/models.py`**

```python
from django.db import models
from organizations.models import Organization
from django_fernet_fields import EncryptedTextField


class SMTPConfig(models.Model):
    organization = models.OneToOneField(
        Organization, on_delete=models.CASCADE, related_name='smtp_config', primary_key=True
    )
    host = models.CharField(max_length=255, blank=True, default='')
    port = models.IntegerField(default=587)
    username = models.CharField(max_length=255, blank=True, default='')
    password = EncryptedTextField(blank=True, default='')
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'SMTP config for {self.organization.name}'
```

- [ ] **Step 6: Create `backend/apps/ai_features/models.py`**

```python
import uuid
from django.db import models
from django.conf import settings
from organizations.models import Organization


class AIJob(models.Model):
    JOB_TYPE_CHOICES = [
        ('subject_lines', 'Subject Lines'),
        ('copy_optimize', 'Copy Optimize'),
        ('spam_check', 'Spam Check'),
        ('cta_suggest', 'CTA Suggest'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='ai_jobs')
    campaign = models.ForeignKey(
        'campaigns.Campaign', on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_jobs'
    )
    job_type = models.CharField(max_length=30, choices=JOB_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='ai_jobs'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.job_type} ({self.status})'
```

- [ ] **Step 7: Create all apps.py files**

```python
# backend/apps/templates_app/apps.py
from django.apps import AppConfig
class TemplatesAppConfig(AppConfig):
    name = 'apps.templates_app'
    label = 'templates_app'
```

```python
# backend/apps/campaigns/apps.py
from django.apps import AppConfig
class CampaignsConfig(AppConfig):
    name = 'apps.campaigns'
    label = 'campaigns'
```

```python
# backend/apps/settings_app/apps.py
from django.apps import AppConfig
class SettingsAppConfig(AppConfig):
    name = 'apps.settings_app'
    label = 'settings_app'
```

```python
# backend/apps/ai_features/apps.py
from django.apps import AppConfig
class AiFeaturesConfig(AppConfig):
    name = 'apps.ai_features'
    label = 'ai_features'
```

- [ ] **Step 8: Create factories**

```python
# backend/apps/templates_app/tests/factories.py
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
```

```python
# backend/apps/campaigns/tests/factories.py
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
```

- [ ] **Step 9: Run migrations and tests**

```bash
python manage.py makemigrations templates_app campaigns settings_app ai_features
python manage.py migrate
python -m pytest apps/templates_app/tests/ apps/campaigns/tests/ -v
```

Expected: all tests PASSED.

- [ ] **Step 10: Commit**

```bash
git add backend/apps/
git commit -m "feat: EmailTemplate, Campaign, CampaignRecipient, SMTPConfig, AIJob models"
```

---

## Task 5: JWT Auth + JWTAuth class

**Files:**
- Create: `backend/apps/accounts/auth.py`
- Create: `backend/apps/accounts/schemas.py`
- Create: `backend/apps/accounts/api.py`
- Modify: `backend/apps/accounts/tests/test_api.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/apps/accounts/tests/test_api.py
import pytest
from ninja.testing import TestClient
from apps.accounts.api import router
from apps.accounts.tests.factories import UserFactory

client = TestClient(router)


@pytest.mark.django_db
def test_login_returns_jwt_tokens():
    user = UserFactory(email='login@test.com', password='pass1234')
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
def test_me_returns_user_info(mocker):
    user = UserFactory(email='me@test.com')
    # get valid token
    resp = client.post('/token', json={'email': 'me@test.com', 'password': 'testpass123'})
    token = resp.json()['access']
    resp2 = client.get('/me', headers={'Authorization': f'Bearer {token}'})
    assert resp2.status_code == 200
    assert resp2.json()['email'] == 'me@test.com'
```

- [ ] **Step 2: Run — expect failure**

```bash
python -m pytest apps/accounts/tests/test_api.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Create `backend/apps/accounts/auth.py`**

```python
from ninja.security import HttpBearer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class JWTAuth(HttpBearer):
    def authenticate(self, request, token: str):
        try:
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
            if user and user.is_active:
                return user
            return None
        except (InvalidToken, TokenError):
            return None
```

- [ ] **Step 4: Create `backend/apps/accounts/schemas.py`**

```python
from ninja import Schema
from uuid import UUID


class LoginIn(Schema):
    email: str
    password: str


class TokenOut(Schema):
    access: str
    refresh: str


class GoogleAuthIn(Schema):
    id_token: str


class MeOut(Schema):
    id: UUID
    email: str
    full_name: str
    is_staff: bool
```

- [ ] **Step 5: Create `backend/apps/accounts/api.py`**

```python
from ninja import Router
from ninja.errors import HttpError
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from django.conf import settings

from apps.accounts.models import User
from apps.accounts.auth import JWTAuth
from apps.accounts.schemas import LoginIn, TokenOut, GoogleAuthIn, MeOut

router = Router()


@router.post('/token', response=TokenOut, auth=None)
def login(request, payload: LoginIn):
    user = authenticate(request, username=payload.email, password=payload.password)
    if not user:
        raise HttpError(401, 'Invalid email or password')
    refresh = RefreshToken.for_user(user)
    return TokenOut(access=str(refresh.access_token), refresh=str(refresh))


@router.post('/token/refresh', response=TokenOut, auth=None)
def refresh_token(request, payload: dict):
    try:
        refresh = RefreshToken(payload.get('refresh', ''))
        return TokenOut(access=str(refresh.access_token), refresh=str(refresh))
    except TokenError as e:
        raise HttpError(401, str(e))


@router.post('/google', response=TokenOut, auth=None)
def google_auth(request, payload: GoogleAuthIn):
    try:
        idinfo = google_id_token.verify_oauth2_token(
            payload.id_token,
            google_requests.Request(),
            settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id'],
        )
    except ValueError:
        raise HttpError(401, 'Invalid Google token')

    email = idinfo.get('email')
    full_name = idinfo.get('name', '')
    if not email:
        raise HttpError(400, 'Google account has no email')

    user, _ = User.objects.get_or_create(
        email=email,
        defaults={'full_name': full_name, 'is_active': True},
    )
    refresh = RefreshToken.for_user(user)
    return TokenOut(access=str(refresh.access_token), refresh=str(refresh))


@router.post('/logout', auth=JWTAuth())
def logout(request, payload: dict):
    try:
        token = RefreshToken(payload.get('refresh', ''))
        token.blacklist()
    except TokenError:
        pass
    return {'detail': 'Logged out'}


@router.get('/me', response=MeOut, auth=JWTAuth())
def me(request):
    user = request.auth
    return MeOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_staff=user.is_staff,
    )
```

- [ ] **Step 6: Add simplejwt to INSTALLED_APPS and enable token blacklist**

Add to `backend/config/settings/base.py` INSTALLED_APPS:
```python
'rest_framework_simplejwt',
'rest_framework_simplejwt.token_blacklist',
```

Run migrations:
```bash
python manage.py migrate
```

- [ ] **Step 7: Run tests**

```bash
python -m pytest apps/accounts/tests/test_api.py -v
```

Expected: 4 tests PASSED.

- [ ] **Step 8: Commit**

```bash
git add backend/apps/accounts/ backend/config/
git commit -m "feat: JWT auth endpoints (login, refresh, google, logout, me)"
```

---

## Task 6: Org-Scoped Middleware + Permissions

**Files:**
- Create: `backend/core/middleware.py`
- Create: `backend/core/permissions.py`

- [ ] **Step 1: Write failing test**

```python
# backend/apps/organizations_app/tests/test_api.py
import pytest
from ninja.testing import TestClient
from apps.organizations_app.api import router
from apps.accounts.tests.factories import UserFactory
from apps.organizations_app.tests.factories import OrganizationFactory, OrganizationUserFactory, OrgProfileFactory

client = TestClient(router)


def auth_headers(user):
    from rest_framework_simplejwt.tokens import RefreshToken
    token = str(RefreshToken.for_user(user).access_token)
    return {'Authorization': f'Bearer {token}'}


@pytest.mark.django_db
def test_list_orgs_returns_only_user_orgs():
    user = UserFactory()
    org1 = OrganizationFactory(name='Org Alpha')
    org2 = OrganizationFactory(name='Org Beta')
    OrgProfileFactory(organization=org1)
    OrganizationUserFactory(organization=org1, user=user)
    # user is NOT in org2
    resp = client.get('/', headers=auth_headers(user))
    assert resp.status_code == 200
    names = [o['name'] for o in resp.json()]
    assert 'Org Alpha' in names
    assert 'Org Beta' not in names
```

- [ ] **Step 2: Run — expect failure**

```bash
python -m pytest apps/organizations_app/tests/test_api.py::test_list_orgs_returns_only_user_orgs -v
```

- [ ] **Step 3: Create `backend/core/permissions.py`**

```python
from functools import wraps
from ninja.errors import HttpError


def require_role(*roles):
    """Decorator for Django Ninja endpoints requiring specific org roles."""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            user = request.auth
            if not user:
                raise HttpError(401, 'Authentication required')
            # Get org from path param or request
            org_slug = kwargs.get('slug') or getattr(request, '_org_slug', None)
            if org_slug:
                from organizations.models import OrganizationUser
                try:
                    ou = OrganizationUser.objects.get(
                        organization__slug=org_slug, user=user
                    )
                    user_role = getattr(ou, 'profile', None)
                    role = user_role.role if user_role else ('admin' if ou.is_admin else 'viewer')
                    if role not in roles and 'admin' not in roles:
                        raise HttpError(403, 'Insufficient permissions')
                    if roles and role not in roles:
                        raise HttpError(403, 'Insufficient permissions')
                except OrganizationUser.DoesNotExist:
                    raise HttpError(403, 'Not a member of this organization')
            return func(request, *args, **kwargs)
        return wrapper
    return decorator
```

- [ ] **Step 4: Create `backend/apps/organizations_app/schemas.py`**

```python
from ninja import Schema
from typing import Optional


class OrgOut(Schema):
    id: int
    name: str
    slug: str
    is_active: bool
    plan: Optional[str] = 'internal'
    logo_url: Optional[str] = ''


class OrgUpdateIn(Schema):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    brand_colors: Optional[dict] = None


class OrgUserOut(Schema):
    user_email: str
    user_full_name: str
    role: str
    is_admin: bool


class InviteIn(Schema):
    email: str
    role: str = 'editor'
```

- [ ] **Step 5: Create `backend/apps/organizations_app/api.py`**

```python
from ninja import Router
from ninja.errors import HttpError
from typing import List
from organizations.models import Organization, OrganizationUser
from apps.accounts.auth import JWTAuth
from apps.organizations_app.models import OrganizationProfile, OrganizationUserProfile
from apps.organizations_app.schemas import OrgOut, OrgUpdateIn, OrgUserOut, InviteIn

router = Router(auth=JWTAuth())


def _org_to_out(org: Organization) -> OrgOut:
    profile = getattr(org, 'profile', None)
    return OrgOut(
        id=org.id,
        name=org.name,
        slug=org.slug,
        is_active=org.is_active,
        plan=profile.plan if profile else 'internal',
        logo_url=profile.logo_url if profile else '',
    )


@router.get('/', response=List[OrgOut])
def list_orgs(request):
    user = request.auth
    org_ids = OrganizationUser.objects.filter(user=user).values_list('organization_id', flat=True)
    orgs = Organization.objects.filter(id__in=org_ids, is_active=True)
    return [_org_to_out(o) for o in orgs]


@router.get('/{slug}', response=OrgOut)
def get_org(request, slug: str):
    user = request.auth
    try:
        OrganizationUser.objects.get(organization__slug=slug, user=user)
    except OrganizationUser.DoesNotExist:
        raise HttpError(404, 'Organization not found')
    org = Organization.objects.get(slug=slug)
    return _org_to_out(org)


@router.patch('/{slug}', response=OrgOut)
def update_org(request, slug: str, payload: OrgUpdateIn):
    user = request.auth
    try:
        ou = OrganizationUser.objects.get(organization__slug=slug, user=user)
    except OrganizationUser.DoesNotExist:
        raise HttpError(404, 'Organization not found')
    if not ou.is_admin:
        raise HttpError(403, 'Admin access required')
    org = ou.organization
    if payload.name:
        org.name = payload.name
        org.save()
    profile, _ = OrganizationProfile.objects.get_or_create(organization=org)
    if payload.logo_url is not None:
        profile.logo_url = payload.logo_url
    if payload.brand_colors is not None:
        profile.brand_colors = payload.brand_colors
    profile.save()
    return _org_to_out(org)


@router.get('/{slug}/users', response=List[OrgUserOut])
def list_org_users(request, slug: str):
    user = request.auth
    try:
        OrganizationUser.objects.get(organization__slug=slug, user=user)
    except OrganizationUser.DoesNotExist:
        raise HttpError(404, 'Organization not found')
    org_users = OrganizationUser.objects.filter(
        organization__slug=slug
    ).select_related('user', 'profile')
    result = []
    for ou in org_users:
        profile = getattr(ou, 'profile', None)
        result.append(OrgUserOut(
            user_email=ou.user.email,
            user_full_name=ou.user.full_name,
            role=profile.role if profile else ('admin' if ou.is_admin else 'viewer'),
            is_admin=ou.is_admin,
        ))
    return result


@router.post('/{slug}/invite')
def invite_user(request, slug: str, payload: InviteIn):
    user = request.auth
    try:
        ou = OrganizationUser.objects.get(organization__slug=slug, user=user)
    except OrganizationUser.DoesNotExist:
        raise HttpError(404, 'Organization not found')
    if not ou.is_admin:
        raise HttpError(403, 'Admin access required')
    from apps.accounts.models import User as AppUser
    invited_user, created = AppUser.objects.get_or_create(
        email=payload.email,
        defaults={'is_active': True}
    )
    new_ou, ou_created = OrganizationUser.objects.get_or_create(
        organization=ou.organization,
        user=invited_user,
        defaults={'is_admin': payload.role == 'admin'}
    )
    if ou_created:
        OrganizationUserProfile.objects.create(org_user=new_ou, role=payload.role)
    return {'detail': f'User {payload.email} invited', 'created': ou_created}


@router.delete('/{slug}/users/{user_id}')
def remove_user(request, slug: str, user_id: int):
    user = request.auth
    try:
        ou = OrganizationUser.objects.get(organization__slug=slug, user=user)
    except OrganizationUser.DoesNotExist:
        raise HttpError(404, 'Organization not found')
    if not ou.is_admin:
        raise HttpError(403, 'Admin access required')
    OrganizationUser.objects.filter(organization__slug=slug, user_id=user_id).delete()
    return {'detail': 'User removed'}
```

- [ ] **Step 6: Run tests**

```bash
python -m pytest apps/organizations_app/tests/ -v
```

Expected: PASSED.

- [ ] **Step 7: Commit**

```bash
git add backend/core/ backend/apps/organizations_app/
git commit -m "feat: organizations API with role-based access"
```

---

## Task 7: Templates API

**Files:**
- Create: `backend/apps/templates_app/schemas.py`
- Create: `backend/apps/templates_app/api.py`
- Create: `backend/apps/templates_app/tests/test_api.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/apps/templates_app/tests/test_api.py
import pytest
from ninja.testing import TestClient
from apps.templates_app.api import router
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
    my_template = EmailTemplateFactory(organization=org, name='Mine')
    other_template = EmailTemplateFactory(organization=other_org, name='Other')
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
    data = resp.json()
    assert data['gjs_components'] == {'type': 'mj-body'}
```

- [ ] **Step 2: Run — expect failure**

```bash
python -m pytest apps/templates_app/tests/test_api.py -v
```

- [ ] **Step 3: Create `backend/apps/templates_app/schemas.py`**

```python
from ninja import Schema
from typing import Optional
from uuid import UUID
from datetime import datetime


class TemplateCreateIn(Schema):
    name: str
    category: str = 'promo'


class TemplateSaveIn(Schema):
    name: Optional[str] = None
    category: Optional[str] = None
    gjs_components: Optional[dict] = None
    gjs_styles: Optional[dict] = None
    mjml_source: Optional[str] = None
    html_output: Optional[str] = None
    thumbnail_url: Optional[str] = None


class TemplateOut(Schema):
    id: UUID
    name: str
    category: str
    thumbnail_url: str
    is_system: bool
    gjs_components: dict
    gjs_styles: dict
    mjml_source: str
    html_output: str
    updated_at: datetime
```

- [ ] **Step 4: Create `backend/apps/templates_app/api.py`**

```python
from ninja import Router
from ninja.errors import HttpError
from typing import List, Optional
from uuid import UUID
from organizations.models import OrganizationUser
from apps.accounts.auth import JWTAuth
from apps.templates_app.models import EmailTemplate
from apps.templates_app.schemas import TemplateCreateIn, TemplateSaveIn, TemplateOut

router = Router(auth=JWTAuth())


def _get_org_or_403(user, org_slug: str):
    try:
        ou = OrganizationUser.objects.select_related('organization').get(
            organization__slug=org_slug, user=user
        )
        return ou.organization
    except OrganizationUser.DoesNotExist:
        raise HttpError(403, 'Not a member of this organization')


@router.get('/', response=List[TemplateOut])
def list_templates(request, org_slug: str, category: Optional[str] = None, is_system: Optional[bool] = None):
    org = _get_org_or_403(request.auth, org_slug)
    qs = EmailTemplate.objects.filter(organization=org)
    if category:
        qs = qs.filter(category=category)
    if is_system is not None:
        qs = qs.filter(is_system=is_system)
    return [TemplateOut.from_orm(t) for t in qs]


@router.post('/', response=TemplateOut)
def create_template(request, org_slug: str, payload: TemplateCreateIn):
    org = _get_org_or_403(request.auth, org_slug)
    t = EmailTemplate.objects.create(
        organization=org,
        name=payload.name,
        category=payload.category,
        created_by=request.auth,
    )
    return TemplateOut.from_orm(t)


@router.get('/{template_id}', response=TemplateOut)
def get_template(request, org_slug: str, template_id: UUID):
    org = _get_org_or_403(request.auth, org_slug)
    try:
        t = EmailTemplate.objects.get(id=template_id, organization=org)
    except EmailTemplate.DoesNotExist:
        raise HttpError(404, 'Template not found')
    return TemplateOut.from_orm(t)


@router.patch('/{template_id}', response=TemplateOut)
def save_template(request, org_slug: str, template_id: UUID, payload: TemplateSaveIn):
    org = _get_org_or_403(request.auth, org_slug)
    try:
        t = EmailTemplate.objects.get(id=template_id, organization=org)
    except EmailTemplate.DoesNotExist:
        raise HttpError(404, 'Template not found')
    for field, value in payload.dict(exclude_none=True).items():
        setattr(t, field, value)
    t.save()
    return TemplateOut.from_orm(t)


@router.delete('/{template_id}')
def delete_template(request, org_slug: str, template_id: UUID):
    org = _get_org_or_403(request.auth, org_slug)
    try:
        t = EmailTemplate.objects.get(id=template_id, organization=org, is_system=False)
    except EmailTemplate.DoesNotExist:
        raise HttpError(404, 'Template not found or cannot be deleted')
    t.delete()
    return {'detail': 'Deleted'}


@router.post('/{template_id}/duplicate', response=TemplateOut)
def duplicate_template(request, org_slug: str, template_id: UUID):
    org = _get_org_or_403(request.auth, org_slug)
    try:
        t = EmailTemplate.objects.get(id=template_id, organization=org)
    except EmailTemplate.DoesNotExist:
        raise HttpError(404, 'Template not found')
    t.pk = None
    t.id = None
    t.name = f'{t.name} (Copy)'
    t.is_system = False
    t.created_by = request.auth
    t.save()
    return TemplateOut.from_orm(t)
```

- [ ] **Step 5: Run tests**

```bash
python -m pytest apps/templates_app/tests/test_api.py -v
```

Expected: 3 tests PASSED.

- [ ] **Step 6: Commit**

```bash
git add backend/apps/templates_app/
git commit -m "feat: EmailTemplate CRUD API"
```

---

## Task 8: Campaigns API

**Files:**
- Create: `backend/apps/campaigns/schemas.py`
- Create: `backend/apps/campaigns/api.py`
- Create: `backend/apps/campaigns/services.py`
- Create: `backend/apps/campaigns/tests/test_api.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/apps/campaigns/tests/test_api.py
import pytest
from ninja.testing import TestClient
from apps.campaigns.api import router
from apps.campaigns.tests.factories import CampaignFactory, CampaignRecipientFactory
from apps.organizations_app.tests.factories import OrganizationFactory, OrganizationUserFactory
from apps.accounts.tests.factories import UserFactory
from rest_framework_simplejwt.tokens import RefreshToken

client = TestClient(router)


def auth_headers(user):
    token = str(RefreshToken.for_user(user).access_token)
    return {'Authorization': f'Bearer {token}'}


@pytest.mark.django_db
def test_create_campaign():
    user = UserFactory()
    org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user)
    resp = client.post(
        f'/?org_slug={org.slug}',
        json={'name': 'Test Campaign', 'subject_line': 'Hello World'},
        headers=auth_headers(user),
    )
    assert resp.status_code == 200
    assert resp.json()['status'] == 'draft'


@pytest.mark.django_db
def test_list_campaigns_scoped_to_org():
    user = UserFactory()
    org = OrganizationFactory()
    other_org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user)
    c1 = CampaignFactory(organization=org, name='Mine')
    c2 = CampaignFactory(organization=other_org, name='Other')
    resp = client.get(f'/?org_slug={org.slug}', headers=auth_headers(user))
    assert resp.status_code == 200
    names = [c['name'] for c in resp.json()]
    assert 'Mine' in names
    assert 'Other' not in names


@pytest.mark.django_db
def test_cannot_delete_sent_campaign():
    user = UserFactory()
    org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user)
    c = CampaignFactory(organization=org, status='sent')
    resp = client.delete(f'/{c.id}?org_slug={org.slug}', headers=auth_headers(user))
    assert resp.status_code == 400
```

- [ ] **Step 2: Run — expect failure**

```bash
python -m pytest apps/campaigns/tests/test_api.py -v
```

- [ ] **Step 3: Create `backend/apps/campaigns/schemas.py`**

```python
from ninja import Schema
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class CampaignCreateIn(Schema):
    name: str
    subject_line: str = ''
    preview_text: str = ''
    from_name: str = ''
    from_email: str = ''
    reply_to: str = ''
    tags: List[str] = []
    template_id: Optional[UUID] = None


class CampaignUpdateIn(Schema):
    name: Optional[str] = None
    subject_line: Optional[str] = None
    preview_text: Optional[str] = None
    from_name: Optional[str] = None
    from_email: Optional[str] = None
    reply_to: Optional[str] = None
    tags: Optional[List[str]] = None
    template_id: Optional[UUID] = None


class CampaignOut(Schema):
    id: UUID
    name: str
    subject_line: str
    preview_text: str
    from_name: str
    from_email: str
    reply_to: str
    tags: List[str]
    status: str
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    created_at: datetime


class ScheduleIn(Schema):
    scheduled_at: datetime


class RecipientOut(Schema):
    id: UUID
    email: str
    name: str
    status: str
    sent_at: Optional[datetime] = None
    error_message: str
```

- [ ] **Step 4: Create `backend/apps/campaigns/services.py`**

```python
import csv
import io
from typing import List, Dict


def parse_recipient_csv(csv_content: str) -> List[Dict]:
    """
    Parse CSV with columns: email, name, and any personalization columns.
    Returns list of dicts with 'email', 'name', and 'personalization' keys.
    """
    reader = csv.DictReader(io.StringIO(csv_content))
    recipients = []
    standard_fields = {'email', 'name'}
    for row in reader:
        row = {k.strip().lower(): v.strip() for k, v in row.items()}
        if not row.get('email'):
            continue
        personalization = {k: v for k, v in row.items() if k not in standard_fields}
        recipients.append({
            'email': row['email'],
            'name': row.get('name', ''),
            'personalization': personalization,
        })
    return recipients


def render_personalized_html(html: str, personalization: Dict) -> str:
    """Replace {{key}} placeholders with personalization values."""
    for key, value in personalization.items():
        html = html.replace(f'{{{{{key}}}}}', str(value))
    return html
```

- [ ] **Step 5: Create `backend/apps/campaigns/api.py`**

```python
from ninja import Router, File
from ninja.errors import HttpError
from ninja.files import UploadedFile
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from organizations.models import OrganizationUser
from apps.accounts.auth import JWTAuth
from apps.campaigns.models import Campaign, CampaignRecipient
from apps.campaigns.schemas import (
    CampaignCreateIn, CampaignUpdateIn, CampaignOut, ScheduleIn, RecipientOut
)
from apps.campaigns.services import parse_recipient_csv

router = Router(auth=JWTAuth())


def _get_org_or_403(user, org_slug: str):
    try:
        return OrganizationUser.objects.select_related('organization').get(
            organization__slug=org_slug, user=user
        ).organization
    except OrganizationUser.DoesNotExist:
        raise HttpError(403, 'Not a member of this organization')


@router.get('/', response=List[CampaignOut])
def list_campaigns(request, org_slug: str, status: Optional[str] = None):
    org = _get_org_or_403(request.auth, org_slug)
    qs = Campaign.objects.filter(organization=org)
    if status:
        qs = qs.filter(status=status)
    return [CampaignOut.from_orm(c) for c in qs]


@router.post('/', response=CampaignOut)
def create_campaign(request, org_slug: str, payload: CampaignCreateIn):
    org = _get_org_or_403(request.auth, org_slug)
    c = Campaign.objects.create(
        organization=org,
        name=payload.name,
        subject_line=payload.subject_line,
        preview_text=payload.preview_text,
        from_name=payload.from_name,
        from_email=payload.from_email,
        reply_to=payload.reply_to,
        tags=payload.tags,
        template_id=payload.template_id,
        created_by=request.auth,
    )
    return CampaignOut.from_orm(c)


@router.get('/{campaign_id}', response=CampaignOut)
def get_campaign(request, org_slug: str, campaign_id: UUID):
    org = _get_org_or_403(request.auth, org_slug)
    try:
        return CampaignOut.from_orm(Campaign.objects.get(id=campaign_id, organization=org))
    except Campaign.DoesNotExist:
        raise HttpError(404, 'Campaign not found')


@router.patch('/{campaign_id}', response=CampaignOut)
def update_campaign(request, org_slug: str, campaign_id: UUID, payload: CampaignUpdateIn):
    org = _get_org_or_403(request.auth, org_slug)
    try:
        c = Campaign.objects.get(id=campaign_id, organization=org)
    except Campaign.DoesNotExist:
        raise HttpError(404, 'Campaign not found')
    for field, value in payload.dict(exclude_none=True).items():
        setattr(c, field, value)
    c.save()
    return CampaignOut.from_orm(c)


@router.delete('/{campaign_id}')
def delete_campaign(request, org_slug: str, campaign_id: UUID):
    org = _get_org_or_403(request.auth, org_slug)
    try:
        c = Campaign.objects.get(id=campaign_id, organization=org)
    except Campaign.DoesNotExist:
        raise HttpError(404, 'Campaign not found')
    if c.status != 'draft':
        raise HttpError(400, 'Only draft campaigns can be deleted')
    c.delete()
    return {'detail': 'Deleted'}


@router.post('/{campaign_id}/schedule')
def schedule_campaign(request, org_slug: str, campaign_id: UUID, payload: ScheduleIn):
    from django_q.tasks import schedule as q_schedule
    org = _get_org_or_403(request.auth, org_slug)
    try:
        c = Campaign.objects.get(id=campaign_id, organization=org, status='draft')
    except Campaign.DoesNotExist:
        raise HttpError(404, 'Draft campaign not found')
    c.status = 'scheduled'
    c.scheduled_at = payload.scheduled_at
    c.save()
    q_schedule(
        'apps.campaigns.tasks.dispatch_campaign',
        str(campaign_id),
        schedule_type='O',
        next_run=payload.scheduled_at,
        name=f'campaign-{campaign_id}',
    )
    return {'detail': 'Campaign scheduled', 'scheduled_at': payload.scheduled_at.isoformat()}


@router.post('/{campaign_id}/send-now')
def send_campaign_now(request, org_slug: str, campaign_id: UUID):
    from django_q.tasks import async_task
    org = _get_org_or_403(request.auth, org_slug)
    try:
        c = Campaign.objects.get(id=campaign_id, organization=org, status='draft')
    except Campaign.DoesNotExist:
        raise HttpError(404, 'Draft campaign not found')
    c.status = 'sending'
    c.save()
    async_task('apps.campaigns.tasks.dispatch_campaign', str(campaign_id))
    return {'detail': 'Campaign queued for sending'}


@router.post('/{campaign_id}/recipients')
def upload_recipients(request, org_slug: str, campaign_id: UUID, file: UploadedFile = File(...)):
    org = _get_org_or_403(request.auth, org_slug)
    try:
        c = Campaign.objects.get(id=campaign_id, organization=org)
    except Campaign.DoesNotExist:
        raise HttpError(404, 'Campaign not found')
    content = file.read().decode('utf-8')
    recipients = parse_recipient_csv(content)
    created = 0
    for r in recipients:
        _, was_created = CampaignRecipient.objects.update_or_create(
            campaign=c,
            email=r['email'],
            defaults={'name': r['name'], 'personalization': r['personalization'], 'status': 'queued'},
        )
        if was_created:
            created += 1
    return {'total': len(recipients), 'created': created}


@router.get('/{campaign_id}/recipients', response=List[RecipientOut])
def list_recipients(request, org_slug: str, campaign_id: UUID):
    org = _get_org_or_403(request.auth, org_slug)
    try:
        c = Campaign.objects.get(id=campaign_id, organization=org)
    except Campaign.DoesNotExist:
        raise HttpError(404, 'Campaign not found')
    return [RecipientOut.from_orm(r) for r in c.recipients.all()]
```

- [ ] **Step 6: Run tests**

```bash
python -m pytest apps/campaigns/tests/test_api.py -v
```

Expected: 3 tests PASSED.

- [ ] **Step 7: Commit**

```bash
git add backend/apps/campaigns/
git commit -m "feat: campaigns API with CRUD, recipients, schedule and send-now"
```

---

## Task 9: Django-Q2 Email Dispatch Task

**Files:**
- Create: `backend/apps/campaigns/tasks.py`
- Create: `backend/apps/campaigns/tests/test_tasks.py`

- [ ] **Step 1: Write failing test**

```python
# backend/apps/campaigns/tests/test_tasks.py
import pytest
from unittest.mock import patch, MagicMock
from apps.campaigns.tasks import dispatch_campaign
from apps.campaigns.tests.factories import CampaignFactory, CampaignRecipientFactory
from apps.organizations_app.tests.factories import OrganizationFactory
from apps.settings_app.models import SMTPConfig


@pytest.mark.django_db
def test_dispatch_campaign_sends_to_all_queued_recipients():
    org = OrganizationFactory()
    SMTPConfig.objects.create(
        organization=org, host='smtp.test.com', port=587,
        username='user', password='pass', use_tls=True
    )
    campaign = CampaignFactory(
        organization=org,
        status='sending',
        subject_line='Test Subject',
        from_name='Maven',
        from_email='noreply@maven.com',
        html_output='<p>Hello {{first_name}}</p>',
    )
    # Use template's html_output via campaign template
    from apps.templates_app.tests.factories import EmailTemplateFactory
    template = EmailTemplateFactory(organization=org, html_output='<p>Hello {{first_name}}</p>')
    campaign.template = template
    campaign.save()

    r1 = CampaignRecipientFactory(campaign=campaign, email='a@test.com', personalization={'first_name': 'Alice'})
    r2 = CampaignRecipientFactory(campaign=campaign, email='b@test.com', personalization={'first_name': 'Bob'})

    with patch('apps.campaigns.tasks.smtplib.SMTP') as mock_smtp:
        mock_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_instance
        dispatch_campaign(str(campaign.id))

    r1.refresh_from_db()
    r2.refresh_from_db()
    campaign.refresh_from_db()
    assert r1.status == 'sent'
    assert r2.status == 'sent'
    assert campaign.status == 'sent'


@pytest.mark.django_db
def test_dispatch_campaign_marks_failed_on_smtp_error():
    org = OrganizationFactory()
    SMTPConfig.objects.create(
        organization=org, host='bad-host', port=587,
        username='user', password='pass', use_tls=True
    )
    from apps.templates_app.tests.factories import EmailTemplateFactory
    template = EmailTemplateFactory(organization=org, html_output='<p>Hello</p>')
    campaign = CampaignFactory(organization=org, status='sending', template=template)
    r = CampaignRecipientFactory(campaign=campaign)

    import smtplib
    with patch('apps.campaigns.tasks.smtplib.SMTP', side_effect=smtplib.SMTPException('connection failed')):
        dispatch_campaign(str(campaign.id))

    r.refresh_from_db()
    assert r.status == 'failed'
    assert 'connection failed' in r.error_message
```

- [ ] **Step 2: Run — expect failure**

```bash
python -m pytest apps/campaigns/tests/test_tasks.py -v
```

- [ ] **Step 3: Create `backend/apps/campaigns/tasks.py`**

```python
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone

from apps.campaigns.models import Campaign, CampaignRecipient
from apps.campaigns.services import render_personalized_html

logger = logging.getLogger(__name__)


def dispatch_campaign(campaign_id: str) -> None:
    """Django-Q2 task: sends all queued recipients for a campaign."""
    try:
        campaign = Campaign.objects.select_related(
            'organization', 'template', 'organization__smtp_config'
        ).get(id=campaign_id)
    except Campaign.DoesNotExist:
        logger.error(f'Campaign {campaign_id} not found')
        return

    try:
        smtp_config = campaign.organization.smtp_config
    except Exception:
        logger.error(f'No SMTP config for org {campaign.organization.id}')
        campaign.status = 'failed'
        campaign.save(update_fields=['status'])
        return

    html_template = ''
    if campaign.template:
        html_template = campaign.template.html_output

    recipients = CampaignRecipient.objects.filter(campaign=campaign, status='queued')

    for recipient in recipients:
        personalized_html = render_personalized_html(html_template, recipient.personalization)
        try:
            _send_single_email(
                smtp_config=smtp_config,
                to_email=recipient.email,
                to_name=recipient.name,
                subject=campaign.subject_line,
                from_name=campaign.from_name,
                from_email=campaign.from_email,
                html_body=personalized_html,
            )
            recipient.status = 'sent'
            recipient.sent_at = datetime.now(tz=timezone.utc)
            recipient.error_message = ''
        except Exception as e:
            logger.exception(f'Failed to send to {recipient.email}: {e}')
            recipient.status = 'failed'
            recipient.error_message = str(e)
        recipient.save(update_fields=['status', 'sent_at', 'error_message'])

    failed_count = CampaignRecipient.objects.filter(campaign=campaign, status='failed').count()
    campaign.status = 'failed' if failed_count == recipients.count() and recipients.count() > 0 else 'sent'
    campaign.sent_at = datetime.now(tz=timezone.utc)
    campaign.save(update_fields=['status', 'sent_at'])


def _send_single_email(
    smtp_config,
    to_email: str,
    to_name: str,
    subject: str,
    from_name: str,
    from_email: str,
    html_body: str,
) -> None:
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f'{from_name} <{from_email}>' if from_name else from_email
    msg['To'] = f'{to_name} <{to_email}>' if to_name else to_email
    msg.attach(MIMEText(html_body, 'html'))

    if smtp_config.use_ssl:
        smtp_class = smtplib.SMTP_SSL
    else:
        smtp_class = smtplib.SMTP

    with smtp_class(smtp_config.host, smtp_config.port) as server:
        if smtp_config.use_tls and not smtp_config.use_ssl:
            server.starttls()
        if smtp_config.username:
            server.login(smtp_config.username, smtp_config.password)
        server.sendmail(from_email, [to_email], msg.as_string())
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest apps/campaigns/tests/test_tasks.py -v
```

Expected: 2 tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add backend/apps/campaigns/tasks.py backend/apps/campaigns/tests/test_tasks.py
git commit -m "feat: Django-Q2 email dispatch task with SMTP sending"
```

---

## Task 10: Settings API (SMTP)

**Files:**
- Create: `backend/apps/settings_app/schemas.py`
- Create: `backend/apps/settings_app/services.py`
- Create: `backend/apps/settings_app/api.py`
- Create: `backend/apps/settings_app/tests/test_api.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/apps/settings_app/tests/test_api.py
import pytest
from ninja.testing import TestClient
from apps.settings_app.api import router
from apps.organizations_app.tests.factories import OrganizationFactory, OrganizationUserFactory
from apps.accounts.tests.factories import UserFactory
from rest_framework_simplejwt.tokens import RefreshToken

client = TestClient(router)


def auth_headers(user):
    token = str(RefreshToken.for_user(user).access_token)
    return {'Authorization': f'Bearer {token}'}


@pytest.mark.django_db
def test_save_smtp_config():
    user = UserFactory()
    org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user, is_admin=True)
    resp = client.put(
        f'/smtp?org_slug={org.slug}',
        json={
            'host': 'smtp.gmail.com', 'port': 587,
            'username': 'test@gmail.com', 'password': 'secret',
            'use_tls': True, 'use_ssl': False,
        },
        headers=auth_headers(user),
    )
    assert resp.status_code == 200
    assert resp.json()['host'] == 'smtp.gmail.com'
    assert 'password' not in resp.json()  # password not returned


@pytest.mark.django_db
def test_get_smtp_does_not_return_password():
    from apps.settings_app.models import SMTPConfig
    user = UserFactory()
    org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user)
    SMTPConfig.objects.create(organization=org, host='smtp.test.com', port=587, password='secret')
    resp = client.get(f'/smtp?org_slug={org.slug}', headers=auth_headers(user))
    assert resp.status_code == 200
    data = resp.json()
    assert data['host'] == 'smtp.test.com'
    assert 'password' not in data or data.get('password') == ''
```

- [ ] **Step 2: Run — expect failure**

```bash
python -m pytest apps/settings_app/tests/test_api.py -v
```

- [ ] **Step 3: Create `backend/apps/settings_app/schemas.py`**

```python
from ninja import Schema


class SMTPConfigIn(Schema):
    host: str
    port: int = 587
    username: str = ''
    password: str = ''
    use_tls: bool = True
    use_ssl: bool = False


class SMTPConfigOut(Schema):
    host: str
    port: int
    username: str
    use_tls: bool
    use_ssl: bool
    is_verified: bool


class TestEmailIn(Schema):
    to_email: str


class AIKeyIn(Schema):
    openai_api_key: str
```

- [ ] **Step 4: Create `backend/apps/settings_app/services.py`**

```python
import smtplib
from email.mime.text import MIMEText


def test_smtp_connection(host: str, port: int, username: str, password: str,
                         use_tls: bool, use_ssl: bool, to_email: str) -> dict:
    try:
        if use_ssl:
            server = smtplib.SMTP_SSL(host, port, timeout=10)
        else:
            server = smtplib.SMTP(host, port, timeout=10)
        if use_tls and not use_ssl:
            server.starttls()
        if username:
            server.login(username, password)
        msg = MIMEText('<p>SMTP test from Maven Emailer.</p>', 'html')
        msg['Subject'] = 'Maven Emailer — SMTP Test'
        msg['From'] = username or 'noreply@maven.com'
        msg['To'] = to_email
        server.sendmail(username or 'noreply@maven.com', [to_email], msg.as_string())
        server.quit()
        return {'success': True, 'message': 'Test email sent successfully'}
    except smtplib.SMTPException as e:
        return {'success': False, 'message': str(e)}
    except Exception as e:
        return {'success': False, 'message': f'Connection failed: {e}'}
```

- [ ] **Step 5: Create `backend/apps/settings_app/api.py`**

```python
from ninja import Router
from ninja.errors import HttpError
from organizations.models import OrganizationUser
from apps.accounts.auth import JWTAuth
from apps.settings_app.models import SMTPConfig
from apps.settings_app.schemas import SMTPConfigIn, SMTPConfigOut, TestEmailIn, AIKeyIn
from apps.settings_app.services import test_smtp_connection
from apps.organizations_app.models import OrganizationProfile

router = Router(auth=JWTAuth())


def _get_admin_org(user, org_slug: str):
    try:
        ou = OrganizationUser.objects.select_related('organization').get(
            organization__slug=org_slug, user=user
        )
        if not ou.is_admin:
            raise HttpError(403, 'Admin access required')
        return ou.organization
    except OrganizationUser.DoesNotExist:
        raise HttpError(403, 'Not a member of this organization')


@router.get('/smtp', response=SMTPConfigOut)
def get_smtp(request, org_slug: str):
    try:
        ou = OrganizationUser.objects.select_related('organization').get(
            organization__slug=org_slug, user=request.auth
        )
    except OrganizationUser.DoesNotExist:
        raise HttpError(403, 'Not a member of this organization')
    try:
        cfg = SMTPConfig.objects.get(organization=ou.organization)
        return SMTPConfigOut(
            host=cfg.host, port=cfg.port, username=cfg.username,
            use_tls=cfg.use_tls, use_ssl=cfg.use_ssl, is_verified=cfg.is_verified
        )
    except SMTPConfig.DoesNotExist:
        raise HttpError(404, 'SMTP config not configured')


@router.put('/smtp', response=SMTPConfigOut)
def save_smtp(request, org_slug: str, payload: SMTPConfigIn):
    org = _get_admin_org(request.auth, org_slug)
    cfg, _ = SMTPConfig.objects.update_or_create(
        organization=org,
        defaults={
            'host': payload.host, 'port': payload.port,
            'username': payload.username, 'password': payload.password,
            'use_tls': payload.use_tls, 'use_ssl': payload.use_ssl,
            'is_verified': False,
        }
    )
    return SMTPConfigOut(
        host=cfg.host, port=cfg.port, username=cfg.username,
        use_tls=cfg.use_tls, use_ssl=cfg.use_ssl, is_verified=cfg.is_verified
    )


@router.post('/smtp/test')
def test_smtp(request, org_slug: str, payload: TestEmailIn):
    org = _get_admin_org(request.auth, org_slug)
    try:
        cfg = SMTPConfig.objects.get(organization=org)
    except SMTPConfig.DoesNotExist:
        raise HttpError(404, 'SMTP config not found')
    result = test_smtp_connection(
        host=cfg.host, port=cfg.port, username=cfg.username,
        password=cfg.password, use_tls=cfg.use_tls, use_ssl=cfg.use_ssl,
        to_email=payload.to_email,
    )
    if result['success']:
        cfg.is_verified = True
        cfg.save(update_fields=['is_verified'])
    return result


@router.put('/ai-key')
def update_ai_key(request, org_slug: str, payload: AIKeyIn):
    org = _get_admin_org(request.auth, org_slug)
    profile, _ = OrganizationProfile.objects.get_or_create(organization=org)
    profile.openai_api_key = payload.openai_api_key
    profile.save(update_fields=['openai_api_key'])
    return {'detail': 'API key updated'}
```

- [ ] **Step 6: Run tests**

```bash
python -m pytest apps/settings_app/tests/test_api.py -v
```

Expected: 2 tests PASSED.

- [ ] **Step 7: Commit**

```bash
git add backend/apps/settings_app/
git commit -m "feat: SMTP config API with test-connection endpoint"
```

---

## Task 11: LangGraph AI Agents

**Files:**
- Create: `backend/apps/ai_features/agents/base.py`
- Create: `backend/apps/ai_features/agents/subject_line.py`
- Create: `backend/apps/ai_features/agents/copy_optimizer.py`
- Create: `backend/apps/ai_features/agents/spam_checker.py`
- Create: `backend/apps/ai_features/agents/cta_optimizer.py`
- Create: `backend/apps/ai_features/tests/test_agents.py`

- [ ] **Step 1: Write failing test**

```python
# backend/apps/ai_features/tests/test_agents.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from apps.ai_features.agents.subject_line import SubjectLineAgent
from apps.ai_features.agents.spam_checker import SpamCheckerAgent


@pytest.mark.asyncio
async def test_subject_line_agent_returns_list():
    agent = SubjectLineAgent(api_key='test-key')
    mock_chunks = [
        MagicMock(content='1. Transform Your Enterprise\n'),
        MagicMock(content='2. Modernize Operations Today\n'),
        MagicMock(content='3. Unlock Business Insights\n'),
    ]
    with patch.object(agent.llm, 'astream', return_value=aiter(mock_chunks)):
        chunks = []
        async for chunk in agent.astream({'campaign_name': 'Cloud Launch', 'industry': 'Technology'}):
            chunks.append(chunk)
    assert len(chunks) > 0
    full_text = ''.join(chunks)
    assert 'Transform' in full_text or len(full_text) > 0


@pytest.mark.asyncio
async def test_spam_checker_agent_streams():
    agent = SpamCheckerAgent(api_key='test-key')
    mock_chunks = [MagicMock(content='Score: 12/100\nNo spam triggers found.\n')]
    with patch.object(agent.llm, 'astream', return_value=aiter(mock_chunks)):
        chunks = []
        async for chunk in agent.astream({'subject': 'Hello World', 'body': 'Professional content here'}):
            chunks.append(chunk)
    assert len(chunks) > 0


async def aiter(items):
    for item in items:
        yield item
```

- [ ] **Step 2: Run — expect failure**

```bash
python -m pytest apps/ai_features/tests/test_agents.py -v
```

- [ ] **Step 3: Create `backend/apps/ai_features/agents/base.py`**

```python
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel


def get_llm(api_key: str, model: str = 'gpt-4o', streaming: bool = True) -> BaseChatModel:
    """
    Factory that returns the configured LLM.
    Swap ChatOpenAI for ChatAnthropic/ChatGoogleGenerativeAI here for provider switching.
    """
    return ChatOpenAI(
        model=model,
        api_key=api_key,
        streaming=streaming,
        temperature=0.7,
    )
```

- [ ] **Step 4: Create `backend/apps/ai_features/agents/subject_line.py`**

```python
from typing import AsyncIterator
from langchain_core.messages import HumanMessage, SystemMessage
from apps.ai_features.agents.base import get_llm


SYSTEM_PROMPT = """You are an expert B2B email marketing specialist for Maven Technosoft, 
a technology solutions company. Generate compelling subject lines for enterprise email campaigns.
Focus on: digital transformation, cloud computing, big data, enterprise solutions, TTHL technology.
Always produce exactly 5 subject lines, numbered 1-5, one per line.
Keep each under 60 characters. Focus on value, urgency, and enterprise relevance."""


class SubjectLineAgent:
    def __init__(self, api_key: str):
        self.llm = get_llm(api_key)

    async def astream(self, input_data: dict) -> AsyncIterator[str]:
        campaign_name = input_data.get('campaign_name', '')
        industry = input_data.get('industry', 'Technology')
        tone = input_data.get('tone', 'professional')
        existing_draft = input_data.get('existing_draft', '')

        user_content = f"""Campaign: {campaign_name}
Industry: {industry}
Tone: {tone}
Existing draft (improve on this): {existing_draft}

Generate 5 high-converting subject lines:"""

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ]

        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content
```

- [ ] **Step 5: Create `backend/apps/ai_features/agents/copy_optimizer.py`**

```python
from typing import AsyncIterator
from langchain_core.messages import HumanMessage, SystemMessage
from apps.ai_features.agents.base import get_llm


SYSTEM_PROMPT = """You are an enterprise email copywriter for Maven Technosoft.
Rewrite the provided email copy to be more compelling, professional, and conversion-focused.
Maintain the original intent but improve: clarity, tone, CTA strength, and enterprise positioning.
Output only the improved copy — no explanations."""


class CopyOptimizerAgent:
    def __init__(self, api_key: str):
        self.llm = get_llm(api_key)

    async def astream(self, input_data: dict) -> AsyncIterator[str]:
        original_copy = input_data.get('copy', '')
        tone = input_data.get('tone', 'professional')
        brand_voice = input_data.get('brand_voice', 'innovative, reliable, enterprise-focused')

        user_content = f"""Original email copy:
{original_copy}

Target tone: {tone}
Brand voice: {brand_voice}

Rewrite this copy to be more compelling:"""

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ]

        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content
```

- [ ] **Step 6: Create `backend/apps/ai_features/agents/spam_checker.py`**

```python
from typing import AsyncIterator
from langchain_core.messages import HumanMessage, SystemMessage
from apps.ai_features.agents.base import get_llm


SYSTEM_PROMPT = """You are an email deliverability expert. Analyze the provided email content for spam triggers.
Your response MUST follow this exact format:
SPAM SCORE: [0-100]/100
RISK LEVEL: [Low/Medium/High]
FLAGGED WORDS: [comma-separated list or 'None']
ISSUES:
- [issue 1]
- [issue 2]
FIXES:
- [fix 1]
- [fix 2]"""


class SpamCheckerAgent:
    def __init__(self, api_key: str):
        self.llm = get_llm(api_key)

    async def astream(self, input_data: dict) -> AsyncIterator[str]:
        subject = input_data.get('subject', '')
        preview_text = input_data.get('preview_text', '')
        body = input_data.get('body', '')

        user_content = f"""Subject line: {subject}
Preview text: {preview_text}
Email body: {body[:2000]}

Analyze for spam triggers and provide deliverability report:"""

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ]

        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content
```

- [ ] **Step 7: Create `backend/apps/ai_features/agents/cta_optimizer.py`**

```python
from typing import AsyncIterator
from langchain_core.messages import HumanMessage, SystemMessage
from apps.ai_features.agents.base import get_llm


SYSTEM_PROMPT = """You are a conversion rate optimization expert for B2B enterprise emails.
Generate high-converting CTA button text variants.
Output exactly 4 CTA options, formatted as:
1. [CTA TEXT] — [Why it converts]
2. [CTA TEXT] — [Why it converts]
3. [CTA TEXT] — [Why it converts]
4. [CTA TEXT] — [Why it converts]
Keep CTA text under 5 words. Focus on enterprise action verbs."""


class CTAOptimizerAgent:
    def __init__(self, api_key: str):
        self.llm = get_llm(api_key)

    async def astream(self, input_data: dict) -> AsyncIterator[str]:
        campaign_goal = input_data.get('campaign_goal', 'schedule a demo')
        current_cta = input_data.get('current_cta', '')
        industry = input_data.get('industry', 'Technology')

        user_content = f"""Campaign goal: {campaign_goal}
Current CTA: {current_cta}
Industry: {industry}

Generate 4 high-converting CTA variants:"""

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ]

        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content
```

- [ ] **Step 8: Run tests**

```bash
python -m pytest apps/ai_features/tests/test_agents.py -v
```

Expected: 2 tests PASSED.

- [ ] **Step 9: Commit**

```bash
git add backend/apps/ai_features/agents/
git commit -m "feat: LangGraph AI agents (subject line, copy optimizer, spam checker, CTA)"
```

---

## Task 12: AI SSE Streaming Endpoint

**Files:**
- Create: `backend/apps/ai_features/schemas.py`
- Create: `backend/apps/ai_features/api.py`
- Create: `backend/apps/ai_features/tests/test_api.py`

- [ ] **Step 1: Write failing test**

```python
# backend/apps/ai_features/tests/test_api.py
import pytest
from ninja.testing import TestClient
from apps.ai_features.api import router
from apps.organizations_app.tests.factories import OrganizationFactory, OrganizationUserFactory
from apps.accounts.tests.factories import UserFactory
from rest_framework_simplejwt.tokens import RefreshToken

client = TestClient(router)


def auth_headers(user):
    token = str(RefreshToken.for_user(user).access_token)
    return {'Authorization': f'Bearer {token}'}


@pytest.mark.django_db
def test_start_ai_stream_creates_job():
    from apps.ai_features.models import AIJob
    from apps.organizations_app.models import OrganizationProfile
    user = UserFactory()
    org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user)
    OrganizationProfile.objects.create(organization=org, openai_api_key='test-key')
    resp = client.post(
        f'/stream?org_slug={org.slug}',
        json={
            'job_type': 'subject_lines',
            'input_data': {'campaign_name': 'Test Campaign', 'industry': 'Technology'},
        },
        headers=auth_headers(user),
    )
    # SSE endpoint returns streaming, so we check the job was created
    assert AIJob.objects.filter(organization=org, job_type='subject_lines').exists()


@pytest.mark.django_db
def test_list_ai_jobs():
    from apps.ai_features.models import AIJob
    user = UserFactory()
    org = OrganizationFactory()
    OrganizationUserFactory(organization=org, user=user)
    AIJob.objects.create(
        organization=org, job_type='spam_check', status='done',
        input_data={}, output_data={'score': 15}, created_by=user
    )
    resp = client.get(f'/jobs?org_slug={org.slug}', headers=auth_headers(user))
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]['job_type'] == 'spam_check'
```

- [ ] **Step 2: Create `backend/apps/ai_features/schemas.py`**

```python
from ninja import Schema
from typing import Optional
from uuid import UUID
from datetime import datetime


class AIStreamIn(Schema):
    job_type: str  # subject_lines | copy_optimize | spam_check | cta_suggest
    input_data: dict
    campaign_id: Optional[UUID] = None


class AIJobOut(Schema):
    id: UUID
    job_type: str
    status: str
    input_data: dict
    output_data: Optional[dict] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
```

- [ ] **Step 3: Create `backend/apps/ai_features/api.py`**

```python
import json
import asyncio
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from ninja import Router
from ninja.errors import HttpError
from django.http import StreamingHttpResponse
from organizations.models import OrganizationUser

from apps.accounts.auth import JWTAuth
from apps.ai_features.models import AIJob
from apps.ai_features.schemas import AIStreamIn, AIJobOut
from apps.organizations_app.models import OrganizationProfile

router = Router(auth=JWTAuth())

AGENT_MAP = {
    'subject_lines': 'apps.ai_features.agents.subject_line.SubjectLineAgent',
    'copy_optimize': 'apps.ai_features.agents.copy_optimizer.CopyOptimizerAgent',
    'spam_check': 'apps.ai_features.agents.spam_checker.SpamCheckerAgent',
    'cta_suggest': 'apps.ai_features.agents.cta_optimizer.CTAOptimizerAgent',
}


def _get_org_or_403(user, org_slug: str):
    try:
        return OrganizationUser.objects.select_related('organization').get(
            organization__slug=org_slug, user=user
        ).organization
    except OrganizationUser.DoesNotExist:
        raise HttpError(403, 'Not a member of this organization')


def _import_agent(dotted_path: str):
    module_path, class_name = dotted_path.rsplit('.', 1)
    import importlib
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


@router.post('/stream')
def start_ai_stream(request, org_slug: str, payload: AIStreamIn):
    """Start an SSE stream for the given AI job type."""
    org = _get_org_or_403(request.auth, org_slug)

    if payload.job_type not in AGENT_MAP:
        raise HttpError(400, f'Unknown job_type: {payload.job_type}')

    try:
        profile = OrganizationProfile.objects.get(organization=org)
        api_key = profile.openai_api_key
    except OrganizationProfile.DoesNotExist:
        api_key = ''

    job = AIJob.objects.create(
        organization=org,
        job_type=payload.job_type,
        status='running',
        input_data=payload.input_data,
        campaign_id=payload.campaign_id,
        created_by=request.auth,
    )

    AgentClass = _import_agent(AGENT_MAP[payload.job_type])
    agent = AgentClass(api_key=api_key)

    async def event_stream():
        try:
            full_output = []
            yield f'data: {json.dumps({"type": "job_id", "job_id": str(job.id)})}\n\n'
            async for chunk in agent.astream(payload.input_data):
                full_output.append(chunk)
                yield f'data: {json.dumps({"type": "chunk", "content": chunk})}\n\n'
                await asyncio.sleep(0)
            # Save completed output
            await _save_job_done(job.id, ''.join(full_output))
            yield f'data: {json.dumps({"type": "done", "job_id": str(job.id)})}\n\n'
        except Exception as e:
            await _save_job_failed(job.id, str(e))
            yield f'data: {json.dumps({"type": "error", "message": str(e)})}\n\n'

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


async def _save_job_done(job_id, output: str):
    from asgiref.sync import sync_to_async
    @sync_to_async
    def _save():
        AIJob.objects.filter(id=job_id).update(
            status='done',
            output_data={'text': output},
            completed_at=datetime.now(tz=timezone.utc),
        )
    await _save()


async def _save_job_failed(job_id, error: str):
    from asgiref.sync import sync_to_async
    @sync_to_async
    def _save():
        AIJob.objects.filter(id=job_id).update(
            status='failed',
            output_data={'error': error},
            completed_at=datetime.now(tz=timezone.utc),
        )
    await _save()


@router.get('/jobs', response=List[AIJobOut])
def list_jobs(request, org_slug: str):
    org = _get_org_or_403(request.auth, org_slug)
    jobs = AIJob.objects.filter(organization=org)
    return [AIJobOut.from_orm(j) for j in jobs]


@router.get('/jobs/{job_id}', response=AIJobOut)
def get_job(request, org_slug: str, job_id: UUID):
    org = _get_org_or_403(request.auth, org_slug)
    try:
        return AIJobOut.from_orm(AIJob.objects.get(id=job_id, organization=org))
    except AIJob.DoesNotExist:
        raise HttpError(404, 'Job not found')
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest apps/ai_features/tests/test_api.py -v
```

Expected: 2 tests PASSED.

- [ ] **Step 5: Run full backend test suite**

```bash
python -m pytest -v --tb=short
```

Expected: all tests PASSED.

- [ ] **Step 6: Commit**

```bash
git add backend/apps/ai_features/
git commit -m "feat: AI SSE streaming endpoint with LangGraph agents"
```

---

## Task 13: System Email Templates Seed Data

**Files:**
- Create: `backend/apps/templates_app/management/commands/seed_templates.py`

- [ ] **Step 1: Create management command**

```python
# backend/apps/templates_app/management/commands/seed_templates.py
from django.core.management.base import BaseCommand
from organizations.models import Organization
from apps.templates_app.models import EmailTemplate


SYSTEM_TEMPLATES = [
    {
        'name': 'Enterprise Technology Solutions',
        'category': 'announcement',
        'gjs_components': {
            'type': 'mj-body',
            'components': [
                {
                    'type': 'mj-section',
                    'attributes': {'background-color': '#1a1a2e'},
                    'components': [
                        {
                            'type': 'mj-column',
                            'components': [
                                {
                                    'type': 'mj-text',
                                    'content': '<h1 style="color:#ffffff;font-family:sans-serif;">Transform Your Enterprise</h1>',
                                },
                                {
                                    'type': 'mj-text',
                                    'content': '<p style="color:#cccccc;">Scalable, domain-driven technology solutions for modern enterprises.</p>',
                                },
                                {
                                    'type': 'mj-button',
                                    'attributes': {'background-color': '#e94560', 'href': '{{cta_url}}'},
                                    'content': 'Explore Solutions',
                                },
                            ],
                        }
                    ],
                }
            ],
        },
        'mjml_source': '',
        'html_output': '',
    },
    {
        'name': 'Cloud Computing Campaign',
        'category': 'promo',
        'gjs_components': {'type': 'mj-body', 'components': []},
        'mjml_source': '',
        'html_output': '',
    },
    {
        'name': 'Big Data & Analytics Newsletter',
        'category': 'newsletter',
        'gjs_components': {'type': 'mj-body', 'components': []},
        'mjml_source': '',
        'html_output': '',
    },
    {
        'name': 'Travel & Logistics Solutions',
        'category': 'outreach',
        'gjs_components': {'type': 'mj-body', 'components': []},
        'mjml_source': '',
        'html_output': '',
    },
    {
        'name': 'Webinar & Industry Events',
        'category': 'webinar',
        'gjs_components': {'type': 'mj-body', 'components': []},
        'mjml_source': '',
        'html_output': '',
    },
    {
        'name': 'Enterprise Onboarding',
        'category': 'onboarding',
        'gjs_components': {'type': 'mj-body', 'components': []},
        'mjml_source': '',
        'html_output': '',
    },
]


class Command(BaseCommand):
    help = 'Seed system email templates for all organizations'

    def handle(self, *args, **options):
        for org in Organization.objects.all():
            for tpl in SYSTEM_TEMPLATES:
                EmailTemplate.objects.get_or_create(
                    organization=org,
                    name=tpl['name'],
                    is_system=True,
                    defaults={
                        'category': tpl['category'],
                        'gjs_components': tpl['gjs_components'],
                        'mjml_source': tpl['mjml_source'],
                        'html_output': tpl['html_output'],
                    },
                )
            self.stdout.write(f'Seeded templates for {org.name}')
        self.stdout.write(self.style.SUCCESS('Done.'))
```

- [ ] **Step 2: Create `__init__.py` files for management commands**

```bash
mkdir -p backend/apps/templates_app/management/commands
touch backend/apps/templates_app/management/__init__.py
touch backend/apps/templates_app/management/commands/__init__.py
```

- [ ] **Step 3: Run the command**

```bash
python manage.py seed_templates
```

Expected: `Done.` (may say no orgs if none exist yet — that's fine).

- [ ] **Step 4: Commit**

```bash
git add backend/apps/templates_app/management/
git commit -m "feat: seed system email templates management command"
```

---

## Task 14: Final Integration Check

- [ ] **Step 1: Run all migrations cleanly**

```bash
cd backend
python manage.py migrate
```

Expected: `No migrations to apply.`

- [ ] **Step 2: Run full test suite**

```bash
python -m pytest -v --tb=short 2>&1 | tail -30
```

Expected: all tests PASS, no errors.

- [ ] **Step 3: Start development server and verify API docs load**

```bash
python manage.py runserver
```

Open: `http://localhost:8000/api/docs`
Expected: Django Ninja OpenAPI docs showing all 6 routers.

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete backend Phase 1 — auth, orgs, templates, campaigns, AI agents, SMTP"
```

---

## Summary

| Task | Feature | Tests |
|------|---------|-------|
| 1 | Project scaffolding + settings | — |
| 2 | Custom User model | 3 tests |
| 3 | django-organizations extension | 3 tests |
| 4 | All core models | 4 tests |
| 5 | JWT auth API | 4 tests |
| 6 | Org API + permissions | 1 test |
| 7 | Templates API | 3 tests |
| 8 | Campaigns API | 3 tests |
| 9 | Django-Q2 dispatch task | 2 tests |
| 10 | Settings/SMTP API | 2 tests |
| 11 | LangGraph AI agents | 2 tests |
| 12 | AI SSE streaming | 2 tests |
| 13 | System templates seed | — |
| 14 | Integration check | all |
