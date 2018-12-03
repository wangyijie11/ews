import urllib.request, urllib.response, urllib.error, urllib.parse
from django.views.decorators.csrf import csrf_exempt
import requests
from requests.auth import AuthBase
from requests.auth import HTTPBasicAuth
import json


# 镜像仓库API
class RegistryApi(object):
    def __init__(self, realm, token):
        self.realm = realm
        self.token = token

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
        if n and last:
            url = 'http://' + self.realm + '/v2/_catalog?n=' + n + '&last=' + last
        elif not n and last:
            url = 'http://' + self.realm + '/v2/_catalog?last=' + last
        elif n and not last:
            url = 'http://' + self.realm + '/v2/_catalog?n=' + n
        else:
            url = 'http://' + self.realm + '/v2/_catalog'

        headers = {'Authorization': self.token}
        req = urllib.request.Request(url, headers=headers)
        res = urllib.request.urlopen(req)
        return res

    # 获取某个镜像的tags
    def tags(self, image):
        image = image
        url = 'http://' + self.realm + '/v2/' + image + '/tags/list'
        headers = {'Authorization': self.token}
        req = urllib.request.Request(url, headers=headers)
        res = urllib.request.urlopen(req)
        return res

