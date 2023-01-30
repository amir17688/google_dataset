# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djangobmf_timesheet', '0003_version_0_2_0'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timesheet',
            name='uuid',
        ),
    ]
