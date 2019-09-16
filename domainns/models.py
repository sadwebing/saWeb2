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
