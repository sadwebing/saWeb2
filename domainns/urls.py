#-_- coding: utf-8 -_-
from django.conf.urls import url, include
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    url('^$', views.Index, name='Index'),
    url('index$', views.Index, name='Index'),
    # url('get_domains$', views.GetDomains, name='GetDomains'),
    # url('send_telegram$', views.SendTelegram, name='SendTelegram'),
    # url('get_at_users$', views.get_at_users, name='getAtUsers'),
    # #url('get_telegram_user_id$', views.GetTelegramUserId, name='GetTelegramUserId'),

    # # 发送telegram信息
    # url('telegram$', views.telegram_group, name='TelegramGroup'),
    # url('telegram/sendgroupmessage$', views.telegram_sendgroupmessage, name='Telegramsendgroupmessage'),
    # url('telegram/uploadimgs$', views.TelegramUploadimgs, name='TelegramUploadimgs'),
]
