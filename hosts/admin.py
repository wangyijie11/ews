from django.contrib import admin

# Register your models here.
from hosts import models

admin.site.register(models.EwsHost)


