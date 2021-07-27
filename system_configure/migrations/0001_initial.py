# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SystemConfig',
            fields=[
                ('key', models.CharField(max_length=255, unique=True, serialize=False, primary_key=True)),
                ('value', models.TextField(blank=True)),
                ('description', models.CharField(default=b'', max_length=511, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='TemplateHTML',
            fields=[
                ('key', models.CharField(max_length=255, unique=True, serialize=False, primary_key=True)),
                ('body', models.TextField(blank=True)),
                ('description', models.CharField(default=b'', max_length=511, blank=True)),
            ],
        ),
    ]
