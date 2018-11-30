from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
import time
from repository.models import EwsRegistry, EwsRepository, EwsRepositoryPub
from django.contrib.auth.models import User, Group
import urllib.request, urllib.response, urllib.error, urllib.parse
from repository.auth import RegistryAuth
from repository.registry import RegistryApi
from base64 import encodestring
import re
import requests
from requests.auth import AuthBase
from requests.auth import HTTPBasicAuth


# Create your views here.
# 返回公有仓库页面
def repositorypublist(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_account = request.session.get('ews_account')
        return render(request, 'repository/repositoryPub.html', {'ews_account': ews_account})
    else:
        return redirect('/login/')


# 返回项目仓库镜像标签页面
def imagetagspublist(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_account = request.session.get('ews_account')
        return render(request, 'repository/imageTagsPub.html', {'ews_account': ews_account})
    else:
        return redirect('/login/')


# 返回项目仓库页面
def repositorylist(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_account = request.session.get('ews_account')
        return render(request, 'repository/repository.html', {'ews_account': ews_account})
    else:
        return redirect('/login/')


# 返回项目仓库镜像标签页面
def imagetagslist(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_account = request.session.get('ews_account')
        return render(request, 'repository/imageTags.html', {'ews_account': ews_account})
    else:
        return redirect('/login/')


# 项目仓库GET
@csrf_exempt
def repository(request):
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
            num = 0
            for g in groups:
                repositorys = Group.objects.get(pk=g.id).ewsrepository_set.all()
                for r in repositorys:
                    num = num + 1
                    dic = {}
                    dic['id'] = r.id
                    dic['repository'] = r.repository
                    dic['description'] = r.repository_desc
                    dic['created_time'] = r.created_time
                    dict.append(dic)
            result['code'] = 0
            result['msg'] = ""
            result['count'] = num
            result['data'] = dict
            return JsonResponse(result, safe=False)


#  获取公有仓库的所有镜像
@csrf_exempt
def get_repositorypublist(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        images = EwsRepositoryPub.objects.all()
        total = images.count()
        result = {}
        dict = []
        for i in images:
            dic = {}
            dic['id'] = i.id
            dic['repository'] = i.repository
            dic['desc'] = i.repository_desc
            dict.append(dic)
        result['data'] = dict
        result['total'] = total
        result['code'] = 0
        result['msg'] = ""
        return HttpResponse(json.dumps(result))
    else:
        return redirect('/login/')


# 获取公有镜像标签
@csrf_exempt
def imagetagspub(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        registry = request.GET.get('registry')
        repository = request.GET.get('repository')
        domain = EwsRegistry.objects.get(type=registry).domain

    else:
        return redirect('/login/')


# 开发、测试、发布镜像的列表
def image(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        if request.method == 'GET':
            page = request.GET.get('page')  # 分页
            rows = request.GET.get('limit')  # 每次刷新行数
            registry = request.GET.get('registry')  # 获取注册服务器
            repository = request.GET.get('repository')  # 获取查询仓库
            result = {}
            result['code'] = 0
            result['count'] = 0
            result['msg'] = ""
            result['data'] = ""
            # 从请求头中获取token
            registry_token = 'Bearer ' + str(request.META.get('HTTP_REGISTRY_TOKEN', None))
            registry_realm = EwsRegistry.objects.get(type=registry).domain



            try:
                pass
            except urllib.error.HTTPError as ex:
                if ex.code == 401:
                    # 获取response的头部信息
                    www_authenticate = ex.headers['Www-Authenticate']
                    www_authenticate = www_authenticate[7:].split(',')
                    dict = {}
                    for auth in www_authenticate:
                        # 拆分key=value，去除双引号，组成字典
                        dict[auth.split('=')[0]] = re.sub('"', '', auth.split('=')[1])

                    # token认证请求所需参数
                    realm = dict['realm']
                    service = dict['service']
                    scope = dict['scope']
                    user = 'wangyj'
                    password = '123456'

                    try:
                        req_token = RegistryAuth(realm, service, scope, user, password)
                        req_token = req_token.get_registry_token()
                        # 还剩像registry发请求
                    except urllib.error.HTTPError as ex:
                        if ex.code == 401:
                            result['code'] = 401
                            return JsonResponse(result, safe=False)
            return JsonResponse(result, safe=False)


# 开发、测试、发布镜像标签
def imagetag(request):
    pass
    result = {}
    result['code'] = 0
    result['count'] = 0
    result['msg'] = ""
    result['data'] = ""
    return JsonResponse(result)