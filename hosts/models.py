# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User, Group


class EwsHost(models.Model):
    id = models.AutoField(primary_key=True)
    ip = models.CharField(max_length=255, blank=True, null=True)
    hostname = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    cpu_cores = models.IntegerField(blank=True, null=True)
    memory = models.IntegerField(blank=True, null=True)
    disk = models.IntegerField(blank=True, null=True)
    docker_version = models.CharField(max_length=255, blank=True, null=True)
    os = models.CharField(max_length=255, blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)
    ssh_port = models.IntegerField(blank=True, null=True)
    ssh_user = models.CharField(max_length=255, blank=True, null=True)
    ssh_password = models.CharField(blank=True, max_length=255, null=True)
    host_json = models.CharField(max_length=255, blank=True, null=True)
    tab_user = models.ForeignKey(User, on_delete=models.CASCADE)
    tab_group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return self.ip

    class Meta:
        db_table = 'ews_host'
        ordering = ["-created_time"]


class EwsFirewall(models.Model):
    id = models.AutoField(primary_key=True)
    kind = models.CharField(max_length=255, blank=True, null=True)
    policy_name = models.CharField(max_length=255, blank=True, null=True)
    policy_json = models.CharField(max_length=255, blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)
    tab_user = models.ForeignKey(User, on_delete=models.CASCADE)
    tab_group = models.ForeignKey(Group, on_delete=models.CASCADE)
    iscustomize = models.BooleanField()
    tab_host_firewall = models.ManyToManyField(
        to=EwsHost,
        through='EwsHostFirewall',
        through_fields=('tab_firewall', 'tab_host')
     )

    def __str__(self):
        return self.cmd

    class Meta:
        db_table = 'ews_firewall'
        ordering = ["-created_time"]


class EwsHostFirewall(models.Model):
    id = models.AutoField(primary_key=True)
    tab_firewall = models.ForeignKey(EwsFirewall, on_delete=models.CASCADE)
    tab_host = models.ForeignKey(EwsHost, on_delete=models.CASCADE)
    created_time = models.DateTimeField(blank=True, null=True)
    tab_user = models.CharField(max_length=255, blank=True, null=True)
    policy_cmd = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.id

    class Meta:
        db_table = 'ews_host_firewall'
        ordering = ["-created_time"]
