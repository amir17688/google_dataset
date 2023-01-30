# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djangobmf.fields
import djangobmf.contrib.quotation.workflows


class Migration(migrations.Migration):

    dependencies = [
        ('djangobmf_quotation', '0003_changed_verbose_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quotation',
            name='state',
            field=djangobmf.fields.WorkflowField(workflow=djangobmf.contrib.quotation.workflows.QuotationWorkflow, max_length=32, db_index=True),
            preserve_default=True,
        ),
    ]
