import paramiko
from subprocess import Popen, PIPE
import re
import os
import sys
import time


class Centos7(object):
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    # 添加公钥
    def add_pubkey(self):
        try:
            trans = paramiko.Transport((self.host, self.port))
            trans.connect(username=self.user, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(trans)
            sftp.put('/root/.ssh/id_rsa.pub', '/tmp/id_rsa.pub')
            sftp.close()

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.host, port=self.port, username=self.user, password=self.password, timeout=5)
            ssh.exec_command('cat /tmp/id_rsa.pub >> /root/.ssh/authorized_keys ; rm -f /tmp/id_rsa.pub')
            return True
        except Exception as ex:
            return False

    # 建立远程连接的两种方法
    def connect(self):
        try:
            # 创建ssh客户端
            ssh = paramiko.SSHClient()
            # 第一次ssh远程时会提示输入yes或者no
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # 密码远程连接
            ssh.connect(hostname=str(self.host), port=self.port, username=self.user, password=self.password, timeout=5)
            # 秘钥对远程连接
            # key_file = paramiko.RSAKey.from_private_key_file("/root/.ssh/id_rsa")
            # ssh.connect(hostname=self.host, port=self.port, username=self.user, pkey=key_file, timeout=5)
            return ssh
        except Exception as e:
            return False

    def get_hostname(self):
        client = self.connect()
        stdin, stdout, strerr = client.exec_command('hostname')
        hostname = stdout.read().decode().strip('\n')
        client.close()
        return hostname

    def get_version(self):
        client = self.connect()
        stdin, stdout, stderr = client.exec_command("cat /etc/redhat-release")
        version = stdout.read().decode().strip('\n')
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
        memory = 0
        client = self.connect()
        stdin, stdout, stderr = client.exec_command("cat /proc/meminfo")
        meminfo = stdout.readlines()
        for i in meminfo:
            if i.startswith('MemTotal'):
                memory = int(i.split()[1].strip())
                memory = int('%.f' % (memory / 1024.0 ** 2))
        client.close()
        return memory

    def get_disk(self):
        disk = 0
        client = self.connect()
        stdin, stdout, stderr = client.exec_command("lsblk -lb | grep disk |  awk '{sum += $4};END {print sum}'")
        disk = int(stdout.read())
        disk = int('%.f' % (disk / 1024.0 ** 3))
        client.close()
        return disk

    # 执行命令
    def ssh_cmd(self, cmd):
        client = self.connect()
        try:
            stdin, stdout, stderr = client.exec_command(cmd)
            str_out = stdout.read().decode()
            str_err = stderr.read().decode()
            if str_err != "":
                return False
            else:
                return str_out
        except Exception as ex:
            return ex

    # 传文件
    def sftp_put(self, local_path, remote_path):
        try:
            transport = paramiko.Transport((str(self.host), self.port))
            transport.connect(username=self.user, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            # 上传
            sftp.put(local_path, remote_path)
            transport.close()
            return True
        except Exception as ex:
            return False

    def sftp_get(self, local_path, remote_path):
        transport = paramiko.Transport((str(self.host), self.port))
        transport.connect(username=self.user, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        # 下载
        sftp.get(remote_path, local_path)
        transport.close()

    def get_cpustate(self):
        client = self.connect()
        stdin, stdout, stderr = client.exec_command('cat /proc/stat | grep "cpu "')
        str_out = stdout.read().decode()
        str_err = stderr.read().decode()
        if str_err != "":
            return
        cpu_time_list = re.findall('\d+', str_out)
        cpu_idle1 = cpu_time_list[3]
        total_cpu_time1 = 0
        for t in cpu_time_list:
            total_cpu_time1 = total_cpu_time1 + int(t)
        time.sleep(0.1)
        # 第二次取值
        stdin, stdout, stderr = client.exec_command('cat /proc/stat | grep "cpu "')
        str_out = stdout.read().decode()
        str_err = stderr.read().decode()
        if str_err != "":
            return
        cpu_time_list = re.findall('\d+', str_out)
        cpu_idle2 = cpu_time_list[3]
        total_cpu_time2 = 0
        for t in cpu_time_list:
            total_cpu_time2 = total_cpu_time2 + int(t)
        # 两次取值差值
        cpu_usage = str(round(1 - (float(cpu_idle2) - float(cpu_idle1)) / (total_cpu_time2 - total_cpu_time1), 2) * 100) + '%'
        client.close()
        return cpu_usage

    def get_memorystate(self):
        client = self.connect()
        stdin, stdout, stderr = client.exec_command('cat /proc/meminfo')
        str_out = stdout.read().decode()
        str_err = stderr.read().decode()
        if str_err != "":
            return
        str_total = re.search('MemTotal:.*?\n', str_out).group()
        totalmem = re.search('\d+', str_total).group()
        str_free = re.search('MemFree:.*?\n', str_out).group()
        freemem = re.search('\d+', str_free).group()
        memory_usage = str((round(1 - float(freemem) / float(totalmem), 2)) * 100) + '%'
        client.close()
        return memory_usage

    def get_diskstate(self):
        client = self.connect()
        stdin, stdout, stderr = client.exec_command("df | sed -n '2p' | awk '{print $(NF-1)}'")
        str_out = stdout.read().decode()
        str_err = stderr.read().decode()
        disk_usage = str_out.strip('\n')
        if str_err != "":
            return
        else:
            return disk_usage

    def get_state(self):
        if self.connect():
            return 'Up'
        else:
            return 'Down'


# 测试
def test(host):
    session = Centos7(host)  # 类Centos7的connect方法需要改成ssh连接
    hostname = session.get_hostname()
    cpuinfo = session.get_cpuinfo()
    memory = session.get_memory()
    version = session.get_memory()
    disk = session.get_disk()
    data = {'hostname': hostname, 'cpuinfo': cpuinfo, 'memory': memory, 'version': version, 'disk': disk}
    print(data)

