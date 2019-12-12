from django.db import models
from django.contrib.auth.models import User, Group
from repository.models import EwsRepository
# Create your models here.


def get_file_path(instance, filename):
    return 'compose/%s/%s/%s' % (instance.tab_project, instance.tab_version, filename)


# 项目
class EwsProject(models.Model):
    id = models.AutoField(primary_key=True)
    projectname = models.CharField(max_length=255, blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)
    project_json = models.CharField(max_length=255, blank=True, null=True)
    repository = models.CharField(max_length=255, blank=True, null=True)
    tab_group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return self.projectname

    class Meta:
        db_table = 'ews_project'
        ordering = ["-created_time"]


# 版本
class EwsProjectVersion(models.Model):
    id = models.AutoField(primary_key=True)
    version = models.CharField(max_length=255, blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)
    version_json = models.CharField(max_length=255, blank=True, null=True)
    tab_project = models.ForeignKey(EwsProject, on_delete=models.CASCADE)

    def __str__(self):
        return self.version

    class Meta:
        db_table = 'ews_project_version'
        ordering = ["-created_time"]


# 应用app
class EwsProjectApp(models.Model):
    id = models.AutoField(primary_key=True)
    app = models.CharField(max_length=255, blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)
    app_json = models.CharField(max_length=255, blank=True, null=True)
    tab_version = models.ForeignKey(EwsProjectVersion, on_delete=models.CASCADE)

    def __str__(self):
        return self.app

    class Meta:
        db_table = 'ews_project_app'
        ordering = ["-created_time"]


# compose文件
class EwsCompose(models.Model):
    id = models.AutoField(primary_key=True)
    created_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    path = models.CharField(max_length=255, blank=True, null=True)
    compose_file = models.CharField(max_length=255, blank=True, null=True)
    tab_project = models.ForeignKey(EwsProject, on_delete=models.CASCADE)
    tab_version = models.ForeignKey(EwsProjectVersion, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True, null=True)
    compose_json = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.compose_file

    class Meta:
        db_table = 'ews_compose'
        ordering = ["-created_time"]