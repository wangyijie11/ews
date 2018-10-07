import paramiko
from subprocess import Popen, PIPE
import re
import os, sys
from django.http import JsonResponse


class Centos7(object):
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def connect(self):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.host, port=self.port, username=self.user, password=self.password, timeout=5)
            return ssh
        except Exception as e:
            return e

    def get_hostname(self):
        client = self.connect()
        cmd = 'hostname'
        stdin, stdout, strerr = client.exec_command(cmd)
        hostname = stdout.read()
        return hostname

    def get_version(self):
        client = self.connect()
        stdin, stdout, stderr = client.exec_command("cat /etc/redhat-release")
        version = stdout.read()
        return version

    



