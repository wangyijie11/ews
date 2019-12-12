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
from hosts import views

app_name = 'hosts'
urlpatterns = [
    url(r'^hostlist/', views.hostlist, name='hostlist'),
    url(r'^firewall/', views.firewall, name='firewall'),
    url(r'^firewallport/', views.firewallport, name='firewallport'),
    url(r'^firewallrich/', views.firewallrich, name='firewallrich'),
    url(r'^imagelist/', views.imagelist, name='imagelist'),
    url(r'^containerlist/', views.containerlist, name='containerlist'),
    url(r'^firewalllist/', views.firewalllist, name='firewalllist'),
    url(r'^image/', views.image, name='image'),
    url(r'^container/', views.container, name='container'),
    url(r'^host/', views.host, name='host'),
    url(r'^get_hostip/', views.get_hostip, name='get_hostip'),
    url(r'^applypolicy/', views.applypolicy, name='applypolicy'),
    url(r'^get_host_byfirewall/', views.get_host_byfirewall, name='get_host_byfirewall'),
    url(r'^post_desc/', views.post_desc, name='post_desc'),
    url(r'^docker/', views.docker, name='docker'),
    url(r'^hostmonitor/', views.hostmonitor, name='hostmonitor'),
    url(r'^containter/log/', views.containerlog, name='containerlog')
]
