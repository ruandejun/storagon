# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import servermain.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountBalance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('balance_type', models.PositiveSmallIntegerField(default=0, db_index=True, choices=[(0, b'credit'), (1, b'point'), (2, b'paypal'), (3, b'webmoney'), (4, b'ppd')])),
                ('amount', models.BigIntegerField(default=0, db_index=True)),
                ('account_id', models.CharField(default=b'', max_length=255, db_index=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Banlist',
            fields=[
                ('key', models.CharField(max_length=255, unique=True, serialize=False, primary_key=True)),
                ('expires_date', models.DateTimeField(default=None, null=True, db_index=True, blank=True)),
                ('enable', models.BooleanField(default=True, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('bill_status', models.PositiveSmallIntegerField(default=0, db_index=True, choices=[(0, b'ok'), (1, b'cancel'), (2, b'fraud')])),
                ('paygate_id', models.PositiveIntegerField(default=0, db_index=True)),
                ('plan_id', models.PositiveIntegerField(default=0, db_index=True)),
                ('money_charged', models.BigIntegerField(default=0, db_index=True)),
                ('detail', models.TextField(blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('modified_date', models.DateTimeField(auto_now=True, db_index=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('folder_type', models.PositiveSmallIntegerField(default=0, db_index=True, choices=[(0, b'normal'), (1, b'recycle')])),
                ('parent_folder', models.ForeignKey(related_name='subFolderList', blank=True, to='servermain.Folder', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PremiumKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(unique=True, max_length=255)),
                ('plan_id', models.PositiveSmallIntegerField(default=0, db_index=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('activated_date', models.DateTimeField(default=None, null=True, db_index=True, blank=True)),
                ('activated_user', models.ForeignKey(related_name='activatedPremiumKey', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('bill', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='servermain.Bill')),
                ('reseller', models.ForeignKey(related_name='resellPremiumKey', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RealFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('file_size', models.BigIntegerField(default=0, db_index=True)),
                ('file_hash', models.CharField(max_length=255, db_index=True)),
                ('file_location', models.CharField(max_length=255, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='ServerFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('server_status', models.PositiveSmallIntegerField(default=0, db_index=True, choices=[(0, b'normal'), (1, b'offline'), (2, b'downloadOnly')])),
                ('ip_address', models.CharField(max_length=255, db_index=True)),
                ('server_address', models.CharField(max_length=255, db_index=True)),
                ('priority', models.PositiveSmallIntegerField(default=0, db_index=True)),
                ('total_storage', models.BigIntegerField(default=0, db_index=True)),
                ('reserved_storage', models.BigIntegerField(default=0, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='TransactionLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('transaction_type', models.PositiveSmallIntegerField(default=0, db_index=True, choices=[(0, b'agency'), (1, b'referer'), (2, b'website'), (3, b'pay'), (4, b'transfer'), (5, b'ppd'), (6, b'rebill'), (7, b'refererPPD')])),
                ('transaction_status', models.PositiveSmallIntegerField(default=0, db_index=True, choices=[(0, b'auto'), (1, b'manual'), (2, b'revert')])),
                ('amount', models.BigIntegerField(default=0, db_index=True)),
                ('data', models.TextField(blank=True)),
                ('balance', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='servermain.AccountBalance', null=True)),
                ('invoice_bill', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='servermain.Bill', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserApply',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('modified_date', models.DateTimeField(auto_now=True, db_index=True)),
                ('apply_type', models.PositiveSmallIntegerField(default=0, db_index=True, choices=[(0, b'becomeAffiliate'), (1, b'payAffiliate'), (2, b'becomeAffiliatePPD'), (3, b'becomeAffiliatePPS')])),
                ('apply_status', models.PositiveSmallIntegerField(default=0, db_index=True, choices=[(0, b'processing'), (1, b'accepted'), (2, b'rejected')])),
                ('data', models.TextField(default=b'', null=True, blank=True)),
                ('user', models.ForeignKey(related_name='application', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('modified_date', models.DateTimeField(auto_now=True, db_index=True)),
                ('file_name', models.CharField(max_length=255, db_index=True)),
                ('erfk', models.CharField(max_length=1024, null=True, blank=True)),
                ('last_download_date', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('download_count', models.PositiveIntegerField(default=0, db_index=True)),
                ('file_mode', models.PositiveSmallIntegerField(default=0, db_index=True, choices=[(0, b'normal'), (1, b'premiumOnly'), (2, b'private')])),
                ('string_id', models.CharField(default=servermain.models.generateID, max_length=255, db_index=True)),
                ('folder', models.ForeignKey(related_name='fileList', blank=True, to='servermain.Folder', null=True)),
                ('realFile', models.ForeignKey(to='servermain.RealFile')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('modified_date', models.DateTimeField(auto_now=True, db_index=True)),
                ('full_name', models.CharField(max_length=255, db_index=True)),
                ('email', models.CharField(db_index=True, max_length=255, null=True, blank=True)),
                ('address', models.TextField(blank=True)),
                ('account_type', models.PositiveSmallIntegerField(default=0, db_index=True, choices=[(0, b'user'), (1, b'affiliate'), (2, b'reseller'), (3, b'affiliatePPD')])),
                ('account_status', models.PositiveSmallIntegerField(default=0, db_index=True, choices=[(0, b'normal'), (1, b'emailNotActivated'), (2, b'banned'), (3, b'temporary')])),
                ('storage_space', models.BigIntegerField(default=0, db_index=True)),
                ('plan_id', models.PositiveIntegerField(default=0, db_index=True)),
                ('plan_expired', models.DateTimeField(db_index=True, blank=True)),
                ('eumk', models.CharField(max_length=1024, null=True, blank=True)),
                ('signup_ip', models.CharField(db_index=True, max_length=255, null=True, blank=True)),
                ('referer', models.ForeignKey(related_name='refererList', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('referer2', models.ForeignKey(related_name='referer2List', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WebsiteAgency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('website_domain', models.CharField(db_index=True, unique=True, max_length=255, blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('modified_date', models.DateTimeField(auto_now=True, db_index=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='realfile',
            name='serverFile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='servermain.ServerFile', null=True),
        ),
        migrations.AddField(
            model_name='bill',
            name='userFile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='servermain.UserFile', null=True),
        ),
    ]
