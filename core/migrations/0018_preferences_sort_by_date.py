# Generated by Django 3.1.7 on 2021-04-10 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20210409_1839'),
    ]

    operations = [            
        migrations.AddField(
            model_name='preferences',
            name='sort_by_date',
            field=models.BooleanField(default=False),
        ),
    ]
