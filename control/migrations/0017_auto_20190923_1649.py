# Generated by Django 2.2.5 on 2019-09-23 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domainns', '0016_auto_20190923_1624'),
        ('control', '0016_auto_20190916_1638'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergrouppermissionstb',
            name='cdn_account_p',
            field=models.ManyToManyField(blank=True, to='domainns.CdnAccountTb', verbose_name='cdn账号 权限'),
        ),
        migrations.AddField(
            model_name='userpermissionstb',
            name='cdn_account_p',
            field=models.ManyToManyField(blank=True, to='domainns.CdnAccountTb', verbose_name='cdn账号 权限'),
        ),
    ]
