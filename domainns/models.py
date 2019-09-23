from django.db    import models
from django.utils import timezone
from control.middleware.config import choices_s, choices_customer, choices_permission, choices_product, choices_proj

class CfAccountTb(models.Model):
    '''
        CloudFlare 账号表
    '''
    name  = models.CharField(max_length=32, unique=True)
    email = models.CharField(max_length=128, null=False)
    key   = models.CharField(max_length=128, null=False)

    def __str__(self):
    	return " | ".join([self.name, self.email])

class DnspodAccountTb(models.Model):
    '''
        DnsPod 账号表
    '''
    name  = models.CharField(max_length=32, unique=True)
    email = models.CharField(max_length=128, null=False)
    key   = models.CharField(max_length=128, null=False)
    
    def __str__(self):
    	return " | ".join([self.name, self.email])

class AlterHistoryTb(models.Model):
    '''
        CF和DNSPOD 域名解析修改记录表
    '''
    choices_action = (
        ('change', '修改'), 
        ('add',    '新增'),
        ('delete', '删除'),
    )

    time    = models.CharField(max_length=32, null=False)
    req_ip  = models.CharField(max_length=128, null=False)
    user    = models.CharField(max_length=32, null=False)
    pre_rec = models.CharField(max_length=256, null=False)
    now_rec = models.CharField(max_length=256, null=False)
    action  = models.CharField(max_length=10, choices=choices_action, default='change')
    status  = models.BooleanField(default=True)

    def __str__(self):
        return " | ".join([self.time, self.user, self.pre_rec, self.now_rec, self.get_action_display(), str(self.status)])

class DomainDetectGroupTb(models.Model):
    '''
        域名检测的参数表
    '''
    group  = models.CharField(max_length=128, unique=True)
    client = models.CharField(max_length=12, null=False)
    method = models.CharField(max_length=12, null=False)
    ssl    = models.IntegerField(choices=choices_s, default=1)
    retry  = models.IntegerField(default=3)
    def __str__(self):
        if self.ssl == 1:
            ssl = 'ssl'
        else:
            ssl = 'nossl'
        return " | ".join([self.group, self.client, self.method, ssl])
        
class CdnAccountTb(models.Model):
    '''
        CDN 账号表
    '''
    choices_cdn = (
        (0, 'tencent'),
        (1, 'wangsu'),
        (2, 'aws'),
        )

    name      = models.IntegerField(choices=choices_cdn)
    account   = models.CharField(max_length=64, null=False)
    secretid  = models.CharField(max_length=128, null=False)
    secretkey = models.CharField(max_length=128, null=False)
    status    = models.IntegerField(choices=choices_s, default=1)

    class Meta:
        unique_together = ('name', 'account')
    def __str__(self):
        return " | ".join([self.get_name_display(), self.account])

class DomainTb(models.Model):
    '''
        域名表
    '''
    #protocol = models.IntegerField(choices=choices_n, default=1) 
    name       = models.CharField(max_length=128, unique=True, null=False)
    product    = models.IntegerField(choices=choices_product, default=12)
    customer   = models.IntegerField(choices=choices_customer)
    group      = models.ForeignKey(DomainDetectGroupTb, on_delete=models.CASCADE)
    #chat_group = models.ManyToManyField(telegram_chat_group_t, blank=True)
    content    = models.CharField(max_length=128, blank=True)
    status     = models.IntegerField(choices=choices_s, default=1)
    cdn        = models.ManyToManyField(CdnAccountTb, blank=True)
    cf         = models.ForeignKey(CfAccountTb, on_delete=models.CASCADE, blank=True, null=True)
    cf_content = models.CharField(max_length=128, blank=True)
    ws_content = models.CharField(max_length=128, blank=True)
    ng_content = models.CharField(max_length=128, blank=True)
    auto_m_dns = models.IntegerField(choices=choices_s, default=0)
    mod_date   = models.DateTimeField('解析最后修改日期', default=timezone.now)
    
    def __str__(self):
        if self.group.ssl == 1:
            ssl = 'ssl'
        else:
            ssl = 'nossl'
        # return self.name
        return " | ".join([str(self.get_customer_display()), self.name, ' : '.join([self.group.client, self.group.method, ssl]), self.get_status_display()])

class DoaminProjectTb(models.Model):
    '''
        不同项目或者种类，域名表
    '''
    project = models.CharField(max_length=32, unique=True, null=False)
    domain  = models.ManyToManyField(DomainTb)
    status  = models.IntegerField(choices=choices_s, default=1)
    #cdn     = models.ManyToManyField(cdn_t)

    def __str__(self):
        return self.project