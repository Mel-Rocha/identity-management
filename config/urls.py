from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Django",
        default_version='v0',
        description="Documentação da API para o projeto Django",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contato@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(
        permissions.BasePermission,
    ),
)

urlpatterns = [
    path(
        'admin/',
        admin.site.urls),
    path('core/', include('apps.core.urls')),
    path('users/', include('apps.users.urls')),
]


if settings.DEBUG:
    # Segurança por obscuridade: a documentação da API está disponível
    # apenas em modo de desenvolvimento
    urlpatterns += [
        path(
            'swagger/',
            schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui'),
        path(
            'redoc/',
            schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc'),
    ]