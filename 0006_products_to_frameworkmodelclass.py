# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('djangobmf_invoice', '0005_version_0_2_0'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoiceproduct',
            name='created',
            field=models.DateTimeField(null=True, auto_now_add=True, verbose_name='Created'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invoiceproduct',
            name='created_by',
            field=models.ForeignKey(null=True, related_name='+', to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL, editable=False, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invoiceproduct',
            name='modified',
            field=models.DateTimeField(null=True, auto_now=True, verbose_name='Modified'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invoiceproduct',
            name='modified_by',
            field=models.ForeignKey(null=True, related_name='+', to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL, editable=False, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invoiceproduct',
            name='uuid',
            field=models.CharField(null=True, verbose_name='UUID', db_index=True, max_length=100, editable=False, blank=True),
            preserve_default=True,
        ),
    ]
