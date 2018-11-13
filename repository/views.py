from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from . import models
from django.http import JsonResponse
import time
from repository.models import EwsRegistry, EwsRepository, EwsRepositoryPub


# Create your views here.
def repository_pub(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_account = request.session.get('ews_account')
        ews_groupname = request.session.get('ews_groupname')
        return render(request, 'repository/repositoryPub.html', {'ews_account': ews_account, 'ews_groupname': ews_groupname})
    else:
        return redirect('/login/')


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


# 获取公有、开发、测试、发布仓库的镜像标签
@csrf_exempt
def get_imageTags(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        registry = request.GET.get('registry')
        repository = request.GET.get('repository')
        domain = EwsRegistry.objects.get(type=registry).domain

    else:
        return redirect('/login/')
