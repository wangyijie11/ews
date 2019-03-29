from django.shortcuts import render

# Create your views here.
import json
import docker
from docker import DockerClient
from django.views.decorators.csrf import csrf_exempt
from hosts.models import EwsHost
from django.shortcuts import HttpResponse


@csrf_exempt
def container_run():
    pass


@csrf_exempt
def container_start(request):
    if request.session.get('is_login', None):
        if request.method == 'POST':
            containerid = request.POST.get('containerid')
            hostid = request.POST.get('hostid')
            ip = EwsHost.objects.get(pk=hostid).ip
            if (not containerid) or (not ip):
                return HttpResponse(json.dumps({"status": 2, "msg": "缺少变量containerid和hostid"}))
            try:
                client = DockerClient(base_url='tcp://' + ip + ':2375')
                containerins = client.containers.get(containerid)
                containerins.start()
                return HttpResponse(json.dumps({"status": 0}))
            except Exception as ex:
                return HttpResponse(json.dumps({"status": 1, "msg": "API调用异常"}))


@csrf_exempt
def container_stop(request):
    if request.session.get('is_login', None):
        if request.method == 'POST':
            containerid = request.POST.get('containerid')
            hostid = request.POST.get('hostid')
            ip = EwsHost.objects.get(pk=hostid).ip
            if (not containerid) or (not ip):
                return HttpResponse(json.dumps({"status": 2, "msg": "缺少变量containerid和hostid"}))
            try:
                client = DockerClient(base_url='tcp://' + ip + ':2375')
                containerins = client.containers.get(containerid)
                containerins.stop()
                return HttpResponse(json.dumps({"status": 0}))
            except Exception as ex:
                return HttpResponse(json.dumps({"status": 1, "msg": "API调用异常"}))


@csrf_exempt
def container_restart(request):
    if request.session.get('is_login', None):
        if request.method == 'POST':
            containerid = request.POST.get('containerid')
            hostid = request.POST.get('hostid')
            ip = EwsHost.objects.get(pk=hostid).ip
            if (not containerid) or (not ip):
                return HttpResponse(json.dumps({"status": 2, "msg": "缺少变量containerid和hostid"}))
            try:
                client = DockerClient(base_url='tcp://' + ip + ':2375')
                containerins = client.containers.get(containerid)
                containerins.restart()
                return HttpResponse(json.dumps({"status": 0}))
            except Exception as ex:
                return HttpResponse(json.dumps({"status": 1, "msg": "API调用异常"}))


@csrf_exempt
def container_remove(request):
    if request.session.get('is_login', None):
        if request.method == 'POST':
            containerid = request.POST.get('containerid')
            hostid = request.POST.get('hostid')
            ip = EwsHost.objects.get(pk=hostid).ip
            if (not containerid) or (not ip):
                return HttpResponse(json.dumps({"status": 2, "msg": "缺少变量containerid和hostid"}))
            try:
                client = DockerClient(base_url='tcp://' + ip + ':2375')
                containerins = client.containers.get(containerid)
                containerins.remove(v=True, force=True)
                return HttpResponse(json.dumps({"status": 0}))
            except Exception as ex:
                return HttpResponse(json.dumps({"status": 1, "msg": "API调用异常"}))


@csrf_exempt
def container_logs(request):
    if request.session.get('is_login', None):
        if request.method == 'POST':
            containerid = request.POST.get('containerid')
            hostid = request.POST.get('hostid')
            ip = EwsHost.objects.get(pk=hostid).ip
            if (not containerid) or (not ip):
                return HttpResponse(json.dumps({"status": 2, "msg": "缺少变量containerid和hostid"}))
            try:
                client = DockerClient(base_url='tcp://' + ip + ':2375')
                containerins = client.containers.get(containerid)
                str_out = containerins.logs(tail=200).decode()
                return HttpResponse(json.dumps({"status": 0, "msg": "成功", "data": str_out}))
            except Exception as ex:
                print(ex)
                return HttpResponse(json.dumps({"status": 1, "msg": "API调用异常"}))

