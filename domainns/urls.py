#-_- coding: utf-8 -_-
from django.conf.urls import url, include
from django.views.generic.base import RedirectView
from . import views
from domainns import dnspod_views
from domainns import reflesh_views
from domainns import domain_views

urlpatterns = [
    # CloudFlare
    url('cloudflare/get_accounts$', views.get_cf_accounts, name='GetCfAccounts'), # 获取CF账号列表
    url('cloudflare/get_zone_records$', views.get_zone_records, name='GetZoneRecords'),
    url('cloudflare/update_records$', views.update_records, name='UpdateRecords'),
    url('cloudflare/delete_records$', views.delete_records, name='DeleteRecords'),
    url('cloudflare/add_records$', views.add_records, name='AddRecords'),

    # DnsPod
    url('dnspod/get_accounts$', views.get_dnspod_accounts, name='GetDnsPodAccounts'), # 获取CF账号列表
    url('dnspod/get_zone_records$', dnspod_views.get_zone_records, name='GetZoneRecords'),
    url('dnspod/update_records$', dnspod_views.update_records, name='UpdateRecords'),
    url('dnspod/delete_records$', dnspod_views.delete_records, name='DeleteRecords'),
    url('dnspod/add_records$', dnspod_views.add_records, name='AddRecords'),

    # 缓存清理
    url('^reflesh$', views.get_reflesh_project),
    # url('^reflesh/get_domains$', views.refleshGetDomains),
    # url('^reflesh/get_cdnmiddlesourcelist$', views.GetCdnMiddleSourceList),
    # url('^reflesh/get_project$', views.refleshGetProject),
    # url('^reflesh/execute$', views.refleshExecute),
    # url('^reflesh/purge$', views.refleshPurge),
    # url('^reflesh/purgecfdomain$', views.purgeCfDomain),

    # 域名列表
    url('^domain/args$', views.get_domain_args),
    url('^domain/get_records$', domain_views.get_domain_records),
    url('^domain/add_records$', domain_views.add_domain_records),
    url('^domain/edit_records$', domain_views.edit_domain_records),
    url('^domain/delete_records$', domain_views.delete_domain_records),

    # url('get_domains$', views.GetDomains, name='GetDomains'),
    # url('send_telegram$', views.SendTelegram, name='SendTelegram'),
    # url('get_at_users$', views.get_at_users, name='getAtUsers'),
    # #url('get_telegram_user_id$', views.GetTelegramUserId, name='GetTelegramUserId'),

    # # 发送telegram信息
    # url('telegram$', views.telegram_group, name='TelegramGroup'),
    # url('telegram/sendgroupmessage$', views.telegram_sendgroupmessage, name='Telegramsendgroupmessage'),
    # url('telegram/uploadimgs$', views.TelegramUploadimgs, name='TelegramUploadimgs'),
]
