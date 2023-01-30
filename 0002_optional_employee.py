# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    dependencies = [
        ('djangobmf_position', '0001_initial'),
        migrations.swappable_dependency(settings.BMF_CONTRIB_EMPLOYEE),
    ]
    operations = [
        migrations.AddField(
            model_name='position',
            name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.BMF_CONTRIB_EMPLOYEE, null=True),
            preserve_default=True,
        ),
    ]
