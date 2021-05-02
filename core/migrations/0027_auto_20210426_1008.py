# Generated by Django 3.1.7 on 2021-04-26 10:08

from django.db import migrations


def add_balance(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Balance = apps.get_model('core', 'Balance')
    for user in User.objects.all():
        if not Balance.objects.get(user=user):
            Balance(user=user).save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_auto_20210426_0959'),
    ]

    operations = [
        migrations.RunPython(add_balance)
    ]