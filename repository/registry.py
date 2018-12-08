import urllib.request, urllib.response, urllib.error, urllib.parse
from django.views.decorators.csrf import csrf_exempt
import requests
from requests.auth import AuthBase
from requests.auth import HTTPBasicAuth
import json
import itertools
import re


# 镜像仓库API
class RegistryApi(object):
    def __init__(self, realm, token):
        self.realm = realm
        self.token = 'Bearer ' + token

    # registry连通性测试
    def ping(self):
        url = 'http://' + self.realm + '/v2/'
        headers = {'Authorization': self.token}
        req = urllib.request.Request(url, headers=headers)
        res = urllib.request.urlopen(req)
        return res

    # 获取catalog
    def catalog(self, n, last):
        n = n
        last = last
        headers = {'Authorization': self.token}
        rows = n  # 每次查询返回的匹配数
        repository = last  # 查询的项目仓库，用于匹配
        dict = []
        while n == rows and any(last):
            url = 'http://' + self.realm + '/v2/_catalog?n=' + n + '&last=' + last
            req = urllib.request.Request(url, headers=headers)
            res = json.loads(urllib.request.urlopen(req).read().decode())  # 将Registry API返回的byte结果转成str，再转成dict
            res_list = list(itertools.chain.from_iterable(list(res.values())))  # 将Registry API返回的数据再处理成list
            project_list = []
            for r in res_list:
                dic = {}
                if r.split('/')[0] == repository:
                    project_list.append(r.split('/')[0])  # 拆分出项目名，作为统计n
                    dic['image'] = (r.split('/')[1])  # 拆分出镜像名，作为数据输出
                    dict.append(dic)
            rows = project_list.count(repository)  # Registry API参数
            if len(res_list):
                last = res_list[-1]  # Registry API参数
            else:
                last = None
        result = {}
        result['code'] = 0
        result['msg'] = ""
        result['count'] = len(dict)
        result['data'] = dict
        return result

    # 获取某个镜像的tags
    def tags(self, image):
        image = image
        url = 'http://' + self.realm + '/v2/' + image + '/tags/list'
        headers = {'Authorization': self.token}
        req = urllib.request.Request(url, headers=headers)
        res = json.loads(urllib.request.urlopen(req).read().decode())
        tags = res['tags']
        dict = []
        for t in tags:
            dic = {}
            dic['tag'] = t
            dict.append(dic)
        result = {}
        result['code'] = 0
        result['msg'] = ""
        result['count'] = len(tags)
        result['data'] = dict
        return result

    def get_www_authenticate(self, ex):
        # 获取response的头部信息
        www_authenticate = ex.headers['Www-Authenticate']
        www_authenticate = www_authenticate[7:].split(',')
        auth_server = {}
        for auth in www_authenticate:
            auth_server[auth.split('=')[0]] = re.sub('"', '', auth.split('=')[1])  # 拆分key=value，去除双引号，组成字典
        return auth_server
