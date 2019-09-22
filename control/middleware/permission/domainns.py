#-_- coding: utf-8 -_-
from saWeb2                         import settings
from control.middleware.config      import RET_DATA
from control.models                 import UserPermissionsTb
from domainns.models                import CfAccountTb, DnspodAccountTb

# 装饰器
from functools import wraps

import re
import json
import logging
import requests

logger = logging.getLogger('django')

class Domainns(object):
    '''
        用于控制domainns 模块中 models 的权限
        不同的用户，限制增删查改
    '''
    def __init__(self, request):
        self.__request = request

    def get_cf_account(self):
        '''
            返回 CF 账号信息
        '''
        cf_acc_list = []

        try:
            if self.__request.user.is_superuser:
                cf_acc_list = [ acc for acc in CfAccountTb.objects.all() ]
            else:
                user_p = UserPermissionsTb.objects.get(user=self.__request.user)
                cf_acc_list = [ acc for acc in user_p.cf_account_p.all() ]
                for user_group_p in user_p.usergroup_p.all():
                    for cf_acc in user_group_p.cf_account_p.all():
                        if cf_acc not in cf_acc_list: cf_acc_list.append(cf_acc)

        except Exception as e:
            logger.error(str(e))

        return cf_acc_list

    def get_dnspod_account(self):
        '''
            返回 DNSPOD 账号信息
        '''
        dnspod_acc_list = []

        try:
            if self.__request.user.is_superuser:
                dnspod_acc_list = [ acc for acc in DnspodAccountTb.objects.all() ]
            else:
                user_p = UserPermissionsTb.objects.get(user=self.__request.user)
                dnspod_acc_list = [ acc for acc in user_p.dnspod_account_p.all() ]
                for user_group_p in user_p.usergroup_p.all():
                    for dnspod_acc in user_group_p.dnspod_account_p.all():
                        if dnspod_acc not in dnspod_acc_list: dnspod_acc_list.append(dnspod_acc)

        except Exception as e:
            logger.error(str(e))

        return dnspod_acc_list

