from django.conf.urls import url
from container import views

app_name = 'container'
urlpatterns = [
    url(r'^containerlist/', views.containerlist, name='containerlist'),
    url(r'^servicelist/', views.servicelist, name='servicelist'),
    url(r'^composerun/', views.composerun, name='composerun'),
    url(r'^servicegroup/', views.servicegroup, name='servicegroup'),
    url(r'^service/', views.service, name='service'),
    url(r'^get_servicegroup/', views.get_servicegroup, name='get_servicegroup'),
    url(r'^get_servicegrouplist/', views.get_servicegrouplist, name='get_servicegrouplist'),
    url(r'^get_host_byservicegroup/', views.get_host_byservicegroup, name='get_host_byservicegroup'),


]
