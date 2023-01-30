# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djangobmf', '0001_squashed_0_2_0'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dashboard',
            options={'ordering': ('key',)},
        ),
        migrations.RemoveField(
            model_name='dashboard',
            name='name',
        ),
        migrations.RemoveField(
            model_name='dashboard',
            name='user',
        ),
        migrations.AddField(
            model_name='dashboard',
            name='key',
            field=models.CharField(unique=True, null=True, max_length=100, db_index=True),
            preserve_default=True,
        ),
    ]
