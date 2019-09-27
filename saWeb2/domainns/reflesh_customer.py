# coding: utf8
from saWeb2                import settings
from saWeb2.customer       import DefConsumer
from domainns.api.tencent  import TcApi
from domainns.api.wangsu   import WsApi
from domainns.api.aws      import AwsApi
from domainns.models       import CdnAccountTb, CfAccountTb, DomainTb

from domainns.reflesh_views    import send_telegram_re
from domainns.api.cloudflare   import CfApi
from control.middleware.user   import User
from control.middleware.config import MESSAGE_TEST, MESSAGE_ONLINE, CF_URL, DNSPOD_URL, RET_DATA


import json
import logging
import time
from urllib.parse import urlparse

logger = logging.getLogger('django')

#telegram 参数
message = MESSAGE_ONLINE

def cdn_purge(cdn_d, uri_l=['/'], ret_data=RET_DATA.copy(), con=1, socket=None):
    '''
        按CDN 账号进行缓存清理：cdn 为查询object，ret_data 当前函数返回值, con 清缓存域名为并发数
        cdn_d[cdn.get_name_display()+"_"+cdn.account] = {
                    'name': cdn.get_name_display(),
                    'domain': [],
                    'secretid': str(cdn.secretid),
                    'secretkey': str(cdn.secretkey),
                    'failed': [],
                    'success': [],
                }
        
    '''
    for cdn in cdn_d:
        if cdn_d[cdn]['domain']:
            #开始清缓存，判断CDN接口是否存在
            if cdn_d[cdn]['name'] == "wangsu": # 网宿
                req = WsApi(cdn_d[cdn]['secretid'], cdn_d[cdn]['secretkey'])
            # elif cdn_d[cdn]['name'] == "tencent": # 腾讯云的接口有点问题，后面修复
            #     req = tcApi(cdn_d[cdn]['secretid'], cdn_d[cdn]['secretkey'])
            elif cdn_d[cdn]['name'] == "aws": # AWS
                req = AwsApi(cdn_d[cdn]['secretid'], cdn_d[cdn]['secretkey'])
            else:
                # CDN 接口不存在
                ret_data['code'] = 500
                ret_data['msg']  = cdn + ": CDN 接口不存在！"
                logger.error(ret_data['msg'])
                if socket:
                    socket.send(text_data=json.dumps(ret_data))
                    socket.close()
                return cdn_d, ret_data

            # 开始清缓存
            if cdn_d[cdn]['name'] == "aws": # aws cdn 域名清理
                for Id in cdn_d[cdn]['domain']:
                    cdn_d[cdn]['domain'].remove(Id) # 对已经清理过的域名剔除列表
                    result, status = req.purge(Id, uri_l)
                    name = cdn + " - " + Id
                    if status:
                        ret_data['msg'] = name + ": 缓存清理执行中......"
                        cdn_d[cdn]['success'] += [ name ]
                    else:
                        ret_data['msg'] = name + ": 缓存清理失败！" 
                        cdn_d[cdn]['failed'] += [ name ]
                    if socket:
                        ret_data['step_finished'] += 1
                        socket.send(text_data=json.dumps(ret_data))
                    
            else:
                while len(cdn_d[cdn]['domain']) != 0 :
                    domains_c            = cdn_d[cdn]['domain'][:con] 
                    cdn_d[cdn]['domain'] = cdn_d[cdn]['domain'][con:] # 对已经清理过的域名剔除列表
                    for uri in uri_l:
                        result, status = req.purge(domains_c, uri)
                        if status:
                            ret_data['msg'] = "<br/>".join([ domain+uri+": 清缓存成功。" for domain in domains_c ])
                            cdn_d[cdn]['success'] += [ domain+uri for domain in domains_c ]
                        else:
                            ret_data['msg'] = "<br/>".join([ domain+uri+": 清缓存失败！" for domain in domains_c ])
                            cdn_d[cdn]['failed'] += [ domain+uri for domain in domains_c ]
                        if socket:
                            ret_data['step_finished'] += len(domains_c)
                            # logger.info(ret_data['step_finished'])
                            socket.send(text_data=json.dumps(ret_data))
    return cdn_d, ret_data               

def cf_purge(cf_d, uri_l=['/'], ret_data=RET_DATA.copy(), con=1, socket=None):
    '''
        按cf 账号进行缓存清理：cf 为查询object，ret_data 当前函数返回值, con 清缓存域名为并发数
        cf_d[cf.name] = {
                    'name': cf.name,
                    'domain': [],
                    'email': str(cf.email),
                    'key': str(cf.key),
                    'failed': [],
                    'success': [],
                }
        
    '''
    for cf in cf_d:
        if cf_d[cf]['domain']:
            #开始清CF缓存
            req = CfApi(CF_URL, cf_d[cf]['email'], cf_d[cf]['key'])

            for domain in cf_d[cf]['domain']:
                cf_d[cf]['domain'].remove(domain) # 对已经清理过的域名剔除列表
                zone = ".".join(domain.split(".")[-2:])
                zone_id = req.get_zone_id(zone)['zone_id']
                if not zone_id:
                    ret_data['msg'] = "CloudFlare_"+cf+": "+domain+": 清缓存失败！"
                    cf_d[cf]['failed'] += [domain]

                result = req.purge(zone_id)
                if result['success']:
                    ret_data['msg'] = "CloudFlare_"+cf+": "+domain+": 清缓存成功。"
                    cf_d[cf]['success'] += [domain]
                else:
                    ret_data['msg'] = "CloudFlare_"+cf+": "+domain+": 清缓存失败！"
                    cf_d[cf]['failed'] += [domain]
                if socket:
                    ret_data['step_finished'] += 1
                    socket.send(text_data=json.dumps(ret_data))

    return cf_d, ret_data   

class DomainnsRefleshExecuteCdn(DefConsumer):
    # Set to True to automatically port users from HTTP cookies
    # (you don't need channel_session_user, this implies it)

    def receive(self, text_data):
        """
        Called when a message is received with either text or bytes
        filled out.
        """

        if not self.scope['user'].is_authenticated: # 登陆失效，无法继续操作
            self.close()
            return False

        try:
            data = json.loads(text_data)
            # logger.info(data)

            # 将cdn 账号上清缓存的数据，放入字典，方便后面存取
            cdn_d = {}
            cdn   = CdnAccountTb.objects.get(id=data['cdn'])

            logger.info(cdn.get_name_display())
            if cdn.get_name_display() == 'wangsu': # 计入总清缓存次数，网宿清理缓存按uri 单个进行清理
                self._ret_data['step_all'] += len(data['domain']) * len(data['uri'])
            else:
                self._ret_data['step_all'] += len(data['domain'])

            cdn_d[cdn.get_name_display()+"_"+cdn.account] = {
                'name': cdn.get_name_display(),
                'domain': data['domain'],
                'secretid': str(cdn.secretid),
                'secretkey': str(cdn.secretkey),
                'failed': [],
                'success': [],
            }

            while self._ret_data['step_finished'] < self._ret_data['step_all']:
                # self._ret_data['msg'] = domain = data['domain'][self._ret_data['step_finished']]
                # self._ret_data['step_finished'] += 1
                # self.send(text_data=json.dumps(self._ret_data))
                # time.sleep(1)
                # continue

                # 执行清理缓存的操作
                cdn_d, self._ret_data = cdn_purge(cdn_d, data['uri'], self._ret_data, con=10, socket=self)


            # 发telegram 信息前，先关闭socket，防止堵塞
            self.close()

            # 发送 tg 消息
            for cdn in cdn_d:
                # message['group'] = "arno_test2"
                if cdn_d[cdn]['failed']:
                    message["text"] = cdn_d[cdn]['failed']
                    message['caption'] = cdn + ': 域名缓存清理失败!'
                    send_telegram_re(message)
                if cdn_d[cdn]['success']:
                    message["text"] = cdn_d[cdn]['success']
                    message['caption'] = cdn + ': 域名缓存清理成功。'
                    send_telegram_re(message)
            self.close()



        except Exception as e:
            self._ret_data['code'] = 500
            self._ret_data['msg']  = "域名清理失败：" + str(e) 
            logger.error(self._ret_data['msg'])
            self.send(text_data=json.dumps(self._ret_data))
            self.close()


class DomainnsRefleshExecuteProject(DefConsumer):
    # Set to True to automatically port users from HTTP cookies
    # (you don't need channel_session_user, this implies it)

    def receive(self, text_data):
        """
        Called when a message is received with either text or bytes
        filled out.
        """
        if not self.scope['user'].is_authenticated: # 登陆失效，无法继续操作
            self.close()
            return False

        try:
            data = json.loads(text_data)

            # 收集cdn 和 CF 账号
            cdn_d = {}
            cdns  = CdnAccountTb.objects.filter(status=1).all()
            for cdn in cdns:
                cdn_d[cdn.get_name_display()+"_"+cdn.account] = {
                    'name': cdn.get_name_display(),
                    'domain': [],
                    'secretid': str(cdn.secretid),
                    'secretkey': str(cdn.secretkey),
                    'failed': [],
                    'success': [],
                }
            cf_d = {}
            cfs  = CfAccountTb.objects.filter(status=1).all()
            for cf in cfs:
                cf_d[cf.name] = {
                    'name': cf.name,
                    'domain': [],
                    'email': str(cf.email),
                    'key': str(cf.key),
                    'failed': [],
                    'success': [],
                }

            # 获取域名信息
            domain_l = DomainTb.objects.filter(id__in=[ int(id) for id in data['domain'] ]).all()

            # 将每个域名在对应cdn 或者 CF 上信息存入字典
            for domain in domain_l:
                for cdn in domain.cdn.all():
                    if cdn.get_name_display() == 'wangsu': # 计入总清缓存次数，网宿清理缓存按uri 单个进行清理
                        self._ret_data['step_all'] += len(data['uri'])
                    else:
                        self._ret_data['step_all'] += 1
                    cdn_d[cdn.get_name_display()+"_"+cdn.account]['domain'].append(urlparse(domain.name).scheme+"://"+urlparse(domain.name).netloc)
                if domain.cf:
                    self._ret_data['step_all'] += 1
                    cf_d[domain.cf.name]['domain'].append(urlparse(domain.name).scheme+"://"+urlparse(domain.name).netloc)

            # 按照上面收集的cdn 和 CF 账号，以及域名，进行缓存清理
            while self._ret_data['step_finished'] < self._ret_data['step_all']:
                cdn_d, self._ret_data = cdn_purge(cdn_d, data['uri'], self._ret_data, con=10, socket=self)
                cf_d, self._ret_data = cf_purge(cf_d, data['uri'], self._ret_data, con=10, socket=self)


            # 发telegram 信息前，先关闭socket，防止堵塞
            self.close()

            # 发送 tg 消息
            for cdn in cdn_d:
                # message['group'] = "arno_test2"
                if cdn_d[cdn]['failed']:
                    message["text"] = cdn_d[cdn]['failed']
                    message['caption'] = cdn + ': 域名缓存清理失败!'
                    send_telegram_re(message)
                if cdn_d[cdn]['success']:
                    message["text"] = cdn_d[cdn]['success']
                    message['caption'] = cdn + ': 域名缓存清理成功。'
                    send_telegram_re(message)
            for cf in cf_d:
                message['group'] = "arno_test2"
                if cf_d[cf]['failed']:
                    message["text"] = cf_d[cf]['failed']
                    message['caption'] = "CloudFlare_"+cf + ': 域名缓存清理失败!'
                    send_telegram_re(message)
                if cf_d[cf]['success']:
                    message["text"] = cf_d[cf]['success']
                    message['caption'] = "CloudFlare_"+cf + ': 域名缓存清理成功。'
                    send_telegram_re(message)
            

        except Exception as e:
            self._ret_data['code'] = 500
            self._ret_data['msg']  = "域名清理失败：" + str(e) 
            logger.error(self._ret_data['msg'])
            self.send(text_data=json.dumps(self._ret_data))
            self.close()
