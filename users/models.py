# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class EwsUser(models.Model):
    id = models.IntegerField(primary_key=True)
    account = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)
    user_json = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'ews_user'

    def __str__(self):
        return self.account


class EwsGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    group_id = models.CharField(max_length=255, blank=True, null=True)
    group_name = models.CharField(max_length=255, blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)
    group_json = models.CharField(max_length=255, blank=True, null=True)
    members = models.ManyToManyField(EwsUser, through='EwsUserGroup')

    class Meta:
        db_table = 'ews_group'

    def __str__(self):
        return self.group_id


class EwsUserGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    tab_user = models.ForeignKey(EwsUser, on_delete=models.CASCADE)
    tab_group = models.ForeignKey(EwsGroup, on_delete=models.CASCADE)

    class Meta:
        db_table = 'ews_user_group'
