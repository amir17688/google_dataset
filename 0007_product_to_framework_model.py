# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('djangobmf_quotation', '0006_quotation_completed'),
    ]

    operations = [
        migrations.AddField(
            model_name='quotationproduct',
            name='created',
            field=models.DateTimeField(null=True, verbose_name='Created', auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='quotationproduct',
            name='created_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False, blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='quotationproduct',
            name='modified',
            field=models.DateTimeField(null=True, verbose_name='Modified', auto_now=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='quotationproduct',
            name='modified_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False, blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='quotationproduct',
            name='uuid',
            field=models.CharField(db_index=True, verbose_name='UUID', editable=False, blank=True, null=True, max_length=100),
            preserve_default=True,
        ),
    ]
