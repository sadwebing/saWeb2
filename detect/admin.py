from django.contrib import admin
# from detect.models import groups, domains, cdn_account_t, telegram_chat_group_t, telegram_user_id_t, department_user_t
from detect.models import telegram_chat_group_t, telegram_user_id_t, department_user_t

# admin.site.register(groups)
# admin.site.register(domains)
# admin.site.register(cdn_account_t)

admin.site.register(telegram_chat_group_t)
admin.site.register(telegram_user_id_t)
admin.site.register(department_user_t)