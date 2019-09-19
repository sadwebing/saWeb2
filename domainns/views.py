#-_- coding: utf-8 -_-
from django.shortcuts               import render
from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from saWeb2                         import settings
from control.middleware.user        import User, login_required_layui, is_authenticated_to_request
from control.middleware.config      import RET_DATA, MESSAGE_TEST, CF_URL
from domainns.models                import CfAccountTb, DnspodAccountTb
from domainns.api.cloudflare        import CfApi
from pypinyin                       import lazy_pinyin
from domainns.cf_views              import *
from control.middleware.permission.domainns  import Domainns

import re
import json
import time
import logging
import requests

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


