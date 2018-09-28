# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class EwsHost(models.Model):
    ip = models.CharField(max_length=255, blank=True, null=True)
    hostname = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    cpu_cores = models.IntegerField(blank=True, null=True)
    memory = models.IntegerField(blank=True, null=True)
    disk = models.IntegerField(blank=True, null=True)
    docker_version = models.CharField(max_length=255, blank=True, null=True)
    os = models.CharField(max_length=255, blank=True, null=True)
    extend = models.CharField(max_length=255, blank=True, null=True)
    tab_user_id = models.IntegerField(blank=True, null=True)
    tab_group_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ews_host'
