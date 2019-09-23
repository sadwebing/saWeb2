# Generated by Django 2.2.5 on 2019-09-23 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domainns', '0015_auto_20190923_1604'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domaintb',
            name='customer',
            field=models.IntegerField(choices=[(29, '公共客户[pub]'), (1, '阿里[ali]'), (2, '光大[guangda]'), (34, '恒达[hengda]'), (121001, '恒信[hengxin]'), (3, '乐盈|熊猫[leying]'), (4, '彩投[caitou]'), (5, '天天[tiantian]'), (6, '三德|富豪|668[sande]'), (7, 'uc彩票[uc]'), (10, 'ag彩[agcai]'), (23, '亿腾[yiteng]'), (11, '万游[klc]'), (39, '68彩[68bet]'), (40, '567彩[567bet]'), (41, '专业盘彩票[zyp]'), (42, '飞信[feixin]'), (43, '世彩堂[sct]'), (8, '谷歌[9393cp]'), (9, '苹果[188cp|3535]'), (19, '芒果[1717cp]'), (21, '乐都城[ldc]'), (36, '瑞银[ruiyin|UBS]'), (37, '勇士[warrior]'), (38, '体彩[tc]'), (13, '钻石[le7|diamond]'), (32, '世德[shide]'), (33, '图腾[tuteng]'), (31, '恒隆[henglong]'), (35, '迪拜吧[dibaiba]'), (101001, 'BB棋牌'), (101002, '汪汪棋牌')]),
        ),
        migrations.CreateModel(
            name='DoaminProjectTb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.CharField(max_length=32, unique=True)),
                ('domain', models.ManyToManyField(to='domainns.DomainTb')),
            ],
        ),
    ]
