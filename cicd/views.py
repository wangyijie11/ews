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
            try:
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
            except Exception as ex:
                result['code'] = 1
                result['msg'] = ""
                result['count'] = 0
                result['data'] = ""
                return JsonResponse(result, safe=False)


        if request.method == 'POST':
            cicd_url = request.POST.get('cicd_url')
            cicd_user = request.POST.get('cicd_user')
            cicd_passwd = request.POST.get('cicd_passwd')
            cicd_desc = request.POST.get('cicd_desc')

            if cicd_url and cicd_user and cicd_passwd:
                # Jenkins对象
                try:
                    if Jenkins(cicd_url, username=cicd_user, password=cicd_passwd):
                        new_cicd = EwsCicd()
                        new_cicd.cicd_user = cicd_user
                        new_cicd.cicd_passwd = cicd_passwd
                        new_cicd.cicd_url = cicd_url
                        new_cicd.description = cicd_desc
                        new_cicd.created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                        new_cicd.tab_user_id = ews_accountid
                        new_cicd.save()
                        return HttpResponse(json.dumps({"status": 0, "msg": "接入成功"}))
                except Exception as ex:
                    return HttpResponse(json.dumps({"status": 1, "msg": "账号认证不通过"}))
                    print(ex)
            else:
                return HttpResponse(json.dumps({"status": 2, "msg": "缺少请求参数"}))

        if request.method == 'DELETE':
            id = QueryDict(request.body).get('id')
            try:
                if any(id):
                    EwsCicd.objects.filter(pk=id).delete()
                    return HttpResponse(json.dumps({"status": 0}))
                else:
                    return HttpResponse(json.dumps({"status": 1}))
            except Exception as ex:
                return HttpResponse(json.dumps({"status": 2}))


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
            cicdobj = EwsCicd.objects.get(pk=cicdid)

            cicd_url = cicdobj.cicd_url
            cicd_user = cicdobj.cicd_user
            cicd_passwd = cicdobj.cicd_passwd
            try:
                # Jenkins对象
                cicdsession = Jenkins(cicd_url, username=cicd_user, password=cicd_passwd)
                for job_name, job_instance in cicdsession.get_jobs():
                    dic = {}
                    dic['job_name'] = job_instance.name
                    dic['job_desc'] = job_instance.get_description()
                    # 以下两行代码运行慢
                    # dic['isrunning'] = job_instance.is_running()
                    # dic['isenabled'] = job_instance.is_enabled()
                    dict.append(dic)
                total = len(dict)
                dict = dict[i:j]
                result['code'] = 0
                result['msg'] = ""
                result['count'] = total
                result['data'] = dict
                return JsonResponse(result, safe=False)
            except jenkinsapi.jenkins.JenkinsAPIException as ex:
                print(ex)
