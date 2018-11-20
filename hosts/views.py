from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from . import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from hosts.models import EwsHost
from django.contrib.auth.models import User, Group
import docker
from hosts.hostmgr import Centos7
import paramiko
import time
from django.http import QueryDict


# Create your views here.
def hostlist(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_account = request.session.get('ews_account')
        return render(request, 'hosts/hostlist.html', {'ews_account': ews_account})
    else:
        return redirect('/login/')


def firewall(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_account = request.session.get('ews_account')
        return render(request, 'hosts/firewall.html', {'ews_account': ews_account})
    else:
        return redirect('/login/')


def imagelist(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_account = request.session.get('ews_account')
        return render(request, 'hosts/imagelist.html', {'ews_account': ews_account})
    else:
        return redirect('/login/')


def containerlist(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_account = request.session.get('ews_account')
        return render(request, 'hosts/containerlist.html', {'ews_account': ews_account})
    else:
        return redirect('/login/')


# 获取主机列表
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
        dic['tab_groupname'] = Group.objects.get(pk=h.tab_group_id).name
        dict.append(dic)
    resultdict['code'] = 0
    resultdict['msg'] = ""
    resultdict['count'] = total
    resultdict['data'] = dict
    return JsonResponse(resultdict, safe=False)


# 远程获取主机信息
def get_hostinfo(host, port, user, password):
    session = Centos7(host, port, user, password)  # 类Centos7的connect方法需要改成ssh连接
    hostname = session.get_hostname()
    cpuinfo = session.get_cpuinfo()
    memory = session.get_memory()
    version = session.get_version()
    disk = session.get_disk()
    data = {'hostname': hostname, 'cpuinfo': cpuinfo, 'memory': memory, 'version': version, 'disk': disk}
    return data


# 主机GET/POST，添加主机、删除主机、获取主机信息
@csrf_exempt
def host(request):
    if request.session.get('is_login', None):
        ews_accountid = request.session.get('ews_accountid')
        if request.method == 'POST':
            host = request.POST.get('host')
            port = request.POST.get('port')
            user = request.POST.get('user')
            password = request.POST.get('password')
            ews_groupid = request.POST.get('ews_groupid')
            try:
                # 添加公钥
                # if not add_pubkey(host, port, user, password):
                #     return HttpResponse(json.dumps({"status": 1}))
                data = get_hostinfo(host, port, user, password)
                if data:
                    new_host = models.EwsHost()
                    new_host.ip = host
                    new_host.hostname = data['hostname']
                    new_host.disk = data['disk']
                    new_host.memory = data['memory']
                    new_host.os = data['version']
                    new_host.cpu_cores = data['cpuinfo']
                    new_host.created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    new_host.tab_user_id = ews_accountid
                    new_host.tab_group_id = ews_groupid
                    new_host.ssh_port = int(port)
                    new_host.ssh_user = user
                    new_host.ssh_password = password
                    new_host.save()
                    return HttpResponse(json.dumps({"status": 0}))
                else:
                    return HttpResponse(json.dumps({"status": 2}))
            except Exception as ex:
                return HttpResponse(json.dumps({"status": 3}))

        if request.method == 'DELETE':
            id = QueryDict(request.body).get('id')
            try:
                if any(id):
                    EwsHost.objects.filter(pk=id).delete()
                    return HttpResponse(json.dumps({"status": 0}))
                else:
                    return HttpResponse(json.dumps({"status": 1}))
            except Exception as ex:
                return HttpResponse(json.dumps({"status": 2}))


# 更新主机备注信息
@csrf_exempt
def post_desc(request):
    if request.session.get('is_login', None):
        if request.method == 'POST':
            desc = request.POST.get('desc')
            id = request.POST.get('id')
            try:
                if EwsHost.objects.filter(pk=id).update(description=desc):
                    return HttpResponse(json.dumps({"status": 0}))
            except Exception as ex:
                return HttpResponse(json.dumps({"status": 1}))


# 获取镜像列表
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


# 获取容器列表
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
