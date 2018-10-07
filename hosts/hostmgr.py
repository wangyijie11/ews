import paramiko
from subprocess import Popen, PIPE
import re
import os, sys
from django.http import JsonResponse

class AddLinux:
    def session(self, host, port, user, password):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=host, port=port, username=user, password=password, timeout=5)
            return ssh
        except Exception as e:
            return e.message

class GetLinuxMessage:
    def session(self, host, port, user, password):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=host, port=port, username=user, password=password, timeout=5)
            return ssh
        except Exception as e:
            return e.message

    def get_hostname(self, host, port, user, password):
        client = self.session(host=host, port=port, user=user, password=password)
        cmd = 'hostname'
        stdin, stdout, strerr = client.exec_command(cmd)
        hostname = stdout.read()
        return hostname

    def get_version(self):
        pass




