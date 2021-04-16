# Generated by Django 3.1.7 on 2021-04-14 13:54

from django.db import migrations

def set_pending_false(apps, schema_editor):
    ReturnedSale = apps.get_model('core', 'ReturnedSale')
    for sale in ReturnedSale.objects.all():
        sale.is_pending = False
        sale.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20210414_1321'),
    ]

    operations = [
        migrations.RunPython(set_pending_false),
    ]