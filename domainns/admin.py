from django.contrib  import admin
from domainns.models import CfAccountTb, DnspodAccountTb, AlterHistoryTb
from domainns.models import DomainDetectGroupTb, CdnAccountTb, DomainTb, DoaminProjectTb

admin.site.register(CfAccountTb)
admin.site.register(DnspodAccountTb)
admin.site.register(AlterHistoryTb)

admin.site.register(DomainDetectGroupTb)
admin.site.register(CdnAccountTb)
admin.site.register(DomainTb)
admin.site.register(DoaminProjectTb)
