#-_- coding: utf-8 -_-
from django.shortcuts               import render
from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from saWeb2                         import settings
from control.middleware.user        import User, login_required_layui, is_authenticated_to_request
from control.middleware.config      import RET_DATA, MESSAGE_TEST, CF_URL, DNSPOD_URL
from domainns.models                import CfAccountTb, DnspodAccountTb, DoaminProjectTb
from domainns.api.cloudflare        import CfApi
from domainns.api.dnspod            import DpApi
from domainns.api.tencent           import TcApi
from domainns.api.wangsu            import WsApi
from domainns.api.aws               import AwsApi
from pypinyin                       import lazy_pinyin
from domainns.cf_views              import *
from control.middleware.permission.domainns import Domainns

import re
import json
import time
import logging
import requests
from urllib.parse import urlparse

logger = logging.getLogger('django')

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def get_cf_accounts(request):
    '''
        获取CF账号列表
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '获取CF账号列表'
    ret_data['data'] = []

    # 获取CF 账号
    cf_acc_list = Domainns(request).get_cf_account()

    for cf_acc in cf_acc_list:
        cfapi  = CfApi(CF_URL, cf_acc.email, cf_acc.key)
        page   = 1
        result = cfapi.get_dns_lists(page=page)
        
        # 请求异常处理
        if 'result_info' not in result: 
            ret_data['msg'] = "获取CF DNS失败：%s" %str(result)
            return HttpResponse(json.dumps(ret_data))

        # 格式化账号信息
        total_pages = result['result_info']['total_pages']
        tmp_dict = {
            'name':      cf_acc.name,
            'email':     cf_acc.email,
            'cf_acc_py': lazy_pinyin(cf_acc.name), # 将账号按照中文拼音进行排序
            'domain':    [],
            }
        if len(result['result']) == 0:
            continue
        while page <= total_pages: # 如果拿到的数据有多页，循环获取，直到拿到所有域名
            for record in result['result']:
                tmp_dict['domain'].append({
                        'name': record['name'],
                        'id':   record['id'],
                        'status': 'enable',
                    })
            page += 1
            result = cfapi.get_dns_lists(page=page)
        ret_data['data'].append(tmp_dict)

    #logger.info(ret_data['data'])
    ret_data['data'].sort(key=lambda acc: acc['cf_acc_py']) # cf_acc 拼音排序

    return HttpResponse(json.dumps(ret_data))

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def get_dnspod_accounts(request):
    '''
        获取DNSPOD账号列表
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '获取DNSPOD账号列表'
    ret_data['data'] = []

    # 获取DNSPOD 账号
    dnspod_acc_list = Domainns(request).get_dnspod_account()

    for dnspod_acc in dnspod_acc_list:

        # 做一步异常处理
        try:
            dpapi = DpApi(DNSPOD_URL, dnspod_acc.key)
        except Exception as e:
            ret_data['code'] = 500
            ret_data['msg']  = "查询 %s 账号失败：%s" %(dnspod_acc.name, str(e))
            logger.error(ret_data['msg'] )
            return HttpResponse(json.dumps(ret_data))
        else:
            result, status = dpapi.get_dns_lists(type='all')
            if not status:
                ret_data['code'] = 500
                ret_data['msg']  = '获取DNSPOD账号列表 失败：%s' %str(result)
                logger.error(ret_data['msg'])
                return HttpResponse(json.dumps(ret_data))
            else:
                ret_data['data'].append({
                    'name':   dnspod_acc.name,
                    'email':  dnspod_acc.email,
                    'domain': result['domains'],
                    'dnspod_acc_py': lazy_pinyin(dnspod_acc.name),
                })

    #logger.info(ret_data['data'])
    ret_data['data'].sort(key=lambda acc: acc['dnspod_acc_py']) # dnspod_acc_py 拼音排序

    return HttpResponse(json.dumps(ret_data))

@csrf_exempt
@login_required_layui
@is_authenticated_to_request
def get_reflesh_project(request):
    '''
        获取 清缓存 列表数据
    '''
    username, role, clientip = User(request).get_default_values()

    # 初始化返回数据
    ret_data = RET_DATA.copy()
    ret_data['code'] = 0 # 请求正常，返回 0
    ret_data['msg']  = '获取[清缓存列表数据]成功'
    ret_data['data'] = {'domain_project': [], 'cdn': []}

    # 获取 cdn缓存项目
    domain_project_list = DoaminProjectTb.objects.filter(status=1).all()
    for prot in domain_project_list:
        tmpdict = {}
        tmpdict['project'] = prot.project
        tmpdict['domain']  = [ {'id': domain.id,
                                'name': urlparse(domain.name).scheme+"://"+urlparse(domain.name).netloc,
                                'product': domain.get_product_display(),
                                'customer': domain.get_customer_display()} for domain in prot.domain.all() ]
        #tmpdict['cdn']     = [ {'name': cdn.get_name_display(),
        #                        'account': cdn.account} for cdn in cdn_t.objects.all() ]
        ret_data['data']['domain_project'].append(tmpdict)

    # 获取cdn 账号
    cdn_acc_list = Domainns(request).get_cdn_account()
    for cdn in cdn_acc_list:
        tmpdict = {
            'id':      cdn.id,
            'name':    cdn.get_name_display(),
            'account': cdn.account,
            'domain': [],
        }
        if cdn.get_name_display() == "wangsu":
            req = WsApi(cdn.secretid, cdn.secretkey)
            results, status = req.getdomains()
            if status:
                for line in results:
                    if line['enabled'] == 'true':
                        tmpdict['domain'].append({
                                'name': line['domain-name'],
                                'ssl' : 1 if line['service-type']=='web-https' else 0,
                            })
        # elif cdn.get_name_display() == "tencent": # 腾讯云接口有问题，后面再修复
        #     req = TcApi(cdn.secretid, cdn.secretkey)
        #     results, status = req.getdomains()
        #     for line in results['data']['hosts']:
        #         if line['disabled'] == 0 and line['status'] in [3, 4, 5]:
        #             tmpdict['domain'].append({
        #                     'name': line['host'],
        #                     'ssl' : 1 if line['ssl_type']!=0 else 0,
        #                 })
        elif cdn.get_name_display() == "aws":
            req = AwsApi(cdn.secretid, cdn.secretkey)
            results, status = req.getdomains(['fenghuang'])
            if status:
                for item in results:
                    tmpdict['domain'].append({
                            'Id': item['Id'],
                            'name': item['domains'],
                            'ssl' : 0,
                            'product':  item['product'],
                            'customer': item['customer']
                        })
        else:
            tmpdict['domain'] = []
        ret_data['data']['cdn'].append(tmpdict)
        # break

    #logger.info(ret_data['data'])
    ret_data['data']['cdn'].sort(key=lambda acc: acc['name']) # CDN账号按 name的分类 排序

    return HttpResponse(json.dumps(ret_data))