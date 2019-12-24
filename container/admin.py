from django.contrib import admin

# Register your models here.
from container import models

admin.site.register(models.EwsService)
admin.site.register(models.EwsServiceGroup)