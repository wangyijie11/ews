from django.db import models
from django.contrib.auth.models import User, Group
# Create your models here.


class EwsCicd(models.Model):
    id = models.AutoField(primary_key=True)
    cicd_user = models.CharField(max_length=255, blank=True, null=True)
    cicd_passwd = models.CharField(max_length=255, blank=True, null=True)
    cicd_token = models.CharField(max_length=255, blank=True, null=True)
    cicd_url = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)
    tab_user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.id

    class Meta:
        db_table = 'ews_cicd'
        ordering = ["-created_time"]