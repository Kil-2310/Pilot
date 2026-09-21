"""
URL configuration for django_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from django_site import settings

urlpatterns = [
    path('admin/', admin.site.urls),

    path('authentication/', include('authentication.urls')),
    path('pilot/', include('pilot.urls')),
    path('responsible-person/', include('responsible_person.urls')),
    path('accompanied/', include('accompanied.urls')),
    path('report/', include('report.urls')),

    path('api/responsible-person/', include('responsible_person.api_urls')),
    path('api/pilot/', include('pilot.api_urls')),
    path('api/accompanied/', include('accompanied.api_urls')),
    path('api/report/', include('report.api_urls')),
]

if settings.DEBUG:
    from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    schemas = [
        path('api/schema/', SpectacularAPIView.as_view(), name="schema"),
        path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
        path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]
    urlpatterns.extend(schemas)
