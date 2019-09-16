from django.contrib import admin
# from detect.models import groups, domains, cdn_account_t, TelegramChatGroupTb, TelegramUserIdTb, DepartmentUserTb
from detect.models import TelegramChatGroupTb, TelegramUserIdTb, DepartmentUserTb

# admin.site.register(groups)
# admin.site.register(domains)
# admin.site.register(cdn_account_t)

admin.site.register(TelegramChatGroupTb)
admin.site.register(TelegramUserIdTb)
admin.site.register(DepartmentUserTb)