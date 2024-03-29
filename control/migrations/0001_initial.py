# Generated by Django 2.2.5 on 2019-09-16 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WebUriThirdLevelTb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='html title')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='第三级路由名')),
                ('jump', models.CharField(max_length=128, null=True, verbose_name='跳转路由')),
                ('icon', models.CharField(max_length=4, null=True, verbose_name='layui图标')),
                ('status', models.IntegerField(choices=[(1, '启用'), (0, '禁用')], default=1, verbose_name='是否启用')),
            ],
        ),
        migrations.CreateModel(
            name='WebUriSecondLevelTb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='html title')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='第二级路由名')),
                ('jump', models.CharField(max_length=128, null=True, verbose_name='跳转路由')),
                ('icon', models.CharField(max_length=4, null=True, verbose_name='layui图标')),
                ('status', models.IntegerField(choices=[(1, '启用'), (0, '禁用')], default=1, verbose_name='是否启用')),
                ('next_l', models.ManyToManyField(blank=True, db_constraint=False, to='control.WebUriThirdLevelTb', verbose_name='下一层路由')),
            ],
        ),
        migrations.CreateModel(
            name='WebUriFirstLevelTb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='html title')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='第一级路由名')),
                ('jump', models.CharField(max_length=128, null=True, verbose_name='跳转路由')),
                ('icon', models.CharField(max_length=4, null=True, verbose_name='layui图标')),
                ('status', models.IntegerField(choices=[(1, '启用'), (0, '禁用')], default=1, verbose_name='是否启用')),
                ('next_l', models.ManyToManyField(blank=True, db_constraint=False, to='control.WebUriSecondLevelTb', verbose_name='下一层路由')),
            ],
        ),
    ]
