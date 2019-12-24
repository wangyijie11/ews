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
from project.models import EwsCompose
from project.projectmgr import *
from .forms import UploadForm
import os
from django.conf import settings


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


# 项目版本下的容器启动配置文件
def composelist(request):
    is_login = request.session.get('is_login', False)
    if is_login:
        ews_account = request.session.get('ews_account')
        return render(request, 'project/composelist.html', {'ews_account': ews_account})
    else:
        return redirect('/login/')


# 上传文件
def uploadlist(request):
    is_login = request.session.get('is_login', False)
    if is_login:
        ews_account = request.session.get('ews_account')
        return render(request, 'project/uploadFile.html', {'ews_account': ews_account})
    else:
        return redirect('/login/')


@csrf_exempt
# 获取项目，不分页
def get_projectlist(request):
    if request.session.get('is_login', None):
        if request.method == 'GET':
            ews_accountid = request.session.get('ews_accountid')
            groups = User.objects.get(pk=ews_accountid).groups.all()
            result = {}
            dict = []
            for g in groups:
                projects = Group.objects.get(pk=g.id).ewsproject_set.all()
                for p in projects:
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
            result['count'] = projects.count()
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

        if request.method == 'GET':
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
            dict = dict[i:j]
            result['code'] = 0
            result['msg'] = ""
            result['count'] = num
            result['data'] = dict
            return JsonResponse(result, safe=False)


# 获取版本，不分页
@csrf_exempt
def get_versionlist(request):
    if request.session.get('is_login', None):
        if request.method == 'GET':
            projectid = request.GET.get('projectid')
            if projectid:
                versions = EwsProject.objects.get(pk=projectid).ewsprojectversion_set.all()
                total = versions.count()
                result = {}
                dict = []
                for v in versions:
                    dic = {}
                    dic['versionid'] = v.id
                    dic['version'] = v.version
                    dic['projectname'] = EwsProject.objects.get(pk=projectid).projectname
                    dic['created_time'] = v.created_time
                    dict.append(dic)
                result['code'] = 0
                result['msg'] = ""
                result['count'] = total
                result['data'] = dict
                return JsonResponse(result, safe=False)


# 版本GET/POST/DELETE
@csrf_exempt
def version(request):
    if request.session.get('is_login', None):
        if request.method == 'POST':
            version = request.POST.get('version')
            projectid = request.POST.get('projectid')
            try:
                if version and projectid:
                    versions_existed = EwsProject.objects.get(pk=projectid).ewsprojectversion_set.all()
                    if version in versions_existed:
                        return HttpResponse(json.dumps({"status": 1}))
                    new_version = models.EwsProjectVersion()
                    new_version.version = version
                    new_version.created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    new_version.tab_project_id = projectid
                    new_version.save()
                    return HttpResponse(json.dumps({"status": 0}))
            except Exception as ex:
                return HttpResponse(json.dumps({"status": 2}))

        if request.method == 'GET':
            projectid = request.GET.get('projectid')
            versions = EwsProject.objects.get(pk=projectid).ewsprojectversion_set.all()
            page = request.GET.get('page')
            rows = request.GET.get('limit')
            i = (int(page) - 1) * int(rows)
            j = (int(page) - 1) * int(rows) + int(rows)
            total = versions.count()
            versions = versions[i:j]
            result = {}
            dict = []
            for v in versions:
                dic = {}
                dic['id'] = v.id
                dic['version'] = v.version
                dic['projectname'] = EwsProject.objects.get(pk=projectid).projectname
                dic['created_time'] = v.created_time
                dict.append(dic)
            result['code'] = 0
            result['msg'] = ""
            result['count'] = total
            result['data'] = dict
            return JsonResponse(result, safe=False)

        if request.method == 'DELETE':
            id = QueryDict(request.body).get('id')
            try:
                if any(id):
                    EwsProjectVersion.objects.filter(pk=id).delete()
                    return HttpResponse(json.dumps({"status": 0}))
                else:
                    return HttpResponse(json.dumps({"status": 1}))
            except Exception as ex:
                return HttpResponse(json.dumps({"status": 2}))


# 容器启动配置文件GET/POST/DELETE
@csrf_exempt
def compose(request):
    if request.session.get('is_login', None):
        if request.method == 'GET':
            versionid = request.GET.get('versionid', None)
            projectid = request.GET.get('projectid', None)
            ews_accountid = request.session.get('ews_accountid')
            groups = User.objects.get(pk=ews_accountid).groups.all()
            page = request.GET.get('page')
            rows = request.GET.get('limit')
            i = (int(page) - 1) * int(rows)
            j = (int(page) - 1) * int(rows) + int(rows)
            if versionid:
                try:
                    result = {}
                    data = get_compose_byversion(versionid)
                    result['data'] = data[i:j]
                    result['code'] = 0
                    result['msg'] = ""
                    result['count'] = len(data)
                    return JsonResponse(result, safe=False)
                except Exception as ex:
                    result['code'] = 500
                    result['msg'] = "error:get_compose_byversion"
                    result['count'] = 0
                    result['data'] = ""
                    return JsonResponse(result, safe=False)

            elif versionid is None and projectid is None:
                try:
                    result = {}
                    dict = []
                    for g in groups:
                        projects = Group.objects.get(pk=g.id).ewsproject_set.all()
                        for p in projects:
                            data = get_compose_byproject(p.id)
                            dict = dict + data
                    result['code'] = 0
                    result['msg'] = ""
                    result['count'] = len(dict)
                    result['data'] = dict[i:j]
                    return JsonResponse(result, safe=False)
                except Exception as ex:
                    print(ex)
                    result['code'] = 500
                    result['msg'] = "error:get_compose_byproject"
                    result['count'] = 0
                    result['data'] = ""
                    return JsonResponse(result, safe=False)

            elif any(projectid) and versionid is None:
                try:
                    result = {}
                    data = get_compose_byproject(projectid)
                    result['code'] = 0
                    result['msg'] = ""
                    result['count'] = len(data)
                    result['data'] = data[i:j]
                    return JsonResponse(result, safe=False)
                except Exception as ex:
                    result['code'] = 500
                    result['msg'] = "error:get_compose_byproject"
                    result['count'] = 0
                    result['data'] = ""
                    return JsonResponse(result, safe=False)

            else:
                result = {}
                result['code'] = 400
                result['msg'] = "参数错误"
                result['count'] = 0
                result['data'] = ""
                return JsonResponse(result, safe=False)


# 上传文件
@csrf_exempt
def upload(request):
    if request.session.get('is_login', None):
        if request.method == 'POST':
            form = UploadForm(request.POST, request.FILES)
            projectid = request.POST.get('projectid')
            versionid = request.POST.get('versionid')
            if form.is_valid() and projectid and versionid:
                try:
                    files = request.FILES.getlist('file')
                    path_project = EwsProject.objects.get(pk=projectid).projectname
                    path_version = EwsProjectVersion.objects.get(pk=versionid).version
                    for f in files:
                        new_compose = models.EwsCompose()
                        new_compose.created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                        new_compose.update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                        new_compose.path = os.path.join(settings.MEDIA_ROOT, path_project, path_version)
                        new_compose.compose_file = f.name
                        new_compose.description = ''
                        new_compose.compose_json = ''
                        new_compose.tab_project_id = projectid
                        new_compose.tab_version_id = versionid

                        if not os.path.isdir(new_compose.path):
                            os.makedirs(new_compose.path)
                        destination = open(os.path.join(new_compose.path, f.name), 'wb+')
                        for chunk in f.chunks():
                            destination.write(chunk)
                        destination.close()
                        new_compose.save()
                    # 返回成功
                    return HttpResponse(json.dumps({"code": 0}))
                except Exception as ex:
                    # 文件写入失败
                    print(ex)
                    return HttpResponse(json.dumps({"code": 1}))
            else:
                # 返回POST请求缺少参数
                return HttpResponse(json.dumps({"code": 2}))


# 读取文件
@csrf_exempt
def readfile(request):
    if request.session.get('is_login', None):
        file_id = request.GET.get('file_id')
        if file_id:
            compose_file = EwsCompose.objects.get(pk=file_id)
            with open(os.path.join(compose_file.path, compose_file.compose_file), 'r+') as f:
                content = f.readlines()
            result = {}
            result['code'] = 0
            result['data'] = content
            result['id'] = compose_file.id
            result['file'] = compose_file.compose_file
            return JsonResponse(result, safe=False)

