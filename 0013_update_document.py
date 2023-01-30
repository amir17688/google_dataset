# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.BMF_CONTRIB_CUSTOMER),
        migrations.swappable_dependency(settings.BMF_CONTRIB_PROJECT),
        ('djangobmf', '0012_delete_dashboard'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='customer_pk',
        ),
        migrations.RemoveField(
            model_name='document',
            name='project_pk',
        ),
        migrations.AddField(
            model_name='document',
            name='customer',
            field=models.ForeignKey(null=True, related_name='documents', to=settings.BMF_CONTRIB_CUSTOMER, on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False),
        ),
        migrations.AddField(
            model_name='document',
            name='description',
            field=models.TextField(null=True, verbose_name='Description', blank=True),
        ),
        migrations.AddField(
            model_name='document',
            name='encoding',
            field=models.CharField(max_length=60, null=True, editable=False, verbose_name='Encoding'),
        ),
        migrations.AddField(
            model_name='document',
            name='file_exists',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='document',
            name='mimetype',
            field=models.CharField(max_length=120, null=True, editable=False, verbose_name='Mimetype'),
        ),
        migrations.AddField(
            model_name='document',
            name='project',
            field=models.ForeignKey(null=True, related_name='documents', to=settings.BMF_CONTRIB_PROJECT, on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False),
        ),
        migrations.AddField(
            model_name='document',
            name='sha1',
            field=models.CharField(max_length=40, null=True, editable=False, verbose_name='SHA1'),
        ),
        migrations.AlterField(
            model_name='document',
            name='name',
            field=models.CharField(verbose_name='Name', blank=True, null=True, max_length=120),
        ),
        migrations.AlterModelOptions(
            name='document',
            options={'verbose_name_plural': 'Documents', 'get_latest_by': 'modified', 'verbose_name': 'Document', 'permissions': [('view_document', 'Can view documents')]},
        ),
    ]
