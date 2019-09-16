#-_- coding: utf-8 -_-
from django.shortcuts               import render
from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from saWeb2                         import settings

import re
import json
import logging
import requests

logger = logging.getLogger('django')

# models 中启用与禁用参数
choices_s = ((1, '启用'), (0, '禁用'),)

# 初始化返回给前端的数据
RET_DATA = {'code': 1001, 'msg': '请重新登陆'}

# telegram api
TELEGRAM_API = {
    'api':{
        'AuraAlertBot'  : '471691674:AAFx1MQ3VwXdWUYyh4CaErzwoUNswG9XDsU',
        'sa_monitor_bot': '422793714:AAE8A-sLU1Usms2bJxiKWc3tUWaWYP98bSU',
    },

    'url':{
        'AuraAlertBot'  : 'https://api.telegram.org/bot471691674:AAFx1MQ3VwXdWUYyh4CaErzwoUNswG9XDsU/',
        'sa_monitor_bot': 'https://api.telegram.org/bot422793714:AAE8A-sLU1Usms2bJxiKWc3tUWaWYP98bSU/',
    },
}

# telegram 参数
MESSAGE_TEST = {
    'doc': False,
    'bot': "sa_monitor_bot", #AuraAlertBot: 大魔王
    'text': "",
    'group': "arno_test",
    'parse_mode': "HTML",
    'doc_file': "message.txt",
}

MESSAGE_ONLINE = {
    'doc': False,
    'bot': "sa_monitor_bot", #AuraAlertBot: 大魔王
    'text': "",
    'group': "kindergarten",
    'parse_mode': "HTML",
    'doc_file': "message.txt",
}

#cloudflare api
CF_URL = 'https://api.cloudflare.com/client/v4/zones'

#dnspod api
DNSPOD_URL = 'https://dnsapi.cn/'