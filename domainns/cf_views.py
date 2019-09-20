#-_- coding: utf-8 -_-
from django.shortcuts               import render
from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from saWeb2                         import settings
from control.middleware.user        import User, login_required_layui, is_authenticated_to_request
from control.middleware.config      import RET_DATA, MESSAGE_TEST, CF_URL
from control.middleware.common      import insert_ah
from domainns.models                import CfAccountTb, DnspodAccountTb, AlterHistoryTb
from domainns.api.cloudflare        import CfApi
from pypinyin                       import lazy_pinyin
from control.middleware.permission.domainns  import Domainns

import re
import json
import time
import logging
import requests
import datetime

logger = logging.getLogger('django')

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def get_zone_records(request):
    '''
        获取CF 域名信息
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '获取域名信息成功'
    ret_data['data'] = []

    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            logger.info(data)
            for zone in data['zones']:
                cf_acc = CfAccountTb.objects.get(name=zone['cf_acc'])
                cfapi  = CfApi(CF_URL, cf_acc.email, cf_acc.key)
                result = cfapi.get_zone_records(zone['zone_id'])
                if len(result['result']) == 0:
                    continue
                logger.info(result['result'])
                for record in result['result']:
                    tmp_dict = {}
                    tmp_dict['cf_acc']    = zone['cf_acc']
                    tmp_dict['zone']      = record['zone_name']
                    tmp_dict['name']      = record['name']
                    tmp_dict['type']      = record['type']
                    tmp_dict['content']   = record['content']
                    tmp_dict['proxied']   = record['proxied']
                    tmp_dict['record_id'] = record['id']
                    tmp_dict['zone_id']   = record['zone_id']
                    ret_data['data'].append(tmp_dict)

    except Exception as e:
        logger.error(str(e))
        ret_data['code'] = 500
        ret_data['msg']  = '获取域名信息失败: %s' %str(e)

    ret_data['count'] = len(ret_data['data'])

    return HttpResponse(json.dumps(ret_data))

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def update_records(request):
    '''
        更新CF 域名解析
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '修改域名信息成功'
    ret_data['data'] = []

    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            logger.info(data)
            for record in data['records']:
                cf_acc = CfAccountTb.objects.get(name=record['cf_acc'])
                cfapi  = CfApi(CF_URL, cf_acc.email, cf_acc.key)
                if data['proxied'] == 'true':
                    proxied = True
                else:
                    proxied = False

                result = cfapi.update_zone_record(record['zone_id'], data['type'], record['name'], data['content'], proxied=proxied, record_id=record['record_id'])
                logger.info("req_ip: %s | user: %s | updaterecord: { 'type':%s, 'name': %s, 'content': %s, 'proxied':%s } ---> { 'type':%s, 'name': %s, 'content': %s, 'proxied':%s }" %(clientip, username, record['type'], record['name'], record['content'], record['proxied'], data['type'], record['name'], data['content'], proxied))

                insert_h = AlterHistoryTb(
                        time    = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        req_ip  = clientip,
                        user    = username,
                        pre_rec = "'type':%s, 'name': %s, 'content': %s, 'proxied':%s" %(record['type'], record['name'], record['content'], record['proxied']),
                        now_rec = "'type':%s, 'name': %s, 'content': %s, 'proxied':%s" %(data['type'], record['name'], data['content'], proxied)
                    )

                insert_h.save()
    except Exception as e:
        logger.error(str(e))
        ret_data['code'] = 500
        ret_data['msg']  = '修改域名信息失败: %s' %str(e)

    return HttpResponse(json.dumps(ret_data))

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def delete_records(request):
    '''
        删除CF 域名解析
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
                cf_acc = CfAccountTb.objects.get(name=zone['cf_acc'])
                cfapi  = CfApi(CF_URL, cf_acc.email, cf_acc.key)

                result = cfapi.delete_zone_record(zone['zone_id'], zone['record_id'])
                if not result['success']:
                    logger.error(str(e))
                    ret_data['code'] = 500
                    ret_data['msg']  = "删除 %s 域名失败！%s" %(zone['name'], str(result))
                    logger.error(ret_data['msg'])
                    return HttpResponse(json.dumps(ret_data))
                else:
                    logger.info("删除 %s 域名成功！%s" %(zone['name'], str(result)))
                    insert_ah(clientip, username, 
                        "'type':%s, 'name': %s, 'content': %s, 'enabled':%s" %(zone['type'], zone['name'], zone['content'], zone['proxied']), 
                        "null", 
                        result['success'], 'delete')
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
        删除CF 域名解析
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
            for sub_domain in data['sub_domain']:
                cf_acc = CfAccountTb.objects.get(name=zone['cf_acc'])
                try:
                    cfapi = CfApi(CF_URL, cf_acc.email, cf_acc.key)
                except Exception as e:
                    logger.error(str(e))
                    ret_data['code'] = 500
                    ret_data['msg']  = '新增域名解析失败：%s' %str(e)
                    return HttpResponse(json.dumps(ret_data))

                else:
                    result = cfapi.create_zone_record(
                        zone_id        = zone['zone_id'],
                        record_name    = sub_domain+'.'+zone['zone'] if sub_domain != "@" else zone['zone'],
                        record_type    = data['type'],
                        record_content = data['content'],
                        proxied        = True if data['proxied'].lower() == 'true' else False,
                    )
                if not result['success']:
                    ret_data['code'] = 500
                    ret_data['msg']  = '新增域名解析失败：%s' %result['errors'][0]['message']
                    return HttpResponse(json.dumps(ret_data))
                insert_ah(clientip, username, 
                    "null", 
                    "'type':%s, 'name': %s, 'content': %s, 'enabled':%s" %(data['type'], sub_domain+'.'+zone['zone'], data['content'], '1'), 
                    result['success'], 'add')
    except Exception as e:
        logger.error(str(e))
        ret_data['code'] = 500
        ret_data['msg']  = '新增域名解析失败: %s' %str(e)

    return HttpResponse(json.dumps(ret_data))