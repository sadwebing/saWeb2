from django.db import models

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