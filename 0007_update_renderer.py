# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djangobmf.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('djangobmf', '0006_report_settings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='renderer',
            name='key',
        ),
        migrations.AddField(
            model_name='renderer',
            name='extra',
            field=models.BooleanField(verbose_name='Extra', default=False),
        ),
        migrations.AddField(
            model_name='renderer',
            name='letter',
            field=models.BooleanField(verbose_name='Letter', default=True),
        ),
        migrations.AddField(
            model_name='renderer',
            name='letter_background',
            field=djangobmf.fields.file.FileField(null=True, verbose_name='Letter background', related_name='+', to='djangobmf.Document'),
        ),
        migrations.AddField(
            model_name='renderer',
            name='letter_extra_right',
            field=models.PositiveIntegerField(verbose_name='Letter extra right', default=10),
        ),
        migrations.AddField(
            model_name='renderer',
            name='letter_extra_top',
            field=models.PositiveIntegerField(verbose_name='Letter extra top', default=10),
        ),
        migrations.AddField(
            model_name='renderer',
            name='letter_footer_right',
            field=models.PositiveIntegerField(verbose_name='Letter footer height', default=10),
        ),
        migrations.AddField(
            model_name='renderer',
            name='letter_margin_bottom',
            field=models.PositiveIntegerField(verbose_name='Letter margin bottom', default=40),
        ),
        migrations.AddField(
            model_name='renderer',
            name='letter_margin_right',
            field=models.PositiveIntegerField(verbose_name='Letter margin right', default=10),
        ),
        migrations.AddField(
            model_name='renderer',
            name='page_background',
            field=djangobmf.fields.file.FileField(null=True, verbose_name='Page background', related_name='+', to='djangobmf.Document'),
        ),
        migrations.AddField(
            model_name='renderer',
            name='page_margin_bottom',
            field=models.PositiveIntegerField(verbose_name='Letter margin bottom', default=15),
        ),
        migrations.AddField(
            model_name='renderer',
            name='page_margin_right',
            field=models.PositiveIntegerField(verbose_name='Letter margin right', default=10),
        ),
        migrations.AddField(
            model_name='renderer',
            name='page_margin_top',
            field=models.PositiveIntegerField(verbose_name='Letter margin top', default=20),
        ),
        migrations.AddField(
            model_name='renderer',
            name='size',
            field=models.CharField(verbose_name='Size', default='A4/A', max_length=20),
        ),
    ]
