#!/usr/bin/env python
#-_- coding: utf-8 -_-
#author: arno
#introduction:
#    dnspod api

from detect.telegram import SendTelegram
from saWeb2          import settings
from control.middleware.config import MESSAGE_TEST, MESSAGE_ONLINE

import requests
import json
import logging

logger = logging.getLogger('django')

# 禁用安全请求警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#telegram 参数
message = MESSAGE_TEST

class DpApi(object):
    def __init__(self, url, key, format='json'):
        '''
            初始化接口参数，默认获取的数据格式为json
        '''
        self.__url  = url.rstrip('/')
        self.__key  = key
        self.__data = {
            'login_token': self.__key, #登陆token
            'format': format           #获取的数据格式
        }
        #self.__headers = {'X-Auth-Email': self.__email, 'X-Auth-Key': self.__key, 'Content-Type': 'application/json'}

        
    def _exe_post(self, uri, info):
        url = self.__url + uri
        self.__warning = "\r\n".join([ 
                '@arno',
                'Attention: %s 失败，请检查:' %info,
                'URL:  + %s' %url,
                #'%s : %s' %(secretid, secretkey)
              ])
        #logger.info(self.__data)
        try:
            ret = requests.post(url, data=self.__data, verify=False, timeout=15)
        except Exception as e:
            message['text'] = self.__warning + '\nException: ' + str(e.message)
            logger.error(message['text'])
            SendTelegram(message).send()
            return str(e.message), False
        else:
            result = ret.json()
            if result['status']['code'] != "1":
                message['text'] = self.__warning + '\n' + str(result['status'])
                logger.error(message['text'])
                SendTelegram(message).send()
                return result, False
            else:
                logger.info("%s 成功！" %info)
                return result, True

    def get_dns_lists(self, type='all'):
        '''
            获取域名列表
        '''
        self.__data['type'] = type
        return self._exe_post('/Domain.List', "Dnspod域名列表获取")

    def get_zone_records(self, domain):
        '''
            获取域名解析记录
        '''
        self.__data['domain'] = domain
        self.__data['offset'] = 0
        self.__data['length'] = 3000
        return self._exe_post('/Record.List', "Dnspod域名[%s]解析获取" %domain)
        
    def create_zone_record(self, domain, sub_domain='@', record_type='A', record_line='默认', value='8.8.8.8', status='enable'):
        '''
            新增域名解析记录：
                domain_id 或 domain, 分别对应域名ID和域名, 提交其中一个即可；
                sub_domain 主机记录, 如 www，可选，如果不传，默认为 @；
                record_type 记录类型，通过API记录类型获得，大写英文，比如：A, 必选；
                record_line 记录线路，通过API记录线路获得，中文，比如：默认，国内，国外；
                value 记录值, 如 IP:200.200.200.200, CNAME: cname.dnspod.com., MX: mail.dnspod.com., 必选；
                status [“enable”, “disable”]，记录初始状态，默认为“enable”，如果传入“disable”，解析不会生效，也不会验证负载均衡的限制，可选。
        '''
        self.__data.update({
                'domain': domain,
                'value' : value,
                'status': status,

                'sub_domain' : sub_domain,
                'record_type': record_type,
                'record_line': record_line,
            })
        full_domain = domain if sub_domain == '@' else sub_domain +'.'+ domain
        return self._exe_post('/Record.Create', "Dnspod域名记录[%s]新增" %full_domain)

    def delete_zone_record(self, domain, record_id, full_domain=''):
        '''
            删除域名解析记录
        '''
        self.__data['domain']    = domain
        self.__data['record_id'] = record_id
        return self._exe_post('/Record.Remove', "Dnspod域名[%s]删除" %full_domain)
        
    def update_zone_record(self, domain, record_id, sub_domain, value, record_type, record_line_id, status):
        '''
            修改域名解析记录
        '''
        self.__data['domain']         = domain
        self.__data['record_id']      = record_id
        self.__data['sub_domain']     = sub_domain
        self.__data['value']          = value
        self.__data['record_type']    = record_type
        self.__data['record_line_id'] = record_line_id
        self.__data['status']         = status
        return self._exe_post('/Record.Modify', "Dnspod域名[%s]解析修改" %(sub_domain+'.'+domain))
        
if __name__ == '__main__':
    print ('no')