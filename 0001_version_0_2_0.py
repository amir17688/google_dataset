# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion
import djangobmf.fields


class Migration(migrations.Migration):

    replaces = [
        ('djangobmf_quotation', '0001_initial'),
        ('djangobmf_quotation', '0002_optional_quotation_project'),
        ('djangobmf_quotation', '0003_optional_quotation_employee'),
        ('djangobmf_quotation', '0004_optional_quotation_customer'),
        ('djangobmf_quotation', '0005_version_0_2_0'),
        ('djangobmf_quotation', '0006_quotation_completed'),
        ('djangobmf_quotation', '0007_product_to_framework_model'),
        ('djangobmf_quotation', '0008_m2m_editable_false'),
    ]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        migrations.swappable_dependency(settings.BMF_CONTRIB_PROJECT),
        migrations.swappable_dependency(settings.BMF_CONTRIB_PRODUCT),
        migrations.swappable_dependency(settings.BMF_CONTRIB_INVOICE),
        migrations.swappable_dependency(settings.BMF_CONTRIB_EMPLOYEE),
        migrations.swappable_dependency(settings.BMF_CONTRIB_ADDRESS),
        migrations.swappable_dependency(settings.BMF_CONTRIB_CUSTOMER),
    ]

    operations = [
        migrations.CreateModel(
            name='Quotation',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('modified', models.DateTimeField(auto_now=True, null=True, verbose_name='Modified')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created')),
                ('uuid', models.CharField(blank=True, db_index=True, editable=False, null=True, max_length=100, verbose_name='UUID')),
                ('state', djangobmf.fields.OLDWorkflowField(editable=False, null=True, blank=True, max_length=32, db_index=True)),
                ('quotation_number', models.CharField(null=True, max_length=255, verbose_name='Quotation number')),
                ('net', models.FloatField(editable=False, blank=True, null=True)),
                ('date', models.DateField(null=True, verbose_name='Date')),
                ('valid_until', models.DateField(blank=True, null=True, verbose_name='Valid until')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('term_of_payment', models.TextField(blank=True, null=True, verbose_name='Term of payment')),
                ('completed', models.BooleanField(default=False, editable=False, verbose_name='Completed')),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('customer', models.ForeignKey(null=True, to=settings.BMF_CONTRIB_CUSTOMER, on_delete=django.db.models.deletion.SET_NULL)),
                ('employee', models.ForeignKey(null=True, to=settings.BMF_CONTRIB_EMPLOYEE, on_delete=django.db.models.deletion.SET_NULL)),
                ('invoice', models.OneToOneField(related_name='quotation', blank=True, editable=False, to=settings.BMF_CONTRIB_INVOICE, null=True, on_delete=django.db.models.deletion.PROTECT)),
                ('invoice_address', models.ForeignKey(related_name='invoice_quotation', blank=True, to=settings.BMF_CONTRIB_ADDRESS, null=True, on_delete=django.db.models.deletion.PROTECT)),
                ('modified_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=django.db.models.deletion.SET_NULL)),
            ],
            options={
                'verbose_name': 'Quotation',
                'ordering': ['-pk'],
                'verbose_name_plural': 'Quotations',
                'abstract': False,
                'swappable': 'BMF_CONTRIB_QUOTATION',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuotationProduct',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('modified', models.DateTimeField(auto_now=True, null=True, verbose_name='Modified')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created')),
                ('uuid', models.CharField(blank=True, db_index=True, editable=False, null=True, max_length=100, verbose_name='UUID')),
                ('name', models.CharField(null=True, max_length=255, verbose_name='Name')),
                ('price_currency', djangobmf.fields.CurrencyField(editable=False, max_length=4)),
                ('price_precision', models.PositiveSmallIntegerField(default=0, editable=False, blank=True, null=True)),
                ('price', djangobmf.fields.MoneyField(default=None, blank=True, verbose_name='Price')),
                ('amount', models.FloatField(default=1.0, null=True, verbose_name='Amount')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('created_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('modified_by', models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('product', models.ForeignKey(related_name='quotation_products', blank=True, to=settings.BMF_CONTRIB_PRODUCT, null=True, on_delete=django.db.models.deletion.PROTECT)),
                ('quotation', models.ForeignKey(related_name='quotation_products', blank=True, null=True, to=settings.BMF_CONTRIB_QUOTATION)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='quotation',
            name='products',
            field=models.ManyToManyField(editable=False, through='djangobmf_quotation.QuotationProduct', to=settings.BMF_CONTRIB_PRODUCT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='quotation',
            name='project',
            field=models.ForeignKey(null=True, to=settings.BMF_CONTRIB_PROJECT, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='quotation',
            name='shipping_address',
            field=models.ForeignKey(related_name='shipping_quotation', blank=True, to=settings.BMF_CONTRIB_ADDRESS, null=True, on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
    ]
