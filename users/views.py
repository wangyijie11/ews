from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.models import User, Group
import json


# Create your views here.
# 用户登录
def login(request):
    if request.session.get('is_login', None):
        return redirect('/dashboard/')
    if request.method == "POST":

        account = request.POST.get('account', None)
        password = request.POST.get('password', None)
        user = auth.authenticate(username=account, password=password)  # 验证用户名和密码，返回用户对象
        accountid = User.objects.get(username=account).id
        groups = User.objects.get(pk=accountid).groups.all()
        groupid = groups[0].id
        groupname = groups[0].name
        if user:  # 如果用户对象存在
            auth.login(request, user)  # 用户登陆
            request.session['is_login'] = True
            request.session['ews_account'] = account
            request.session['ews_accountid'] = accountid
            request.session['ews_groupid'] = groupid
            request.session['ews_groupname'] = groupname
            request.session.set_expiry(6000)
            return HttpResponse(json.dumps({'status': 0}))
        else:
            return HttpResponse(json.dumps({'status': 1}))
    return render(request, 'login.html')


# 注销
def logout(request):
    if not request.session.get('is_login', False):
        return redirect('/login/')
    auth.logout(request)  # 注销用户
    return redirect('/login/')


def dashboard(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_username = request.session.get('ews_account')
        ews_groupname = request.session.get('ews_groupname')
        return render(request, 'dashboard.html', {'ews_account': ews_username, 'ews_groupname': ews_groupname})
    else:
        return redirect('/login/')


# 用户列表
def userlist(request):
    pass
    return render(request, 'users/userlist.html', locals())


# 用户组列表
def grouplist(request):
    pass
    return render(request, 'users/grouplist.html', locals())


# 获取登录用户所在的所有用户组
def get_usergroup(request):
    ews_accountid = request.session.get('ews_accountid')
    groups = User.objects.get(pk=ews_accountid).groups.all()
    groupdict = {}
    grouplist = []
    for g in groups:
        dic = {}
        dic['group_id'] = g.id
        dic['group_name'] = g.name
        grouplist.append(dic)
    groupdict['data'] = grouplist
    groupdict['total'] = groups.count()
    return JsonResponse(groupdict, safe=False)