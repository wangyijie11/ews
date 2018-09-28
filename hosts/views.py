from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from . import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from hosts.models import EwsHost
import docker

# Create your views here.


def hostlist(request):
    return render(request, 'hosts/hostlist.html', locals())


def firewall(request):
    return render(request, 'hosts/firewall.html', locals())


def imagelist(request):
    return render(request, 'hosts/imagelist.html', locals())


def containerlist(request):
    return render(request, 'hosts/containerlist.html', locals())


@csrf_exempt
def get_hostlist(request):
    page = request.GET.get('page')
    rows = request.GET.get('limit')
    i = (int(page) - 1) * int(rows)
    j = (int(page) - 1) * int(rows) + int(rows)
    hosts = EwsHost.objects.all()
    total = hosts.count()
    hosts = hosts[i:j]
    resultdict = {}
    resultdict['total'] = total
    dict = []
    for h in hosts:
        dic = {}
        dic['id'] = h.id
        dic['ip'] = h.ip
        dic['hostname'] = h.hostname
        dic['description'] = h.description
        dic['cpu_cores'] = h.cpu_cores
        dic['memory'] = h.memory
        dic['disk'] = h.disk
        dic['docker_version'] = h.docker_version
        dic['os'] = h.os
        dic['tab_user_id'] = h.tab_user_id
        dic['tab_group_id'] = h.tab_group_id
        dict.append(dic)
    resultdict['code'] = 0
    resultdict['msg'] = ""
    resultdict['count'] = total
    resultdict['data'] = dict
    return JsonResponse(resultdict, safe=False)


@csrf_exempt
def get_imagelist(request):
    page = request.GET.get('page')
    rows = request.GET.get('limit')
    id = request.GET.get('id')
    ip = EwsHost.objects.get(pk=1).ip
    i = (int(page) - 1) * int(rows)
    j = (int(page) - 1) * int(rows) + int(rows)
    # 根据ip，调用docker engine api获取镜像
    client = docker.DockerClient(base_url='tcp://' + ip + ':2375')
#    client = docker.from_env()
    images = client.images.list()
    total = images.count()
    images = images[i:j]
    resultdict = {}
    dict = []
    for img in images:
        dic = {}
        dic['id'] = img.id
        dic['image'] = img.attrs
        dic['short_id'] = img.short_id
        dict.append(dic)
    resultdict['code'] = 0
    resultdict['msg'] = ""
    resultdict['count'] = total
    resultdict['data'] = dict
    return JsonResponse(resultdict, safe=False)
