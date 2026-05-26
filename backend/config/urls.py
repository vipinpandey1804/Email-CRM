from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from apps.accounts.api import router as auth_router
from apps.organizations_app.api import router as orgs_router
from apps.templates_app.api import router as templates_router
from apps.campaigns.api import router as campaigns_router
from apps.settings_app.api import router as settings_router
from apps.ai_features.api import (
    router as ai_router,
    stream_subject_lines,
    stream_copy_optimizer,
    stream_spam_checker,
    stream_cta_optimizer,
)

api = NinjaAPI(title='Maven Emailer API', version='1.0.0', docs_url='/api/docs')

api.add_router('/auth/', auth_router, tags=['Auth'])
api.add_router('/orgs/', orgs_router, tags=['Organizations'])
api.add_router('/templates/', templates_router, tags=['Templates'])
api.add_router('/campaigns/', campaigns_router, tags=['Campaigns'])
api.add_router('/settings/', settings_router, tags=['Settings'])
api.add_router('/ai/', ai_router, tags=['AI'])

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api.urls),
    # SSE streaming endpoints (async views, not Ninja schema endpoints)
    path('ai/subject-lines/stream', stream_subject_lines, name='ai_subject_lines'),
    path('ai/copy-optimizer/stream', stream_copy_optimizer, name='ai_copy_optimizer'),
    path('ai/spam-checker/stream', stream_spam_checker, name='ai_spam_checker'),
    path('ai/cta-optimizer/stream', stream_cta_optimizer, name='ai_cta_optimizer'),
]
