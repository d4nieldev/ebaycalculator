# Generated by Django 3.1.5 on 2021-02-13 12:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_hipshipper'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hipshipper',
            name='sale_entry',
            field=models.OneToOneField(default=0, on_delete=django.db.models.deletion.CASCADE, to='core.saleentry'),
        ),
    ]
