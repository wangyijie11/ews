"""ews URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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

from django.conf.urls import url
from dockerclient import views

app_name = 'docker'
urlpatterns = [
    url(r'^container/run/', views.container_run, name='container_run'),
    url(r'^container/start/', views.container_start, name='container_start'),
    url(r'^container/stop/', views.container_stop, name='container_stop'),
    url(r'^container/restart/', views.container_restart, name='container_restart'),
    url(r'^container/logs/', views.container_logs, name='container_logs'),
]
