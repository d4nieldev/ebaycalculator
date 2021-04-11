# Generated by Django 3.1.7 on 2021-04-10 13:00

from django.db import migrations, models

def set_pref_month(apps, schema_editor):
    Preferences = apps.get_model('core', 'Preferences')
    for pref in Preferences.objects.all():
        if type(pref.default_month) is not bool:
            pref.default_month = True
            pref.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20210409_1839'),
    ]

    operations = [
        migrations.RunPython(set_pref_month),
        migrations.AddField(
            model_name='preferences',
            name='sort_by_date',
            field=models.BooleanField(default=False),
        ),
    ]
