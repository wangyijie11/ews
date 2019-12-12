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


# Create your views here.
def hostlist(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_account = request.session.get('ews_account')
        return render(request, 'hosts/hostlist.html', {'ews_account': ews_account})
    else:
        return redirect('/login/')


def firewalllist(request):
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


def containerlog(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_account = request.session.get('ews_account')
        return render(request, 'hosts/containerlogs.html', {'ews_account': ews_account})
    else:
        return redirect('/login/')


# 远程获取主机信息
def get_hostinfo(host, port, user, password):
    session = Centos7(host, port, user, password)  # 类Centos7的connect方法需要改成ssh连接
    state = session.get_state()
    if state == 'Up':
        hostname = session.get_hostname()
        cpuinfo = session.get_cpuinfo()
        memory = session.get_memory()
        version = session.get_version()
        disk = session.get_disk()
        data = {'hostname': hostname, 'cpuinfo': cpuinfo, 'memory': memory, 'version': version, 'disk': disk}
        return data
    elif state == 'Down':
        return False

# 获取主机IP地址
@csrf_exempt
def get_hostip(request):
    if request.session.get('is_login', None):
        ews_accountid = request.session.get('ews_accountid')
        if request.method == 'GET':
            groups = User.objects.get(pk=ews_accountid).groups.all()
            result = {}
            dict = []
            for g in groups:
                hosts = Group.objects.get(pk=g.id).ewshost_set.all()
                for h in hosts:
                    dic = {}
                    dic['id'] = h.id
                    dic['ip'] = h.ip
                    dict.append(dic)
            total = len(dict)
            result['code'] = 0
            result['msg'] = ""
            result['count'] = total
            result['data'] = dict
            return JsonResponse(result, safe=False)

# 获取防火墙策略部署的IP地址
@csrf_exempt
def get_host_byfirewall(request):
    if request.session.get('is_login', None):
        if request.method == 'GET':
            policy_id = request.GET.get('policy_id')
            hostids = EwsFirewall.objects.get(pk=policy_id).ewshostfirewall_set.all()
            try:
                result = {}
                dict = []
                for ids in hostids:
                    dic = {}
                    dic['ip'] = ids.tab_host.ip
                    dict.append(dic)
                total = len(dict)
                result['code'] = 0
                result['msg'] = ""
                result['count'] = total
                result['data'] = dict
                return JsonResponse(result, safe=False)
            except Exception as ex:
                #运行异常
                return HttpResponse(json.dumps({"status": 1}))

# 部署防火墙策略至主机
@csrf_exempt
def applypolicy(request):
    if request.session.get('is_login', None):
        ews_accountid = request.session.get('ews_accountid')
        if request.method == 'POST':
            host_id = request.POST.get('host')
            policy_id = request.POST.get('policy')
            try:
                if host_id and policy_id:
                    host = EwsHost.objects.get(pk=host_id)
                    ssh_password = host.ssh_password
                    ssh_user = host.ssh_user
                    ssh_port = host.ssh_port

                    session = Centos7(host, ssh_port, ssh_user, ssh_password)  # 类Centos7的connect方法需要改成ssh连接
                    state = session.get_state()
                    if state == 'Up':
                        policy = EwsFirewall.objects.get(pk=policy_id)
                        policy_str = policy.policy_json
                        policy_json = json.loads(policy_str)
                        zone = policy_json['zone']
                        kind = policy_json['kind']
                        if kind == 'rich':
                            rule = policy_json['rule']
                            rule_family = policy_json['rule']['rule family']
                            source_address = policy_json['rule']['source address']
                            port = policy_json['rule']['port port']
                            protocol = policy_json['rule']['protocol']
                            accept = policy_json['rule']['accept']
                            if accept == 'True':
                                accept = 'accept'
                            cmd1 = 'firewall-cmd --permanent --zone=' + zone + ' --add-rich-rule \'rule family='\
                                   + rule_family + ' source address=' + source_address + ' port port=' + port + \
                                   ' protocol=' + protocol + ' ' + accept + '\''
                            cmd2 = 'firewall-cmd --reload'
                            if session.ssh_cmd(cmd1):
                                if session.ssh_cmd(cmd2):
                                    new_host_firewall = models.EwsHostFirewall()
                                    new_host_firewall.created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                                    new_host_firewall.policy_cmd = cmd1
                                    new_host_firewall.tab_firewall = policy_id
                                    new_host_firewall.tab_host = host_id
                                    new_host_firewall.tab_user = ews_accountid
                                    new_host_firewall.save()

                                    return HttpResponse(json.dumps({"status": 0}))
                                else:
                                    # 命令执行失败
                                    return HttpResponse(json.dumps({"status": 4}))
                            else:
                                # 命令执行失败
                                return HttpResponse(json.dumps({"status": 4}))
                        elif kind == 'port':
                            ports = policy_json['ports']
                            for port in ports:
                                cmd1 = 'firewall-cmd --permanent --zone=' + zone + ' --add-port=' + port + '/tcp'
                                cmd2 = 'firewall-cmd --reload'
                                if session.ssh_cmd(cmd1):
                                    if session.ssh_cmd(cmd2):
                                        new_host_firewall = models.EwsHostFirewall()
                                        new_host_firewall.created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                                        new_host_firewall.policy_cmd = cmd1
                                        new_host_firewall.tab_firewall = policy_id
                                        new_host_firewall.tab_host = host_id
                                        new_host_firewall.tab_user = ews_accountid
                                        new_host_firewall.save()
                                        return HttpResponse(json.dumps({"status": 0}))
                                    else:
                                        # 命令执行失败
                                        return HttpResponse(json.dumps({"status": 4}))
                                else:
                                    # 命令执行失败
                                    return HttpResponse(json.dumps({"status": 4}))
                            return HttpResponse(json.dumps({"status": 0}))
                    elif state == 'Down':
                        # 主机网络不通
                        return HttpResponse(json.dumps({"status": 1}))
                else:
                    # 前端传递参数错误
                    return HttpResponse(json.dumps({"status": 2}))
            except Exception as ex:
                #运行异常
                return HttpResponse(json.dumps({"status": 3}))
        if request.method == 'DELETE':
            pass


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
            ews_groupid = request.POST.get('groupname')
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

        if request.method == 'GET':
            groups = User.objects.get(pk=ews_accountid).groups.all()
            page = request.GET.get('page')
            rows = request.GET.get('limit')
            i = (int(page) - 1) * int(rows)
            j = (int(page) - 1) * int(rows) + int(rows)
            result = {}
            dict = []
            for g in groups:
                hosts = Group.objects.get(pk=g.id).ewshost_set.all()
                for h in hosts:
                    # 获取主机动态状态
                    #session = Centos7(h.ip, h.ssh_port, h.ssh_user, h.ssh_password)  # 类Centos7的connect方法需要改成ssh连接
                    #state = session.get_state()
                    # 查询太慢，先注释
                    #cpu_state = session.get_cpustate()
                    #memory_state = session.get_memorystate()
                    #disk_state = session.get_diskstate()

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
                    dic['state'] = 'N/A'
                    #dic['cpu_state'] = cpu_state
                    #dic['memory_state'] = memory_state
                    #dic['disk_state'] = disk_state
                    dict.append(dic)
            total = len(dict)
            dict = dict[i:j]
            result['code'] = 0
            result['msg'] = ""
            result['count'] = total
            result['data'] = dict
            return JsonResponse(result, safe=False)


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


# 镜像GET/DELETE
@csrf_exempt
def image(request):
    if request.session.get('is_login', None):
        if request.method == 'GET':
            page = request.GET.get('page')
            rows = request.GET.get('limit')
            id = request.GET.get('hostid')
            imageid = request.GET.get('imageid')
            ip = EwsHost.objects.get(pk=id).ip
            if imageid:
                try:
                    client = DockerClient(base_url='tcp://' + ip + ':2375')
                    imageinfo = client.images.get(imageid).attrs
                    return HttpResponse(json.dumps(imageinfo))
                except Exception as ex:
                    return HttpResponse(json.dumps({"API调用异常"}))
            elif not imageid:
                i = (int(page) - 1) * int(rows)
                j = (int(page) - 1) * int(rows) + int(rows)
                # 根据ip，调用docker engine api获取镜像
                client = DockerClient(base_url='tcp://' + ip + ':2375')
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
        if request.method == 'DELETE':
            imageid = QueryDict(request.body).get('imageid')
            hostid = QueryDict(request.body).get('hostid')
            ip = EwsHost.objects.get(pk=hostid).ip
            if (not imageid) or (not ip):
                return HttpResponse(json.dumps({"status": 2, "msg": "缺少变量imageid和hostid"}))
            try:
                client = DockerClient(base_url='tcp://' + ip + ':2375')
                client.images.remove(imageid, force=True)
                return HttpResponse(json.dumps({"status": 0}))
            except Exception as ex:
                return HttpResponse(json.dumps({"status": 1, "msg": "API调用异常"}))


# 容器GET/DELETE
@csrf_exempt
def container(request):
    if request.session.get('is_login', None):
        if request.method == 'GET':
            page = request.GET.get('page')
            rows = request.GET.get('limit')
            hostid = request.GET.get('hostid')
            containerid = request.GET.get('containerid')
            ip = EwsHost.objects.get(pk=hostid).ip
            if containerid:
                try:
                    client = DockerClient(base_url='tcp://' + ip + ':2375')
                    containerinfo = client.containers.get(containerid).attrs
                    return HttpResponse(json.dumps(containerinfo))
                except Exception as ex:
                    return HttpResponse(json.dumps({"API调用异常"}))
            elif not containerid:
                i = (int(page) - 1) * int(rows)
                j = (int(page) - 1) * int(rows) + int(rows)
                # 根据ip，调用docker engine api获取容器
                client = DockerClient(base_url='tcp://' + ip + ':2375')
                containers = client.containers.list(all=True)
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
        if request.method == 'DELETE':
            containerid = QueryDict(request.body).get('containerid')
            hostid = QueryDict(request.body).get('hostid')
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


# 主机docker安装，卸载
@csrf_exempt
def docker(request):
    if request.session.get('is_login', None):
        ews_accountid = request.session.get('ews_accountid')
        if request.method == 'POST':
            id = request.POST.get('id')
            host = EwsHost.objects.get(pk=id)
            ip = host.ip
            port = host.ssh_port
            user = host.ssh_user
            password = host.ssh_password
            local_path = settings.DOCKER_LOCAL_PATH + settings.DOCKER_INSTALL_PKG
            remote_path = settings.DOCKER_REMOTE_PATH + settings.DOCKER_INSTALL_PKG
            try:
                session = Centos7(host, port, user, password)
                if session.sftp_put(local_path, remote_path):  # docker安装包传输
                    cmd1 = 'source ~/.bashrc; cd ' + settings.DOCKER_REMOTE_PATH + '; tar zxf ' + settings.DOCKER_INSTALL_PKG  # 解压安装包
                    if session.ssh_cmd(cmd1):
                        cmd2 = 'source ~/.bashrc; cd ' + settings.DOCKER_REMOTE_PATH + 'ews/; bash install.sh'  # 安装docker
                        if session.ssh_cmd(cmd2):
                            return HttpResponse(json.dumps({"status": 0}))  # 安装成功
                        else:
                            return HttpResponse(json.dumps({"status": 3}))  # 安装失败
                    else:
                        return HttpResponse(json.dumps({"status": 2}))  # 文件解压失败
                else:
                    return HttpResponse(json.dumps({"status": 1}))  # 文件传输失败
            except Exception as ex:
                return HttpResponse(json.dumps({"status": 4}))  # 程序性运行出错


@csrf_exempt
def firewall(request):
    if request.session.get('is_login', None):
        ews_accountid = request.session.get('ews_accountid')
        if request.method == 'GET':

            groups = User.objects.get(pk=ews_accountid).groups.all()
            page = request.GET.get('page')
            rows = request.GET.get('limit')
            i = (int(page) - 1) * int(rows)
            j = (int(page) - 1) * int(rows) + int(rows)
            result = {}
            dict = []
            for g in groups:
                policies = Group.objects.get(pk=g.id).ewsfirewall_set.all()
                for p in policies:
                    dic = {}
                    dic['policy_id'] = p.id
                    dic['policy_name'] = p.policy_name
                    dic['policy_json'] = p.policy_json
                    dic['kind'] = p.kind
                    dic['created_time'] = p.created_time
                    dic['count'] = EwsFirewall.objects.get(pk=p.id).ewshostfirewall_set.all().count()
                    dic['iscustomize'] = p.iscustomize
                    dict.append(dic)
            total = len(dict)
            dict = dict[i:j]
            result['code'] = 0
            result['msg'] = ""
            result['count'] = total
            result['data'] = dict
            return JsonResponse(result, safe=False)
        if request.method == 'DELETE':
            id = QueryDict(request.body).get('id')
            try:
                if any(id):
                    EwsFirewall.objects.filter(pk=id).delete()
                    return HttpResponse(json.dumps({"status": 0}))
                else:
                    return HttpResponse(json.dumps({"status": 1}))
            except Exception as ex:
                return HttpResponse(json.dumps({"status": 2}))

#添加防火墙端口开放规则
@csrf_exempt
def firewallport(request):
    if request.session.get('is_login', None):
        if request.method == 'POST':
            ews_accountid = request.session.get('ews_accountid')
            ews_groupid = request.POST.get('groupname')
            port = request.POST.get('port')
            policy = request.POST.get('policy')
            zone = request.POST.get('zone')
            default_zone = 'public'
            kind = 'port'
            if not zone:
                zone = default_zone

            try:
                policy_json = {"zone": zone, "kind": kind, "ports": port}
                new_policy = models.EwsFirewall()
                new_policy.kind = kind
                new_policy.policy_name = policy
                new_policy.policy_json = policy_json
                new_policy.created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                new_policy.tab_group_id = ews_groupid
                new_policy.tab_user_id = ews_accountid
                new_policy.iscustomize = 0
                new_policy.save()
                return HttpResponse(json.dumps({"status": 0}))

            except Exception as ex:
                return HttpResponse(json.dumps({"status": 1}))

# 添加防火墙端口开放富规则
@csrf_exempt
def firewallrich(request):
    if request.session.get('is_login', None):
        if request.method == 'POST':
            ews_accountid = request.session.get('ews_accountid')
            ews_groupid = request.POST.get('groupname')
            sourceip = request.POST.get('sourceip')
            destinationport = request.POST.get('destinationport')
            isallow = request.POST.get('isallow')
            policy = request.POST.get('policy')
            zone = request.POST.get('zone')
            default_zone = 'public'
            kind = 'rich'
            if not zone:
                zone = default_zone

            try:
                policy_json = {"zone": zone, "kind": kind, "rule": {"rule family": "ipv4", "source address": sourceip, "port port": destinationport, "protocol": "tcp", "accept": isallow}}
                new_policy = models.EwsFirewall()
                new_policy.kind = kind
                new_policy.policy_name = policy
                new_policy.policy_json = policy_json
                new_policy.created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                new_policy.tab_group_id = ews_groupid
                new_policy.tab_user_id = ews_accountid
                new_policy.iscustomize = 0
                new_policy.save()
                return HttpResponse(json.dumps({"status": 0}))

            except Exception as ex:
                return HttpResponse(json.dumps({"status": 1}))

# 主机状态 异步刷新，写了暂时没用
@csrf_exempt
def hostmonitor(request):
    if request.session.get('is_login', None):
        id = request.GET.get('id')
        obj = EwsHost.objects.get(pk=id)
        host = obj.ip
        port = obj.ssh_port
        user = obj.ssh_user
        password = obj.ssh_password
        try:
            session = Centos7(host, port, user, password)  # 类Centos7的connect方法需要改成ssh连接
            cpu_state = session.get_cpustate()
            memory_state = session.get_memorystate()
            disk_state = session.get_diskstate()
            if [any(cpu_state) and any(memory_state) and any(disk_state)]:
                data = {'status': 0, 'cpu_state': cpu_state, 'memory_state': memory_state, 'disk_state': disk_state}
            else:
                data = {'status': 1}
            return HttpResponse(json.dumps(data))
        except Exception as ex:
            data = {'status': 2}
            return HttpResponse(json.dumps(data))