# Generated by Django 3.1.5 on 2021-03-27 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_returnedsale'),
    ]

    operations = [
        migrations.AddField(
            model_name='balance',
            name='paypal_balance',
            field=models.FloatField(default=0),
        ),
    ]