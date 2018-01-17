# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-04 14:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parcelhubPOS', '0013_sku_is_gst_inclusive'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tax',
            name='gst',
            field=models.DecimalField(decimal_places=2, max_digits=2, verbose_name='*GST(%)'),
        ),
    ]