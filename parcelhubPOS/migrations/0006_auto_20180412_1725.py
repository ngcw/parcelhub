# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-12 17:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parcelhubPOS', '0005_auto_20180412_1723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statementofaccountinvoice',
            name='description',
            field=models.CharField(blank=True, max_length=254, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='statementofaccountinvoice',
            name='reference',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
