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
        if user:  # 如果用户对象存在
            auth.login(request, user)  # 用户登陆
            request.session['is_login'] = True
            request.session['ews_account'] = account
            request.session['ews_accountid'] = accountid

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
        return render(request, 'dashboard.html', {'ews_account': ews_username})
    else:
        return redirect('/login/')


# 返回用户列表
def userlist(request):
    is_login = request.session.get('is_login', False)
    if is_login:
        ews_username = request.session.get('ews_account')
        return render(request, 'users/userlist.html', {'ews_account': ews_username})
    else:
        return redirect('/login/')


# 用户组列表
def grouplist(request):
    pass
    return render(request, 'users/grouplist.html', locals())


# 获取登录用户所在的所有用户组
def get_grouplist(request):
    ews_accountid = request.session.get('ews_accountid')
    groups = User.objects.get(pk=ews_accountid).groups.all()
    groupdict = {}
    grouplist = []
    for g in groups:
        dic = {}
        dic['id'] = g.id
        dic['groupname'] = g.name
        grouplist.append(dic)
    groupdict['code'] = 0
    groupdict['msg'] = ""
    groupdict['data'] = grouplist
    groupdict['total'] = groups.count()
    return JsonResponse(groupdict, safe=False)


# 获取用户组内成员信息
@csrf_exempt
def get_userlist(request):
    ews_groupid = request.GET.get('ews_groupid')
    page = request.GET.get('page')
    rows = request.GET.get('limit')
    i = (int(page) - 1) * int(rows)
    j = (int(page) - 1) * int(rows) + int(rows)
    users = Group.objects.get(pk=ews_groupid).user_set.all()
    total = users.count()
    users = users[i:j]
    resultdict = {}
    dict = []
    for u in users:
        dic = {}
        dic['id'] = u.id
        dic['username'] = u.username
        dic['name'] = u.last_name + u.first_name
        dict.append(dic)
    resultdict['data'] = dict
    resultdict['count'] = total
    resultdict['code'] = 0
    resultdict['msg'] = ""
    return JsonResponse(resultdict, safe=False)
