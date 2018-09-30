from django.shortcuts import render
from django.shortcuts import redirect
# Create your views here.


# 登录
def gotologin(request):
    return render(request, 'login.html')


# 注销
def logout(request):
    return redirect('/login/')


def dashboard(request):
    pass
    return render(request, 'dashboard.html')


# 用户列表
def userlist(request):
    pass
    return render(request, 'users/userlist.html', locals())


# 用户组列表
def grouplist(request):
    pass
    return render(request, 'users/grouplist.html', locals())