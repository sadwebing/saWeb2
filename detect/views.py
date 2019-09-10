#-_- coding: utf-8 -_-
from django.shortcuts               import render
from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
# from dwebsocket                     import require_websocket, accept_websocket
# from models                         import domains, department_user_t, telegram_chat_group_t 
# from monitor.models                 import telegram_ssl_alert_t
# from accounts.limit                 import LimitAccess
from detect.telegram                import sendTelegram
from saWeb2                         import settings
from control.userMiddlecont         import userMc

import json, logging, requests, re

logger = logging.getLogger('django')

@csrf_exempt
@login_required
def TelegramGroup(request):
    title = u'Telegram-群组信息'

    username, role, clientip = userMc(request).GetDefaultValues()

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


    return render(
        request,
        'detect/telegram_group.html',
        {
            'title':    title,
            'clientip': clientip,
            'role':     role,
            'username': username,
            'atUsers':  json.dumps(atUsers),
            'groups':   json.dumps(groups),
        }
    )