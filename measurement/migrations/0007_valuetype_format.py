# Generated by Django 4.0.6 on 2022-07-15 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('measurement', '0006_alter_valuetype_options_alter_valuetype_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='valuetype',
            name='format',
            field=models.PositiveIntegerField(default=0, verbose_name='Decimal places'),
        ),
    ]
