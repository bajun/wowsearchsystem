# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('searchsystem', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='place',
            name='categories_places',
        ),
        migrations.AddField(
            model_name='place',
            name='place_cat',
            field=models.ManyToManyField(to='searchsystem.Category', through='searchsystem.PlaceCategory'),
            preserve_default=True,
        ),
    ]
