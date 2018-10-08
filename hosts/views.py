from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from . import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from hosts.models import EwsHost
import docker
from hosts.hostmgr import Centos7
import paramiko

# Create your views here.


def hostlist(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_username = request.session.get('ews_username')
        return render(request, 'hosts/hostlist.html', {'ews_username': ews_username})
    else:
        return redirect('/login/')


def firewall(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_username = request.session.get('ews_username')
        return render(request, 'hosts/firewall.html', {'ews_username': ews_username})
    else:
        return redirect('/login/')


def imagelist(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_username = request.session.get('ews_username')
        return render(request, 'hosts/imagelist.html', {'ews_username': ews_username})
    else:
        return redirect('/login/')


def containerlist(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_username = request.session.get('ews_username')
        return render(request, 'hosts/containerlist.html', {'ews_username': ews_username})
    else:
        return redirect('/login/')


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


# 获取主机信息
def get_hostinfo(host, port, user, password):
    session = Centos7(host, port, user, password)  # 类Centos7的connect方法需要改成ssh连接
    hostname = session.get_hostname()
    cpuinfo = session.get_cpuinfo()
    memory = session.get_memory()
    version = session.get_memory()
    disk = session.get_disk()
    data = {'hostname': hostname, 'cpuinfo': cpuinfo, 'memory': memory, 'version': version, 'disk': disk}
    return data

# 添加公钥
def add_pubkey(host, port, user, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, port=port, username=user, password=password, timeout=5)
        ssh.exec_command('')
    except Exception as e:
        return e

# 主机GET/POST
def host(request):
    if request.session.get('is_login', None):
        if request.method == 'POST':
            host = request.POST.get('host')
            port = request.POST.get('port')
            user = request.POST.get('user')
            password = request.POST.get('password')
            try:
                add_pubkey(host, port, user, password)
                get_hostinfo(host, port, user, password)
            except Exception as e:
                return e










@csrf_exempt
def get_imagelist(request):
    page = request.GET.get('page')
    rows = request.GET.get('limit')
    id = request.GET.get('id')
    ip = EwsHost.objects.get(pk=id).ip
    i = (int(page) - 1) * int(rows)
    j = (int(page) - 1) * int(rows) + int(rows)
    # 根据ip，调用docker engine api获取镜像
    client = docker.DockerClient(base_url='tcp://' + ip + ':2375')
    images = client.images.list()
    total = len(images)
    images = images[i:j]
    resultdict = {}
    dict = []
    for img in images:
        dic = {}
        dic['short_id'] = img.short_id
        dic['repotag'] = img.attrs.get('RepoTags')
        dict.append(dic)
    resultdict['code'] = 0
    resultdict['msg'] = ""
    resultdict['count'] = total
    resultdict['data'] = dict
    return JsonResponse(resultdict, safe=False)


@csrf_exempt
def get_containerlist(request):
    page = request.GET.get('page')
    rows = request.GET.get('limit')
    id = request.GET.get('id')
    ip = EwsHost.objects.get(pk=id).ip
    i = (int(page) - 1) * int(rows)
    j = (int(page) - 1) * int(rows) + int(rows)
    # 根据ip，调用docker engine api获取容器
    client = docker.DockerClient(base_url='tcp://' + ip + ':2375')
    containers = client.containers.list()
    total = len(containers)
    containers = containers[i:j]
    resultdict = {}
    dict = []
    for cont in containers:
        dic = {}
        dic['short_id'] = cont.short_id
        dic['name'] = cont.name
        dic['status'] = cont.status
        dict.append(dic)
    resultdict['code'] = 0
    resultdict['msg'] = ""
    resultdict['count'] = total
    resultdict['data'] = dict
    return JsonResponse(resultdict, safe=False)