"""
URL configuration for ephor_2025 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from blog.views import landing_page  # Importe a view do aplicativo blog

urlpatterns = [
    path('', landing_page, name='landing_page'),  # Landing page na raiz
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # URLs do django-allauth
    path('blog/', include('blog.urls')),  # URLs da aplicação blog
]