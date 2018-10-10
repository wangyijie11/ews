import paramiko
from subprocess import Popen, PIPE
import re
import os
import sys


class Centos7(object):
    def __init__(self, host, port=22, user='root'):
        self.host = host
        self.port = port
        self.user = user

    def connect(self):
        try:
            # 创建ssh客户端
            ssh = paramiko.SSHClient()
            # 第一次ssh远程时会提示输入yes或者no
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # 密码远程连接
            # ssh.connect(hostname=self.host, port=self.port, username=self.user, password=self.password, timeout=5)
            # 秘钥对远程连接
            key_file = paramiko.RSAKey.from_private_key_file("/root/.ssh/id_rsa")
            ssh.connect(hostname=self.host, port=self.port, username=self.user, pkey=key_file, timeout=5)
            return ssh
        except Exception as e:
            return e

    def get_hostname(self):
        client = self.connect()
        stdin, stdout, strerr = client.exec_command('hostname')
        hostname = stdout.read()
        client.close()
        return hostname

    def get_version(self):
        client = self.connect()
        stdin, stdout, stderr = client.exec_command("cat /etc/redhat-release")
        version = stdout.read()
        client.close()
        return version

    def get_cpuinfo(self):
        processor = 0
        client = self.connect()
        stdin, stdout, stderr = client.exec_command("cat /proc/cpuinfo")
        cpuinfo = stdout.readlines()
        for i in cpuinfo:
            if i.startswith('processor'):
                processor = processor + 1
        client.close()
        return processor

    def get_memory(self):
        client = self.connect()
        stdin, stdout, stderr = client.exec_command("cat /proc/meminfo")
        meminfo = stdout.readlines()
        for i in meminfo:
            if i.startswith('MemTotal'):
                memory = int(i.split()[1].strip())
                memory = '%.f' % (memory / 1024.0 ** 2 )
        client.close()
        return memory

    def get_disk(self):
        client = self.connect()
        stdin, stdout, stderr = client.exec_command("lsblk -lb | grep disk |  awk '{sum += $4};END {print sum}'")
        disk = int(stdout.read())
        disk = '%.f' % (disk / 1024.0 ** 2 )
        client.close()
        return disk


def test(host):
    session = Centos7(host)  # 类Centos7的connect方法需要改成ssh连接
    hostname = session.get_hostname()
    cpuinfo = session.get_cpuinfo()
    memory = session.get_memory()
    version = session.get_memory()
    disk = session.get_disk()
    data = {'hostname': hostname, 'cpuinfo': cpuinfo, 'memory': memory, 'version': version, 'disk': disk}
    print(data)
