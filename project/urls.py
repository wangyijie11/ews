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
    # 获取项目名，不分页，用于下拉框
    url(r'^get_projectlist/', views.get_projectlist, name='get_projectlist'),
    # 获取项目名，分页，用于表
    url(r'^project/', views.project, name='project'),
    url(r'^versionlist/', views.versionlist, name='versionlist'),
    # 获取版本号，不分页，用于下拉框
    url(r'^get_versionlist/', views.get_versionlist, name='get_versionlist'),
    # 获取版本号，分页，用于表
    url(r'^version/', views.version, name='version'),
    url(r'^composelist/', views.composelist, name='composelist'),
    url(r'compose/', views.compose, name='compose'),
    # 上传文件
    url(r'upload/', views.upload, name='upload'),
    # 读取文件
    url(r'readfile/', views.readfile, name='readfile'),




]
