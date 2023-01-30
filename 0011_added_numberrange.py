# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('djangobmf', '0010_notification_db_optimization'),
    ]

    operations = [
        migrations.CreateModel(
            name='NumberRange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period_start', models.DateField(null=True, db_index=True)),
                ('period_final', models.DateField(null=True, db_index=True)),
                ('counter', models.PositiveIntegerField(null=True, default=1)),
                ('ct', models.ForeignKey(to='contenttypes.ContentType', related_name='+', null=True, editable=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='numbercycle',
            name='ct',
        ),
        migrations.DeleteModel(
            name='NumberCycle',
        ),
        migrations.AlterUniqueTogether(
            name='numberrange',
            unique_together=set([('ct', 'period_start', 'period_final')]),
        ),
    ]
