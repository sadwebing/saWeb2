#-_- coding: utf-8 -_-
from django.shortcuts               import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from saWeb2                         import settings
from control.middleware.config      import RET_DATA

# 装饰器
from functools import wraps

import re
import json
import logging
import requests

logger = logging.getLogger('django')

# Create your views here.
class User(object):
    '''
        用于获取用户信息
    '''
    def __init__(self, request):
        self.__request = request

    def get_default_values(self):
        '''
            返回 用户名，用户角色，以及IP
        '''

        username = self.__request.user.username
        try:
            role = self.__request.user.userprofile.role
        except:
            role = 'none'
        if 'HTTP_X_FORWARDED_FOR' in self.__request.META:
            clientip = self.__request.META['HTTP_X_FORWARDED_FOR']
        else:
            clientip = self.__request.META['REMOTE_ADDR']
        logger.info('user: %s, %s is requesting %s.' %(username, clientip, self.__request.get_full_path()))

        return username, role, clientip

    # def Getcsrftoken(self):


    def get_post_data(self):
        '''
            获取post的json 数据
        '''
        try:
            data = json.loads(self.__request.POST)
        except Exception as e:
            logger.error(str(e))
            data = {}

        return data
        
def login_required_layui(func):
    """
        装饰器：用户请求接口前，判断是否登陆
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated: 
            return HttpResponse(json.dumps(ret_data))
        else:
            return func(request, *args, **kwargs)
    return wrapper