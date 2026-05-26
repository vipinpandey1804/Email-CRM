from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from apps.accounts.api import router as auth_router

api = NinjaAPI(title='Maven Emailer API', version='1.0.0', docs_url='/api/docs')

api.add_router('/auth/', auth_router, tags=['Auth'])

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api.urls),
]
