import urllib.request, urllib.response, urllib.error, urllib.parse
from django.views.decorators.csrf import csrf_exempt
import requests
from requests.auth import AuthBase
from requests.auth import HTTPBasicAuth
import json


# 镜像仓库token认证请求类
class RegistryAuth(object):
    def __init__(self, realm, service, scope, user, password):
        self.realm = realm
        self.service = service
        self.scope = scope
        self.user = user
        self.password = password

    # 获取token
    def get_registry_token(self):
        auth_url = self.get_auth_url()
        basic_auth = self.get_basic_auth()
        res_auth = requests.post(url=auth_url, auth=basic_auth, verify=False)
        token = json.loads(res_auth.text)
        return token

    # 封装url
    def get_auth_url(self):
        auth_url = self.realm + '?service=' + self.service + '&scope=' + self.scope
        return auth_url

    # 封装HTTP BASIC AUTH
    def get_basic_auth(self):
        basic_auth = HTTPBasicAuth(self.user, self.password)
        return basic_auth
