from django.shortcuts import render
from django.conf import settings
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from cicd.models import EwsCicd
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
import time
from django.http import QueryDict
import jenkinsapi
from jenkinsapi.jenkins import Jenkins


# Create your views here.
# 返回持续集成用户页面
def cicdlist(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_account = request.session.get('ews_account')
        return render(request, 'cicd/cicdlist.html', {'ews_account': ews_account})
    else:
        return redirect('/login/')


# 返回持续集成任务页面
def cicdjoblist(request):
    is_login = request.session.get('is_login', False)  # 获取session里的值
    if is_login:
        ews_account = request.session.get('ews_account')
        return render(request, 'cicd/cicdjoblist.html', {'ews_account': ews_account})
    else:
        return redirect('/login/')


# 持续集成账号信息GET/POST/DELETE
@csrf_exempt
def cicd(request):
    if request.session.get('is_login', None):
        ews_accountid = request.session.get('ews_accountid')
        if request.method == 'GET':
            page = request.GET.get('page')
            rows = request.GET.get('limit')
            i = (int(page) - 1) * int(rows)
            j = (int(page) - 1) * int(rows) + int(rows)
            result = {}
            dict = []
            cicds = EwsCicd.objects.filter(tab_user_id=ews_accountid)
            for c in cicds:
                dic = {}
                dic['id'] = c.id
                dic['cicd_user'] = c.cicd_user
                dic['cicd_url'] = c.cicd_url
                dic['description'] = c.description
                dict.append(dic)
            total = len(dict)
            dict = dict[i:j]
            result['code'] = 0
            result['msg'] = ""
            result['count'] = total
            result['data'] = dict
            return JsonResponse(result, safe=False)


# 持续集成任务GET
@csrf_exempt
def cicdjob(request):
    if request.session.get('is_login', None):
        ews_accountid = request.session.get('ews_accountid')
        if request.method == 'GET':
            page = request.GET.get('page')
            rows = request.GET.get('limit')
            cicdid = request.GET.get('cicd')
            i = (int(page) - 1) * int(rows)
            j = (int(page) - 1) * int(rows) + int(rows)
            result = {}
            dict = []
            cicdObj = EwsCicd.objects.get(pk=cicdid)
            # Jenkins对象
            cicd_url = cicdObj.cicd_url
            cicd_user = cicdObj.cicd_user
            cicd_passwd = cicdObj.cicd_passwd
            cicdSession = Jenkins(cicd_url, username=cicd_user, password=cicd_passwd)
            cicdSession.get_jobs()

            pass
