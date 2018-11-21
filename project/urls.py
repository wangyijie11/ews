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
from project import views

app_name = 'project'
urlpatterns = [
    url(r'^projectlist/', views.projectlist, name='projectlist'),
    url(r'^get_projectlist/', views.get_projectlist, name='get_projectlist'),
    url(r'^project/', views.project, name='project'),
    url(r'^versionlist/', views.versionlist, name='versionlist'),
    url(r'^version/', views.version, name='version'),



]
