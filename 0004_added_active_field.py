# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djangobmf', '0003_delete_workspace'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='configuration',
            options={'ordering': ['app_label', 'field_name'], 'verbose_name_plural': 'Configurations', 'default_permissions': ('change',), 'verbose_name': 'Configuration'},
        ),
        migrations.AddField(
            model_name='configuration',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Active'),
            preserve_default=True,
        ),
    ]
