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
        stdin, stdout, strerr = client.exec_command('hostname')
        hostname = stdout.read()
        return hostname

    def get_version(self):
        client = self.connect()
        stdin, stdout, stderr = client.exec_command("cat /etc/redhat-release")
        version = stdout.read()
        return version

    def get_cpuinfo(self):
        processor = 0
        client = self.connect()
        stdin, stdout, stderr = client.exec_command("cat /proc/cpuinfo")
        cpuinfo = stdout.readlines()
        for i in cpuinfo:
            if i.startswith('processor'):
                processor = processor + 1
        return processor

    def get_memory(self):
        client = self.connect()
        stdin, stdout, stderr = client.exec_command("cat /proc/meminfo")
        meminfo = stdout.readlines()
        for i in meminfo:
            if i.startswith('MemTotal'):
                memory = int(i.split()[1].strip())
                memory = '%.f' % (memory / 1024.0 ** 2 )
        return memory

    def get_disk(self):
        client = self.connect()
        stdin, stdout, stderr = client.exec_command("lsblk -lb | grep disk |  awk '{sum += $4};END {print sum}'")
        disk = int(stdout.read())
        disk = '%.f' % (disk / 1024.0 ** 2 )
        return disk




