#-_- coding: utf-8 -_-
from django.shortcuts               import render
from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from saWeb2                         import settings
from control.middleware.user        import User, login_required_layui, is_authenticated_to_request
from control.middleware.config      import RET_DATA, MESSAGE_TEST, CF_URL, DNSPOD_URL, MESSAGE_ONLINE, MESSAGE_TEST
from control.middleware.common      import insert_ah
from domainns.models                import CfAccountTb, DnspodAccountTb, AlterHistoryTb, DomainTb, CdnAccountTb, DomainDetectGroupTb
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
def get_domain_records(request):
    '''
        域名列表获取
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '域名列表获取成功'
    ret_data['data'] = []

    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            domains = DomainTb.objects.filter(name__icontains=data['name'], status__in=data['status'], group__id__in=data['group'], product__in=data['product'], customer__in=data['customer'])
            logger.info(data)
            if len(data['cdn']) != 0:
                domains = domains.filter(cdn__in=data['cdn'])
            if len(data['cf']) != 0:
                domains = domains.filter(cf__in=data['cf'])

            domains = domains.all().order_by('-id')

            for domain in domains:
                tmp_dict = {}
                tmp_dict['id']       = domain.id
                tmp_dict['name']     = domain.name
                tmp_dict['product']  = (domain.product, domain.get_product_display())
                tmp_dict['customer'] = (domain.customer, domain.get_customer_display())
                tmp_dict['content']  = domain.content
                tmp_dict['status']   = domain.status

                tmp_dict['group']    = {
                    'id': domain.group.id,
                    'group': domain.group.group,
                }
                
                tmp_dict['cdn']      = [{
                        'id':      cdn.id,
                        'name':    cdn.get_name_display(),
                        'account': cdn.account,
                    } for cdn in domain.cdn.all()]
                if domain.cf:
                    tmp_dict['cf'] = [{
                            'id':      domain.cf.id,
                            'name':    "cloudflare",
                            'account': domain.cf.name,
                        }]
                else:
                    tmp_dict['cf'] = []

                ret_data['data'].append(tmp_dict)

    except Exception as e:
        logger.error(str(e))
        ret_data['code'] = 500
        ret_data['msg']  = '域名列表获取失败: %s' %str(e)

    return HttpResponse(json.dumps(ret_data))

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def add_domain_records(request):
    '''
        域名新增
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '域名新增成功'
    ret_data['data'] = []

    try:
        if request.method == 'POST':
            data = json.loads(request.body)

            logger.info(data)
            # return HttpResponse(json.dumps(ret_data))

            for domain_name in data['name']:
                domain = DomainTb(
                        name=domain_name, 
                        product=data['product'], 
                        customer=data['customer'], 
                        group=DomainDetectGroupTb.objects.get(id=data['group']), 
                        content=data['content'], 
                        status=data['status']
                    )

                domain.save()
                for cdn in data['cdn']:
                    domain.cdn.add(CdnAccountTb.objects.get(id=cdn))
                    domain.save()
                if data['cf']:
                    domain.cf = CfAccountTb.objects.get(id=data['cf'])
                    domain.save()

    except Exception as e:
        logger.error(str(e))
        ret_data['code'] = 500
        ret_data['msg']  = '域名新增失败: %s' %str(e)

    return HttpResponse(json.dumps(ret_data))

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def edit_domain_records(request):
    '''
        域名修改
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '域名修改成功'
    ret_data['data'] = []

    try:
        if request.method == 'POST':
            data = json.loads(request.body)

            logger.info(data)
            # return HttpResponse(json.dumps(ret_data))

            index = 0
            for record in data['records']:
                domain = DomainTb.objects.get(id=record['id']) # 获取域名

                if len(data['records']) == 1 or data['content']:
                    domain.content = data['content']

                domain.name = data['name'][index]
                domain.product  = data['product']
                domain.customer = data['customer']
                domain.status   = data['status']
                domain.group    = DomainDetectGroupTb.objects.get(id=data['group'])

                domain.save()
                if data['cdn_status']:
                    for cdn in domain.cdn.all():
                        domain.cdn.remove(cdn)
                    for cdn in data['cdn']:
                        domain.cdn.add(CdnAccountTb.objects.get(id=cdn))
                        domain.save()
                if data['cf_status']:
                    if data['cf']:
                        domain.cf = CfAccountTb.objects.get(id=data['cf'])
                        domain.save()

                index += 1

    except Exception as e:
        logger.error(str(e))
        ret_data['code'] = 500
        ret_data['msg']  = '域名修改失败: %s' %str(e)

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