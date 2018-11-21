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
from repository.models import EwsRepository
# Create your views here.


# 我的项目
def projectlist(request):
    is_login = request.session.get('is_login', False)
    if is_login:
        ews_account = request.session.get('ews_account')
        return render(request, 'project/projectlist.html', {'ews_account': ews_account})
    else:
        return redirect('/login/')


# 项目的版本
def versionlist(request):
    is_login = request.session.get('is_login', False)
    if is_login:
        ews_account = request.session.get('ews_account')
        return render(request, 'project/versionlist.html', {'ews_account': ews_account})
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
    result = {}
    dict = []
    num = 0
    for g in groups:
        projects = Group.objects.get(pk=g.id).ewsproject_set.all()
        for p in projects:
            num = num + 1
            dic = {}
            dic['groupid'] = g.id
            dic['groupname'] = g.name
            dic['projectid'] = p.id
            dic['projectname'] = p.projectname
            dic['repository'] = p.repository
            dic['created_time'] = p.created_time
            dict.append(dic)
    result['code'] = 0
    result['msg'] = ""
    result['count'] = num
    result['data'] = dict
    return JsonResponse(result, safe=False)


# 项目POST/GET/DELETE，添加、删除、获取项目
@csrf_exempt
def project(request):
    if request.session.get('is_login', None):
        if request.method == 'POST':
            projectname = request.POST.get('projectname')
            groupname = request.POST.get('groupname')
            repository = request.POST.get('repository')
            try:
                if projectname and groupname and repository:
                    # 判断是否已存在项目和仓库
                    repository_existed = EwsRepository.objects.filter(repository=repository)
                    projectname_existed = EwsProject.objects.filter(projectname=projectname)
                    if repository_existed:
                        return HttpResponse(json.dumps({"status": 3}))
                    if projectname_existed:
                        return HttpResponse(json.dumps({"status": 4}))
                    # 保存项目和仓库
                    new_project = models.EwsProject()
                    new_repository = models.EwsRepository()

                    new_project.projectname = projectname
                    new_project.created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    new_project.tab_group_id = groupname
                    new_project.repository = repository

                    new_repository.repository = repository
                    new_repository.created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    new_repository.tab_group_id = groupname

                    new_project.save()
                    new_repository.save()
                    return HttpResponse(json.dumps({"status": 0}))
                else:
                    return HttpResponse(json.dumps({"status": 1}))
            except Exception as ex:
                return HttpResponse(json.dumps({"status": 2}))

        if request.method == 'DELETE':
            id = QueryDict(request.body).get('id')
            try:
                if any(id):
                    EwsProject.objects.filter(pk=id).delete()
                    return HttpResponse(json.dumps({"status": 0}))
                else:
                    return HttpResponse(json.dumps({"status": 1}))
            except Exception as ex:
                return HttpResponse(json.dumps({"status": 2}))


# 获取项目的版本
def version(request):
    if request.session.get('is_login', None):
        if request.method == 'POST':
            pass
        if request.method == 'GET':
            pass
        if request.method == 'DELETE':
            pass
    result = {}
    return JsonResponse(result, safe=False)