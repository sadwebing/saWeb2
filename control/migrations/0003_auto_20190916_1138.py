# Generated by Django 2.2.5 on 2019-09-16 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0002_auto_20190916_1136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weburifirstleveltb',
            name='icon',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='layui图标'),
        ),
        migrations.AlterField(
            model_name='weburifirstleveltb',
            name='jump',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='跳转路由'),
        ),
        migrations.AlterField(
            model_name='weburisecondleveltb',
            name='icon',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='layui图标'),
        ),
        migrations.AlterField(
            model_name='weburisecondleveltb',
            name='jump',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='跳转路由'),
        ),
        migrations.AlterField(
            model_name='weburithirdleveltb',
            name='icon',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='layui图标'),
        ),
        migrations.AlterField(
            model_name='weburithirdleveltb',
            name='jump',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='跳转路由'),
        ),
    ]
