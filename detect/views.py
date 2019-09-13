#-_- coding: utf-8 -_-
from django.shortcuts               import render
from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
# from dwebsocket                     import require_websocket, accept_websocket
from detect.models                  import department_user_t, telegram_chat_group_t 
# from monitor.models                 import telegram_ssl_alert_t
# from accounts.limit                 import LimitAccess
from detect.telegram                import SendTelegram
from saWeb2                         import settings
from control.middleware.user         import User, login_required_layui
from control.middleware.config       import ret_data, MESSAGE_TEST
from control.middleware.common       import IsSomeType

import re
import json
import time
import logging
import requests

logger = logging.getLogger('django')

@csrf_exempt
@login_required_layui
# @login_required
def telegram_group(request):
    '''
        获取telegram 群组，以及 各部门的人员
    '''
    username, role, clientip = User(request).get_default_values()

    # 判断是否登陆
    if not request.user.is_authenticated: return HttpResponse(json.dumps(ret_data))

    # 获取需要@的群组人员
    atUsers = {}
    if request.user.is_superuser:
        atUsersSelects = department_user_t.objects.filter(status=1).all()
    elif role == "sa":
        atUsersSelects = department_user_t.objects.filter(status=1).all()
    else:
        atUsersSelects = department_user_t.objects.filter(status=1).all()

    # 获取需要发送信息的群组
    groups = {}
    if request.user.is_superuser:
        groupSelects = telegram_chat_group_t.objects.filter(status=1).all()
    elif role == "sa":
        groupSelects = telegram_chat_group_t.objects.filter(status=1, group__in=['kindergarten', 'zhuanyepan', 'yunwei']).all()
    else:
        groupSelects = telegram_chat_group_t.objects.filter(status=1, group__in=['kindergarten', 'zhuanyepan']).all()

    for department in atUsersSelects:
        atUsers[department.name] = {
            'id': department.id,
            'department': department.department,
            'users': [ 
                {
                    'name': user.name,
                    'user': user.user,
                    'user_id': user.user_id,
                }
                for user in department.user.filter(status=1).all() ],
            'atUsers': department.AtUsers(),
            'display': department.display().replace(' ', ''),
        }

    for group in groupSelects:
        groups[group.group] = {
            'id': group.id,
            'group': group.group,
            'name':  group.name,
            'group_id': group.group_id,
        }

    return HttpResponse(json.dumps({"code": 0, 
            "msg": "",
            'data': {
                'atUsers':  atUsers,
                'groups':   groups,
            },

        }))

@csrf_exempt
@login_required_layui
# @login_required
def telegram_sendgroupmessage(request):
    '''
        往对应群组发送信息
    '''
    username, role, clientip = User(request).get_default_values()

    ret_data['code'] = 0 # 请求正常，返回 0

    # time.sleep(5)

    if request.method == 'POST':
        message = MESSAGE_TEST

        data = request.POST

        # 检查群组是否为空
        # if 'group' not in data or not data['group']: 
        #     ret_data['msg'] = 'TG群组为空，请检查！'
        #     return HttpResponse(json.dumps(ret_data))
        # else:
        #     message['group'] = data['group']

        # 检查是否有图片
        if 'file' in request.FILES and request.FILES['file']:
            img = request.FILES['file']

            # 判断文件是不是 gif
            s = SendTelegram(message)
            if str(img)[-3:] == "gif":
                r = s.send_document(img)
            else:
                r = s.send_photo(img)

            if r:
                ret_data['msg']  = '图片发送成功'
            else:
                ret_data['code'] = 500
                ret_data['msg']  = '图片发送失败'
            return HttpResponse(json.dumps(ret_data))

        # 检查信息是否为空
        if 'text' not in data or not data['text']: 
            ret_data['msg'] = '信息为空，请检查！'
            return HttpResponse(json.dumps(ret_data))

        # 获取需要@的部门或组
        atUsers = []
        if 'atUsers' in data and not data['atUsers']: 
            atUsersDepList = [ int(id) for id in data['atUsers'].replace(' ', '').split(',') if IsSomeType(id).is_int() ]
            atUsersSelects = department_user_t.objects.filter(status=1, id__in=atUsersDepList).all()
            for department in atUsersSelects:
                atUsers.append(department.department + ': ' + ', '.join([ '@'+user.user for user in department.user.filter(status=1).all() ]))

        message['text']  = data['text'] + '\r\n\r\n' + '\r\n'.join(atUsers)
        s = SendTelegram(message)
        if s.send():
            ret_data['msg'] = '发送成功！'
        else: 
            ret_data['msg'] = 'telegram 接口错误，发送失败！'
        return HttpResponse(json.dumps(ret_data))

    else:
        ret_data['msg'] = '403'
        return HttpResponse(json.dumps(ret_data))


