from django.db import models
from django.contrib.auth.models import User, Group
# Create your models here.


class EwsRegistry(models.Model):
    id = models.AutoField(primary_key=True)
    domain = models.CharField(max_length=255, blank=True, null=True)
    ip = models.CharField(max_length=255, blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    registry_json = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'ews_registry'


class EwsRepositoryPub(models.Model):
    id = models.AutoField(primary_key=True)
    repository = models.CharField(max_length=255, blank=True, null=True)
    repository_desc = models.CharField(max_length=500, blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)
    readme = models.FileField(upload_to='md/repositorypub/')
    image = models.ImageField(upload_to='img/repositorypub/')
    repository_json = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'ews_repository_pub'


class EwsRepository(models.Model):
    id = models.AutoField(primary_key=True)
    repository = models.CharField(max_length=255, blank=True, null=True)
    repository_desc = models.CharField(max_length=500, blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)
    readme = models.FileField(upload_to='md/repositorypub/')
    image = models.ImageField(upload_to='img/repositorypub/')
    tab_group = models.ForeignKey(Group, on_delete=models.CASCADE)
    repository_json = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'ews_repository'
