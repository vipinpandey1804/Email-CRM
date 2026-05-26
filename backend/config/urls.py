from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

api = NinjaAPI(title='Maven Emailer API', version='1.0.0', docs_url='/api/docs')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api.urls),
]
