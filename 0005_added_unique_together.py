# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djangobmf', '0004_added_active_field'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='configuration',
            unique_together=set([('app_label', 'field_name')]),
        ),
    ]
