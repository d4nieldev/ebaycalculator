# Generated by Django 3.1.5 on 2021-01-29 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='saleentry',
            name='date',
            field=models.DateField(),
        ),
    ]
