# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def set_default_date(apps, schema_editor):
    obj = apps.get_model("djangobmf_accounting", "TransactionItem")
    for o in obj.objects.all():
        o.date = o.created
        o.save()


class Migration(migrations.Migration):

    dependencies = [
        ('djangobmf_accounting', '0002_money_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionitem',
            name='date',
            field=models.DateField(null=True, verbose_name='Date'),
        ),
        migrations.AlterModelOptions(
            name='transactionitem',
            options={'ordering': ('-date', '-draft', 'credit', 'transaction__text')},
        ),
        migrations.RunPython(set_default_date),
    ]
