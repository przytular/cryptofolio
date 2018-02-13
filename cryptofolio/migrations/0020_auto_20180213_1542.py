# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-13 14:42
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cryptofolio', '0019_addressinput'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrencyTimestamp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(default='BTC', max_length=10)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='currency',
            name='timestamp',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
