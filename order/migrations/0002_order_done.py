# Generated by Django 4.1.1 on 2022-09-24 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='done',
            field=models.BooleanField(default=False, verbose_name='Done'),
        ),
    ]
