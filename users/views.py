from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from users.models import EwsUser, EwsGroup, EwsUserGroup
from django.shortcuts import HttpResponse
import json


# Create your views here.
# 用户登录
def login(request):
    if request.session.get('is_login', None):
        return redirect('/dashboard/')

    if request.method == "POST":
        account = request.POST.get('account', None)
        password = request.POST.get('password', None)
        if account and password:  # 确保用户名和密码都不为空
            account = account.strip()
            try:
                user = EwsUser.objects.get(account=account)
                username = EwsUser.objects.get(account=account).username
                if user.password == password:
                    request.session['is_login'] = True
                    request.session['ews_account'] = account
                    request.session['ews_username'] = username
                    request.session.set_expiry(6000)
                    return HttpResponse(json.dumps({
                        "status": 1,  # 正确登录
                    }))
                else:
                    return HttpResponse(json.dumps({
                        "status": 2,  # 密码错误
                    }))
            except:
                return HttpResponse(json.dumps({
                    "status": 0,  # 用户不存在
                }))
        return HttpResponse(json.dumps({
                    "status": 3,  # 用户名或密码为空
                }))
    return render(request, 'login.html')


# 注销
def logout(request):
    if not request.session.get('is_login', False):
        return redirect('/login/')
    request.session.flush()
    return redirect('/login/')


def dashboard(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_username = request.session.get('ews_username')
        return render(request, 'dashboard.html', {'ews_username': ews_username})
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
