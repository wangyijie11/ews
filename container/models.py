from django.db import models
from django.contrib.auth.models import User, Group
from project.models import EwsProject, EwsProjectVersion, EwsCompose, EwsProjectApp
from hosts.models import EwsHost


# Create your models here.
class EwsServiceGroup(models.Model):
    id = models.AutoField(primary_key=True)
    service_group = models.CharField(max_length=255, blank=True, null=True)
    service_group_desc = models.CharField(max_length=255, blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)
    tab_user = models.ForeignKey(User, on_delete=models.CASCADE)
    tab_group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return self.service_group

    class Meta:
        db_table = 'ews_service_group'
        ordering = ["-created_time"]


class EwsService(models.Model):
    id = models.AutoField(primary_key=True)
    service = models.CharField(max_length=255, blank=True, null=True)
    service_desc = models.CharField(max_length=255, blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    port = models.CharField(max_length=255, blank=True, null=True)
    compose = models.CharField(max_length=255, blank=True, null=True)
    project = models.CharField(max_length=255, blank=True, null=True)
    version = models.CharField(max_length=255, blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)
    host = models.ManyToManyField(EwsHost)
    tab_service_group = models.ForeignKey(EwsServiceGroup, on_delete=models.CASCADE)
    tab_user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.service

    class Meta:
        db_table = 'ews_service'
        ordering = ["-created_time"]



