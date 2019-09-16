#!/usr/bin/env python
#-_- coding: utf-8 -_-
#author: arno
#introduction:
#    cfapi

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from saWeb2          import settings
from detect.telegram import SendTelegram
from control.middleware.config import MESSAGE_TEST, MESSAGE_ONLINE

import requests
import json
import logging


# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logger = logging.getLogger('django')

#telegram 参数
message = MESSAGE_TEST.copy()

class CfApi(object):
    def __init__(self, url, email, key):
        self.__url = url.rstrip('/')
        self.__email = email
        self.__key = key
        self.__headers = {'X-Auth-Email': self.__email, 'X-Auth-Key': self.__key, 'Content-Type': 'application/json'}

    def get_dns_lists(self, page=1, status='active', match='all', order='name', direction='asc'):
        url = self.__url + '?per_page=50&page=%s&status=%s&match=%s&order=%s&direction=%s' %(page, status, match, order, direction)
        try:
            ret = requests.get(url, headers=self.__headers, verify=False)
            return ret.json()
        except Exception as e:
            logger.error("获取CF dns列表失败: %s" %str(e))
            return {u'result': [str(e)], u'success': False}

    def get_zone_id(self, zone):
        url = self.__url + '?name=%s' %(zone)
        try:
            ret = requests.get(url, headers=self.__headers, verify=False)
            zone_id = ret.json()['result'][0]['id']
            #logger.info(ret.json())
            return {u'zone_id': zone_id}
        except:
            return {u'zone_id': None}

    def get_dns_record(self, zone, record_name):
        self.__zone_id   = self.get_zone_id(zone)['zone_id']
        self.__record_id = self.get_dns_record_id(self.__zone_id, record_name)
        url = self.__url + '/%s/' %self.__zone_id + 'dns_records/%s' %self.__record_id
        #logger.info(url)
        try:
            ret = requests.get(url, headers=self.__headers, verify=False)
            return ret.json()
        except:
            return False

    def get_zone_records(self, zone_id):
        url = self.__url + '/%s/' %zone_id + 'dns_records?per_page=100'
        try:
            ret = requests.get(url, headers=self.__headers, verify=False)
            return ret.json()
        except:
            return {'result': []}

    def get_dns_record_id(self, zone_id, record_name):
        self.__record_id = ''
        url = self.__url + '/%s/' %zone_id + 'dns_records?per_page=100&name=%s' %record_name
        try:
            ret = requests.get(url, headers=self.__headers, verify=False)
            #logger.info(ret.json())
            if len(ret.json()['result']) == 0:
                pass
            elif len(ret.json()['result']) == 1:
                self.__record_id = ret.json()['result'][0]['id']
            else:
                self.__record_id = 'id more than one'
        except:
            self.__record_id = 'bad arguments'

        return self.__record_id

    def create_zone_record(self, zone_id, record_type, record_name, record_content, proxied=False):
        '''
            新增解析记录，{'type':'A', 'name':'example.com', 'content': '127.0.0.1', 'proxied':false}
        '''
        datas  = {'type':record_type, 'name': record_name, 'content': record_content, 'proxied':proxied}
        result = {}

        url = self.__url + '/%s/' %zone_id + 'dns_records'

        self.__warning = "\r\n".join([ 
                '@arno',
                'Attention: CF域名解析新增失败，请检查:',
                'URL:  + %s' %url,
                #'%s : %s' %(secretid, secretkey)
              ])

        try:
            ret = requests.post(url, data=json.dumps(datas), headers=self.__headers, verify=False)
            result = ret.json()

        except Exception as e:
            result = {'result': None, 'errors': str(e), 'success': False}

        if not result['success']:
            message['text'] = self.__warning + '\n' + str(result)
            logger.error(message['text'].replace('\r\n', '\n'))
            SendTelegram(message).send()

        return result

    def update_zone_record(self, zone_id, record_type, record_name, record_content, proxied=False, record_id=''):
        datas = {'type':record_type, 'name': record_name, 'content': record_content, 'proxied':proxied}
        if record_id == '':
            record_id = self.get_dns_record_id(zone_id, record_name)
        logger.info('record_id: %s' %record_id)

        if record_id == '':
            return {'result': 'id null'}
        elif record_id == 'id more than one':
            return {'result': 'id more than one'}
        elif record_id == 'bad arguments':
            return {'result': 'bad arguments'}
        else:
            url = self.__url + '/%s/' %zone_id + 'dns_records/'+ record_id
            try:
                ret = requests.put(url, data=json.dumps(datas), headers=self.__headers, verify=False)
                return ret.json()

            except:
                return {'result': {}, 'success': False}

    def delete_zone_record(self, zone_id, record_id):
        '''
            删除解析记录
        '''
        result = {}

        url = self.__url + '/%s/' %zone_id + 'dns_records/' + record_id

        self.__warning = "\r\n".join([ 
                '@arno',
                'Attention: CF域名解析删除失败，请检查:',
                'URL:  + %s' %url,
                #'%s : %s' %(secretid, secretkey)
              ])

        try:
            ret = requests.delete(url, headers=self.__headers, verify=False)
            result = ret.json()

        except Exception as e:
            result = {'result': None, 'errors': str(e), 'success': False}

        if not result['success']:
            message['text'] = self.__warning + '\n' + str(result)
            logger.error(message['text'].replace('\r\n', '\n'))
            SendTelegram(message).send()

        return result

    def purge(self, zone_id):
        '''
            清理缓存："purge_everything":true
        '''
        result = {}
        data = {"purge_everything": True}
        url  = self.__url + '/%s/' %zone_id + 'purge_cache'

        self.__warning = "\r\n".join([ 
                '@arno',
                'Attention: CF域名缓存清理失败，请检查:',
                'URL:  + %s' %url,
                #'%s : %s' %(secretid, secretkey)
              ])

        try:
            ret = requests.post(url, data=json.dumps(data), headers=self.__headers, verify=False)
            result = ret.json()

        except Exception as e:
            result = {'result': None, 'errors': str(e), 'success': False}

        if not result['success']:
            message['text'] = self.__warning + '\n' + str(result)
            logger.error(message['text'].replace('\r\n', '\n'))
            SendTelegram(message).send()

        return result


if __name__ == '__main__':
    print ('no')