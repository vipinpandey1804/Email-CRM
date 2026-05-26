from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from apps.accounts.api import router as auth_router
from apps.organizations_app.api import router as orgs_router
from apps.templates_app.api import router as templates_router

api = NinjaAPI(title='Maven Emailer API', version='1.0.0', docs_url='/api/docs')

api.add_router('/auth/', auth_router, tags=['Auth'])
api.add_router('/orgs/', orgs_router, tags=['Organizations'])
api.add_router('/templates/', templates_router, tags=['Templates'])

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api.urls),
]
