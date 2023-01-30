# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('djangobmf_quotation', '0007_product_to_framework_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quotation',
            name='products',
            field=models.ManyToManyField(editable=False, through='djangobmf_quotation.QuotationProduct', to=settings.BMF_CONTRIB_PRODUCT),
            preserve_default=True,
        ),
    ]
