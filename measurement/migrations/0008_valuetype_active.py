# Generated by Django 4.0.6 on 2022-07-15 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('measurement', '0007_valuetype_format'),
    ]

    operations = [
        migrations.AddField(
            model_name='valuetype',
            name='active',
            field=models.BooleanField(default=True, verbose_name='active'),
        ),
    ]
