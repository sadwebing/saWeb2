#-_- coding: utf-8 -_-
from django.shortcuts               import render
from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from saWeb2                         import settings
from control.middleware.user        import User, login_required_layui, is_authenticated_to_request
from control.middleware.config      import RET_DATA, MESSAGE_TEST, CF_URL, DNSPOD_URL, MESSAGE_ONLINE, MESSAGE_TEST
from control.middleware.common      import insert_ah
from domainns.models                import CfAccountTb, DnspodAccountTb, AlterHistoryTb
from domainns.api.cloudflare        import CfApi
from domainns.api.dnspod            import DpApi
from detect.telegram                import SendTelegram
from pypinyin                       import lazy_pinyin
from control.middleware.permission.domainns  import Domainns

import re
import json
import time
import logging
import requests
import datetime

logger = logging.getLogger('django')

#telegram 参数
message = MESSAGE_ONLINE

def send_telegram_re(message):
    #message['group'] = 'arno_test'
    if len(message["text"]) > 10:
        message["text"] = '\n'.join(message["text"])
        message["doc"] = True
        message['doc_name'] = 'domain.txt'
    else:
        message["doc"] = False
        message["text"] = '\r\n'.join(message["text"]) +'\r\n'+ message['caption']
    SendTelegram(message).send()

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def reflesh_execute_cdn(request):
    '''
        刷新指定账号上域名的缓存
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '域名缓存刷新成功'
    ret_data['data'] = []

    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            ret_data['data'] = data
    except Exception as e:
        logger.error(str(e))
        ret_data['code'] = 500
        ret_data['msg']  = '域名缓存刷新失败: %s' %str(e)

    return HttpResponse(json.dumps(ret_data))

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def delete_records(request):
    '''
        删除DNSPOD 域名解析
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '删除域名解析成功'
    ret_data['data'] = []

    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            for zone in data:
                dnspod_acc = DnspodAccountTb.objects.get(name=zone['dnspod_acc'])
                dpapi  = DpApi(DNSPOD_URL, dnspod_acc.key)

                result, status = dpapi.delete_zone_record(zone['zone'], zone['record_id'], zone['name'])
                if not status:
                    logger.error(str(result))
                    ret_data['code'] = 500
                    ret_data['msg']  = "删除 %s 域名失败！%s" %(zone['name'], str(result))
                    logger.error(ret_data['msg'])
                    return HttpResponse(json.dumps(ret_data))
                else:
                    logger.info("删除 %s 域名成功！%s" %(zone['name'], str(result)))
                    insert_ah(clientip, username, 
                        "'type':%s, 'name': %s, 'content': %s, 'enabled':%s" %(zone['type'], zone['name'], zone['value'], zone['enabled']), 
                        "null", 
                        status, 'delete')
    except Exception as e:
        logger.error(str(e))
        ret_data['code'] = 500
        ret_data['msg']  = '删除域名解析失败: %s' %str(e)

    return HttpResponse(json.dumps(ret_data))

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def add_records(request):
    '''
        新增DNSPOD 域名解析
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '新增域名解析成功'
    ret_data['data'] = []

    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            zone = data['zone']
            logger.info(data)
            for sub_domain in data['sub_domain']:
                dnspod_acc  = DnspodAccountTb.objects.get(name=zone['dnspod_acc'])
                record_name = zone['zone'] if sub_domain == '@' else sub_domain+"."+zone['zone']
                try:
                    dpapi = DpApi(DNSPOD_URL, dnspod_acc.key)
                except Exception as e:
                    logger.error(str(e))
                    ret_data['code'] = 500
                    ret_data['msg']  = '%s 新增域名解析失败：%s' %(record_name, str(e))
                    return HttpResponse(json.dumps(ret_data))

                else:
                    result, status = dpapi.create_zone_record(
                        domain         = zone['zone'],
                        sub_domain     = sub_domain,
                        record_type    = data['type'],
                        value          = data['content'],
                        record_line    = data['record_line'],
                        #status         = 'enable' if data['enabled'] == '1' else 'disable',
                    )
                if not status:
                    ret_data['code'] = 500
                    ret_data['msg']  = '%s 新增域名解析失败：%s' %(record_name, str(result))
                    return HttpResponse(json.dumps(ret_data))
                insert_ah(clientip, username, 
                    "'type':%s, 'name': %s, 'content': %s, 'enabled':%s" %('null', 'null', 'null', 'null'), 
                    "'type':%s, 'name': %s, 'content': %s, 'enabled':%s" %(data['type'], record_name, data['content'], '1'), 
                    status, 'add')
    except Exception as e:
        logger.error(str(e))
        ret_data['code'] = 500
        ret_data['msg']  = '新增域名解析失败: %s' %str(e)

    return HttpResponse(json.dumps(ret_data))