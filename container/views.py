from django.shortcuts import render
from django.conf import settings
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from . import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from hosts.models import EwsHost, EwsFirewall
from django.contrib.auth.models import User, Group
import docker
from docker import DockerClient
from hosts.hostmgr import Centos7
import paramiko
import time
from django.http import QueryDict
# Create your views here.


# 返回服务列表页面
def servicelist(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_account = request.session.get('ews_account')
        return render(request, 'container/servicelist.html', {'ews_account': ews_account})
    else:
        return redirect('/login/')


# 返回容器列表页面
def containerlist(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_account = request.session.get('ews_account')
        return render(request, 'container/containerlist.html', {'ews_account': ews_account})
    else:
        return redirect('/login/')


# 服务列表数据GET/POST/DELETE
@csrf_exempt
def service(request):
    if request.session.get('is_login', None):
        if request.method == 'GET':
            ews_accountid = request.session.get('ews_accountid')
            service_group_id = request.GET.get('service_group_id')
            page = request.GET.get('page')
            rows = request.GET.get('limit')
            i = (int(page) - 1) * int(rows)
            j = (int(page) - 1) * int(rows) + int(rows)
            pass



# 获取服务虚拟分组信息，不分页
@csrf_exempt
def get_servicegroup(request):
    if request.session.get('is_login', None):
        if request.method == 'GET':
            ews_accountid = request.session.get('ews_accountid')
            groups = User.objects.get(pk=ews_accountid).groups.all()
            result = {}
            dict = []
            for g in groups:
                servicegroups = Group.objects.get(pk=g.id).ewsservicegroup_set.all()
                for s in servicegroups:
                    dic = {}
                    dic['id'] = s.id
                    dic['servive_group'] = s.service_group
                    dic['servive_group_desc'] = s.service_group_desc
                    dict.append(dic)
            result['code'] = 0
            result['msg'] = ""
            result['count'] = servicegroups.count()
            result['data'] = dict
            return JsonResponse(result, safe=False)