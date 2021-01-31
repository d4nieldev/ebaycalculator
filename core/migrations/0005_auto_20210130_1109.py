# Generated by Django 3.1.5 on 2021-01-30 09:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0004_auto_20210130_1057'),
    ]

    operations = [
        migrations.AddField(
            model_name='gift',
            name='user',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='saleentry',
            name='country',
            field=models.CharField(default='', max_length=100),
        ),
    ]
