# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import djangobmf.storage
import djangobmf.fields.file
import django.utils.timezone
import djangobmf.utils.generate_filename


class Migration(migrations.Migration):

    replaces = [('djangobmf', '0001_squashed_0_2_0'), ('djangobmf', '0002_dashboard_update'), ('djangobmf', '0003_delete_workspace'), ('djangobmf', '0004_added_active_field'), ('djangobmf', '0005_added_unique_together'), ('djangobmf', '0006_report_settings'), ('djangobmf', '0007_update_renderer'), ('djangobmf', '0008_renderer_filefields'), ('djangobmf', '0009_notification_rename'), ('djangobmf', '0010_notification_db_optimization'), ('djangobmf', '0011_added_numberrange'), ('djangobmf', '0012_delete_dashboard'), ('djangobmf', '0013_update_document')]

    dependencies = [
        migrations.swappable_dependency(settings.BMF_CONTRIB_CUSTOMER),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.BMF_CONTRIB_PROJECT),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('topic', models.CharField(verbose_name='Topic', blank=True, null=True, max_length=100)),
                ('text', models.TextField(verbose_name='Text', blank=True, null=True)),
                ('action', models.PositiveSmallIntegerField(verbose_name='Action', default=1, choices=[(1, 'Comment'), (2, 'Created'), (3, 'Updated'), (4, 'Workflow'), (5, 'File')], editable=False, null=True)),
                ('template', models.CharField(verbose_name='Template', editable=False, null=True, max_length=100)),
                ('parent_id', models.PositiveIntegerField()),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('parent_ct', models.ForeignKey(related_name='bmf_history_parent', to='contenttypes.ContentType')),
                ('user', models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'modified',
                'verbose_name': 'Activity',
                'ordering': ('-modified',),
                'verbose_name_plural': 'Activity',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('app_label', models.CharField(verbose_name='Application', editable=False, null=True, max_length=100)),
                ('field_name', models.CharField(verbose_name='Fieldname', editable=False, null=True, max_length=100)),
                ('value', models.TextField(verbose_name='Value', null=True)),
                ('active', models.BooleanField(verbose_name='Active', default=True)),
            ],
            options={
                'ordering': ['app_label', 'field_name'],
                'verbose_name_plural': 'Configurations',
                'abstract': False,
                'verbose_name': 'Configuration',
                'default_permissions': ('change',),
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(verbose_name='Name', blank=True, null=True, max_length=120)),
                ('mimetype', models.CharField(verbose_name='Mimetype', editable=False, null=True, max_length=120)),
                ('encoding', models.CharField(verbose_name='Encoding', editable=False, null=True, max_length=60)),
                ('description', models.TextField(verbose_name='Description', blank=True, null=True)),
                ('file', models.FileField(upload_to=djangobmf.utils.generate_filename.generate_filename, storage=djangobmf.storage.Storage(), verbose_name='File')),
                ('size', models.PositiveIntegerField(editable=False, blank=True, null=True)),
                ('sha1', models.CharField(verbose_name='SHA1', editable=False, null=True, max_length=40)),
                ('is_static', models.BooleanField(editable=False, default=True)),
                ('file_exists', models.BooleanField(default=True)),
                ('content_id', models.PositiveIntegerField(editable=False, blank=True, null=True)),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified', null=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created', null=True)),
                ('content_type', models.ForeignKey(related_name='bmf_document', null=True, editable=False, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='contenttypes.ContentType')),
                ('created_by', models.ForeignKey(related_name='+', null=True, editable=False, on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(related_name='documents', null=True, editable=False, on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.BMF_CONTRIB_CUSTOMER)),
                ('modified_by', models.ForeignKey(related_name='+', null=True, editable=False, on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(related_name='documents', null=True, editable=False, on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.BMF_CONTRIB_PROJECT)),
            ],
            options={
                'get_latest_by': 'modified',
                'verbose_name': 'Document',
                'permissions': [('view_document', 'Can view documents')],
                'verbose_name_plural': 'Documents',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('watch_id', models.PositiveIntegerField(null=True, db_index=True)),
                ('triggered', models.BooleanField(verbose_name='Triggered', default=True, editable=False, db_index=True)),
                ('unread', models.BooleanField(verbose_name='Unread', default=True, editable=False, db_index=True)),
                ('last_seen_object', models.PositiveIntegerField(null=True)),
                ('new_entry', models.BooleanField(verbose_name='New entry', default=False, db_index=True)),
                ('comments', models.BooleanField(verbose_name='Comment written', default=False, db_index=True)),
                ('files', models.BooleanField(verbose_name='File added', default=False, db_index=True)),
                ('detectchanges', models.BooleanField(verbose_name='Object changed', default=False, db_index=True)),
                ('workflow', models.BooleanField(verbose_name='Workflowstate changed', default=False, db_index=True)),
                ('modified', models.DateTimeField(verbose_name='Modified', default=django.utils.timezone.now, editable=False, null=True)),
                ('user', models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
                ('watch_ct', models.ForeignKey(to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ('-modified',),
                'verbose_name_plural': 'Watched activities',
                'abstract': False,
                'verbose_name': 'Watched activity',
                'get_latest_by': 'modified',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='NumberRange',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('period_start', models.DateField(null=True, db_index=True)),
                ('period_final', models.DateField(null=True, db_index=True)),
                ('counter', models.PositiveIntegerField(default=1, null=True)),
                ('ct', models.ForeignKey(related_name='+', null=True, editable=False, to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Renderer',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(verbose_name='Name', max_length=20)),
                ('size', models.CharField(verbose_name='Size', default='A4/A', max_length=20)),
                ('letter', models.BooleanField(verbose_name='Letter', default=True)),
                ('extra', models.BooleanField(verbose_name='Extra', default=False)),
                ('letter_margin_right', models.PositiveIntegerField(verbose_name='Letter margin right', default=10)),
                ('letter_margin_bottom', models.PositiveIntegerField(verbose_name='Letter margin bottom', default=40)),
                ('letter_extra_right', models.PositiveIntegerField(verbose_name='Letter extra right', default=10)),
                ('letter_extra_top', models.PositiveIntegerField(verbose_name='Letter extra top', default=10)),
                ('letter_footer_right', models.PositiveIntegerField(verbose_name='Letter footer height', default=10)),
                ('page_margin_right', models.PositiveIntegerField(verbose_name='Letter margin right', default=10)),
                ('page_margin_bottom', models.PositiveIntegerField(verbose_name='Letter margin bottom', default=15)),
                ('page_margin_top', models.PositiveIntegerField(verbose_name='Letter margin top', default=20)),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('letter_background', djangobmf.fields.file.FileField(related_name='+', null=True, verbose_name='Letter background', blank=True, to='djangobmf.Document')),
                ('page_background', djangobmf.fields.file.FileField(related_name='+', null=True, verbose_name='Page background', blank=True, to='djangobmf.Document')),
            ],
            options={
                'verbose_name': 'Renderer',
                'get_latest_by': 'modified',
                'verbose_name_plural': 'Renderer',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('key', models.CharField(editable=False, null=True, db_index=True, verbose_name='Key', blank=True, max_length=255)),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('contenttype', models.ForeignKey(help_text='Connect a Report to an BMF-Model', related_name='bmf_report', null=True, editable=False, blank=True, to='contenttypes.ContentType')),
                ('renderer', models.ForeignKey(help_text='Connect a Report to an Renderer', related_name='reports', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='djangobmf.Renderer')),
            ],
            options={
                'verbose_name': 'Report',
                'get_latest_by': 'modified',
                'verbose_name_plural': 'Reports',
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='configuration',
            unique_together=set([('app_label', 'field_name')]),
        ),
        migrations.AlterUniqueTogether(
            name='numberrange',
            unique_together=set([('ct', 'period_start', 'period_final')]),
        ),
        migrations.AlterUniqueTogether(
            name='notification',
            unique_together=set([('user', 'watch_ct', 'watch_id')]),
        ),
    ]
