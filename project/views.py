from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from . import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import docker
import paramiko
import time
from django.http import QueryDict
from django.contrib.auth.models import User, Group
from project.models import EwsProject, EwsProjectVersion, EwsProjectApp
# Create your views here.


# 我的项目
def projectlist(request):
    is_login = request.session.get('is_login', False)
    if is_login:
        ews_account = request.session.get('ews_account')
        return render(request, 'project/projectlist.html', {'ews_account': ews_account})
    else:
        return redirect('/login/')


# 获取用户所在所有组的项目
def get_projectlist(request):
    ews_accountid = request.session.get('ews_accountid')
    groups = User.objects.get(pk=ews_accountid).groups.all()
    page = request.GET.get('page')
    rows = request.GET.get('limit')
    i = (int(page) - 1) * int(rows)
    j = (int(page) - 1) * int(rows) + int(rows)

    return JsonResponse(resultdict, safe=False)