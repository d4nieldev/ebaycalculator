# Generated by Django 3.1.7 on 2021-06-04 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_cost_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cost',
            name='start_date',
            field=models.DateField(blank=True),
        ),
    ]
