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
from container.models import EwsService, EwsServiceGroup
from project.models import EwsProjectVersion, EwsProject
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


# 返回编排部署页面
def composerun(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_account = request.session.get('ews_account')
        return render(request, 'container/composerun.html', {'ews_account': ews_account})
    else:
        return redirect('/login/')


# 返回部署环境页面
def servicegroup(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_account = request.session.get('ews_account')
        return render(request, 'container/servicegroup.html', {'ews_account': ews_account})
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
            if service_group_id:
                try:
                    result = {}
                    dict = []
                    services = EwsService.objects.filter(tab_service_group_id=service_group_id)
                    if services:
                        for s in services:
                            ips = []
                            ipobjs = EwsService.objects.get(pk=s.id).host.all()
                            for i in ipobjs:
                                ips.append(i.ip)
                            dic = {}
                            dic['id'] = s.id
                            dic['service'] = s.service
                            dic['state'] = ''
                            dic['image'] = s.image
                            dic['ip'] = ips
                            dic['port'] = s.port
                            dic['project'] = s.project
                            dic['version'] = s.version
                            dic['service_desc'] = s.service_desc
                            dict.append(dic)
                        dict = dict[i:j]
                        total = len(dict)
                        result['code'] = 0
                        result['msg'] = ""
                        result['count'] = total
                        result['data'] = dict
                        return JsonResponse(result, safe=False)
                    else:
                        result['code'] = 0
                        result['msg'] = ""
                        result['count'] = 0
                        result['data'] = ""
                        return JsonResponse(result, safe=False)
                except Exception as ex:
                    print(ex)
                    result['code'] = 500
                    result['msg'] = "error:get service by service_group_id"
                    result['count'] = 0
                    result['data'] = ""
                    return JsonResponse(result, safe=False)
            elif service_group_id is None:
                result = {}
                result['code'] = 0
                result['msg'] = "请选择部署环境"
                result['count'] = 0
                result['data'] = ""
                return JsonResponse(result, safe=False)


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


# 获取服务虚拟分组信息，分页
@csrf_exempt
def get_servicegrouplist(request):
    if request.session.get('is_login', None):
        if request.method == 'GET':
            ews_accountid = request.session.get('ews_accountid')
            groups = User.objects.get(pk=ews_accountid).groups.all()
            page = request.GET.get('page')
            rows = request.GET.get('limit')
            i = (int(page) - 1) * int(rows)
            j = (int(page) - 1) * int(rows) + int(rows)
            result = {}
            dict = []
            for g in groups:
                servicegroups = Group.objects.get(pk=g.id).ewsservicegroup_set.all()
                for s in servicegroups:
                    ips = []
                    ipobjs = EwsServiceGroup.objects.get(pk=s.id).host.all()
                    for i in ipobjs:
                        ips.append(i.ip)
                    dic = {}
                    dic['id'] = s.id
                    dic['servive_group'] = s.service_group
                    dic['servive_group_desc'] = s.service_group_desc
                    dic['project'] = EwsProject.objects.get(pk=s.tab_project_id).projectname
                    dic['version'] = EwsProjectVersion.objects.get(pk=s.tab_version_id).version
                    dic['host'] = ips
                    dict.append(dic)

            dict = dict[i:j]
            total = len(dict)
            result['code'] = 0
            result['msg'] = ""
            result['count'] = total
            result['data'] = dict
            return JsonResponse(result, safe=False)