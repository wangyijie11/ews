from django.contrib.auth.models import User, Group
from project.models import EwsProject, EwsProjectVersion, EwsProjectApp, EwsCompose
from django.core import serializers


# 查询用户所在用户组的所有项目
def get_project_bygroup(groupid):
    result = []
    projects = Group.objects.get(pk=groupid).ewsproject_set.all()
    for p in projects:
        dic = {}
        dic['id'] = p.id
        dic['projectname'] = p.projectname
        dic['repository'] = p.repository
        dic['created_time'] = p.created_time
        result.append(dic)
    return result


# 根据项目查询compose文件
def get_compose_byproject(projectid):
    result = []
    composes = EwsProject.objects.get(pk=projectid).ewscompose_set.all()
    projectname = EwsProject.objects.get(pk=projectid).projectname
    for c in composes:
        dic = {}
        dic['id'] = c.id
        dic['compose_file'] = str(c.compose_file)
        dic['update_time'] = c.update_time
        dic['created_time'] = c.created_time
        dic['description'] = c.description
        dic['projectname'] = projectname
        dic['version'] = EwsProjectVersion.objects.get(pk=c.tab_version_id).version
        result.append(dic)
    return result


# 根据项目的版本查询compose文件
def get_compose_byversion(versionid):
    result = []
    composes = EwsProjectVersion.objects.get(pk=versionid).ewscompose_set.all()
    version = EwsProjectVersion.objects.get(pk=c.tab_version).version
    for c in composes:
        dic = {}
        dic['id'] = c.id
        dic['compose_file'] = str(c.compose_file)
        dic['update_time'] = c.update_time
        dic['created_time'] = c.created_time
        dic['description'] = c.description
        projectname = EwsProject.objects.get(pk=c.tab_project).projectname
        dic['projectname'] = projectname
        dic['version'] = version
        result.append(dic)
    return result