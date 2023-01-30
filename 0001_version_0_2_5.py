# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    replaces = [('djangobmf_address', '0001_version_0_2_0'), ('djangobmf_address', '0002_remove_uuid'), ('djangobmf_address', '0003_changed_verbose_name')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('djangobmf_customer', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('modified', models.DateTimeField(auto_now=True, null=True, verbose_name='Modified')),
                ('created', models.DateTimeField(null=True, verbose_name='Created', auto_now_add=True)),
                ('is_active', models.BooleanField(verbose_name='Is active', default=True)),
                ('is_billing', models.BooleanField(verbose_name='Is billing', default=True)),
                ('is_shipping', models.BooleanField(verbose_name='Is shipping', default=True)),
                ('default_billing', models.BooleanField(verbose_name='Default billing', default=False)),
                ('default_shipping', models.BooleanField(verbose_name='Default shipping', default=False)),
                ('name', models.CharField(max_length=255, null=True, verbose_name='Name')),
                ('name2', models.CharField(blank=True, max_length=255, null=True, verbose_name='Name2')),
                ('street', models.CharField(max_length=255, null=True, verbose_name='Street')),
                ('zip', models.CharField(max_length=255, null=True, verbose_name='Zipcode')),
                ('city', models.CharField(max_length=255, null=True, verbose_name='City')),
                ('state', models.CharField(blank=True, max_length=255, null=True, verbose_name='State')),
                ('country', models.CharField(max_length=255, null=True, verbose_name='Country')),
                ('created_by', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, verbose_name='Created by', on_delete=django.db.models.deletion.SET_NULL, blank=True, related_name='+', editable=False)),
                ('customer', models.ForeignKey(to=settings.BMF_CONTRIB_CUSTOMER, related_name='customer_address')),
                ('modified_by', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, verbose_name='Modified by', on_delete=django.db.models.deletion.SET_NULL, blank=True, related_name='+', editable=False)),
            ],
            options={
                'verbose_name_plural': 'Addresses',
                'swappable': 'BMF_CONTRIB_ADDRESS',
                'abstract': False,
                'ordering': ['name'],
                'verbose_name': 'Address',
            },
        ),
    ]
