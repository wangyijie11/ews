from django.conf.urls import url
from container import views

app_name = 'container'
urlpatterns = [
    url(r'^containerlist/', views.containerlist, name='containerlist'),
    url(r'^servicelist/', views.servicelist, name='servicelist'),
    url(r'^service/', views.service, name='service'),
    url(r'^get_servicegroup/', views.get_servicegroup, name='get_servicegroup'),
]
