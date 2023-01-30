# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings

import django

class Migration(migrations.Migration):
    dependencies = [
        ('djangobmf_invoice', '0001_initial'),
        migrations.swappable_dependency(settings.BMF_CONTRIB_PROJECT),
    ]
    operations = [
        migrations.AddField(
            model_name='invoice',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.BMF_CONTRIB_PROJECT, null=True),
            preserve_default=True,
        ),
    ]
