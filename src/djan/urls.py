"""djan URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path

from djan import api, views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/status", api.status_view, name="api_status_view"),
    path("api/shorten", api.shorten_view, name="api_shorten_view"),
    path("api/info/<path:short_url>", api.counter_view, name="counter_view"),
    path("", views.redirect_view, {"short_url": ""}, name="redirect_root"),
    path("<path:short_url>", views.redirect_view, name="redirect"),
]
