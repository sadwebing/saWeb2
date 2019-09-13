#-_- coding: utf-8 -_-
from django.shortcuts               import render
from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from django.contrib.auth.forms      import AuthenticationForm
from saWeb2                         import settings
from control.middleware.user         import User
import json, logging, requests, re

# 获取django 自带的登入登出机制
from django.contrib.auth import (
                                REDIRECT_FIELD_NAME, get_user_model, login as auth_login,
                                logout as auth_logout, update_session_auth_hash,
                            )

logger = logging.getLogger('django')

# Create your views here.
@csrf_exempt
def Login(request, authentication_form=AuthenticationForm):
    '''
        控制登陆
    '''
    username, role, clientip = User(request).get_default_values()

    data = request.POST

    # # 判断是否登入
    # if request.user.is_authenticated:
    #     return HttpResponseRedirect('/')

    # 校验登陆
    form = authentication_form(request, data=data)
    if form.is_valid():
        auth_login(request, form.get_user())

        # 返回新的token
        logger.info('%s login' %username)
        return HttpResponse(json.dumps({
                  "code": 0,
                  "msg": "登陆成功了",
                  "data": {
                    "csrftoken": "c262e61cd13ad99fc650e6908c7e5e65b63d2f32185ecfed6b801ee3fbdd5c0a"
                  }
                })
            )
    else:
        return HttpResponse(json.dumps({
                  "code": 1001,
                  "msg": "账号密码错误",
                })
            )

@csrf_exempt
def Logout(request):
    '''
        控制登出
    '''
    username, role, clientip = User(request).get_default_values()

    data = request.POST

    # 登出
    logger.info('%s logout' %username)
    ret_data = {"code": 1001, "msg": "您已登出"}
    auth_logout(request)
    return HttpResponse(json.dumps(ret_data))

@csrf_exempt
# @login_required
def userSession(request):
    '''
        控制登陆和登出
    '''
    username, role, clientip = User(request).get_default_values()

    data = request.POST

    # 判断是否登入
    if not request.user.is_authenticated:
        ret_data = {"code": 1001, "msg": "请重新登陆"}
        return HttpResponse(json.dumps(ret_data))

    # 返回新的token
    logger.info('%s login' %username)
    return HttpResponse(json.dumps({
              "code": 0,
              "msg": "获取用户信息成功",
              "data": {
                'username': username,
                'is_superuser': request.user.is_superuser
              }
            })
        )