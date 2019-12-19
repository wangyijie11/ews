from django.conf.urls import url
from container import views

app_name = 'container'
urlpatterns = [
    url(r'^containerlist/', views.containerlist, name='containerlist'),
]
