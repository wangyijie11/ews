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
        ews_account = request.session.get('ews_account')
        if request.method == 'GET':
            page = request.GET.get('page')  # 分页
            rows = request.GET.get('limit')  # 每次刷新行数
            registry = request.GET.get('registry')  # 获取注册服务器
            repository = request.GET.get('repository')  # 获取查询仓库
            registry_token = str(request.META.get('HTTP_REGISTRY_TOKEN', None))  # 从请求头中获取token
            registry_realm = EwsRegistry.objects.get(type=registry).domain
            try:
                registry_api = RegistryApi(registry_realm, registry_token)  # 生成Registry API对象
                result = registry_api.catalog(rows, repository)
                return JsonResponse(result, safe=False)
            except urllib.error.HTTPError as ex:
                # print(ex.headers)
                if ex.code == 401:

                    auth_server = registry_api.get_www_authenticate(ex)
                    # token认证请求所需参数
                    realm = auth_server['realm']
                    service = auth_server['service']
                    scope = auth_server['scope']
                    user = ews_account
                    password = User.objects.get(username=ews_account).password  # 无法破解密码为明文，用密文作为token请求认证密码

                    try:
                        req_token = RegistryAuth(realm, service, scope, user, password)
                        new_registry_token = req_token.get_registry_token()
                        new_registry_api = RegistryApi(registry_realm, new_registry_token)
                        result = new_registry_api.catalog(rows, repository)
                        return JsonResponse(result, safe=False)

                    except urllib.error.HTTPError as ex:
                        if ex.code == 401:
                            result = {}
                            result['code'] = 401
                            result['msg'] = '未授权'
                            return JsonResponse(result, safe=False)
                else:
                    result = {}
                    result['code'] = 500
                    result['msg'] = '内部错误'
                    return JsonResponse(result, safe=False)


# 开发、测试、发布镜像标签
def imagetag(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_account = request.session.get('ews_account')
        if request.method == 'GET':
            page = request.GET.get('page')  # 分页
            rows = request.GET.get('limit')  # 每次刷新行数
            registry = request.GET.get('registry')  # 获取注册服务器
            image = request.GET.get('image')  # 获取镜像名，包含仓库名
            registry_token = str(request.META.get('HTTP_REGISTRY_TOKEN', None))  # 从请求头中获取token
            registry_realm = EwsRegistry.objects.get(type=registry).domain
            try:
                registry_api = RegistryApi(registry_realm, registry_token)  # 生成Registry API对象
                result = registry_api.tags(image)
                return JsonResponse(result, safe=False)
            except urllib.error.HTTPError as ex:
                if ex.code == 401:
                    auth_server = registry_api.get_www_authenticate(ex)
                    # token认证请求所需参数
                    realm = auth_server['realm']
                    service = auth_server['service']
                    scope = auth_server['scope']
                    user = ews_account
                    password = User.objects.get(username=ews_account).password  # 无法破解密码为明文，用密文作为token请求认证密码

                    try:
                        req_token = RegistryAuth(realm, service, scope, user, password)
                        new_registry_token = req_token.get_registry_token()
                        new_registry_api = RegistryApi(registry_realm, new_registry_token)
                        result = new_registry_api.tags(image)
                        return JsonResponse(result, safe=False)

                    except urllib.error.HTTPError as ex:
                        if ex.code == 401:
                            result = {}
                            result['code'] = 401
                            result['msg'] = '未授权'
                            return JsonResponse(result, safe=False)
                else:
                    result = {}
                    result['code'] = 500
                    result['msg'] = '内部错误'
                    return JsonResponse(result, safe=False)


