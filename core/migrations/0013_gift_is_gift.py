# Generated by Django 3.1.5 on 2021-03-27 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_balance_paypal_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='gift',
            name='is_gift',
            field=models.BooleanField(default=True),
        ),
    ]