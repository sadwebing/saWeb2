#-_- coding: utf-8 -_-
from saWeb2                    import settings
from control.middleware.config import RET_DATA

# 装饰器
from functools import wraps

import re
import json
import logging

logger = logging.getLogger('django')

# Create your views here.
class IsSomeType(object):
    '''
        用于判断字符串是否是指定的数据类型
    '''
    def __init__(self, strToverify):
        self.__strToverify = strToverify

    def is_int(self):
        '''
            判断字符串是否是整数型
        '''
        try:
            if isinstance(int(self.__strToverify), int):
                return True
            else:
                return False
        except Exception as e:
            return False
        
