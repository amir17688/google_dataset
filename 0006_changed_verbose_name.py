# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djangobmf_position', '0005_remove_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='created_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False, verbose_name='Created by', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, related_name='+'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='position',
            name='modified_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False, verbose_name='Modified by', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, related_name='+'),
            preserve_default=True,
        ),
    ]
