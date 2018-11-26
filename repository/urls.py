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
from repository import views

app_name = 'repository'
urlpatterns = [
    # 公有仓库
    url(r'^repositorypublist/', views.repositorypublist, name='repositorypublist'),
    url(r'^imagetagspublist/', views.imagetagspublist, name='imagetagspublist'),
    url(r'^get_repositorypublist/', views.get_repositorypublist, name='get_repositorypublist'),
    url(r'^imagetagspub/', views.imagetagspub, name='imagetagspub'),

    # 开发、测试、发布仓库
    url(r'^repositorylist/', views.repositorylist, name='repositorylist'),
    url(r'^imagetagslist/', views.imagetagslist, name='imagetagslist'),
    url(r'^repositry/', views.repository, name='repository'),
    url(r'^image/', views.image, name='image'),
    url(r'^imagetag/', views.imagetag, name='imagetag'),



]
