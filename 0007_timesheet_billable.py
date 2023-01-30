# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djangobmf_timesheet', '0006_new_workflowfield'),
    ]

    operations = [
        migrations.AddField(
            model_name='timesheet',
            name='billable',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
