# Generated by Django 2.2 on 2019-04-26 08:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medikamente', '0004_auto_20190425_2140'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='medikament',
            options={'ordering': ['name', 'staerke'], 'verbose_name': 'Medicament', 'verbose_name_plural': 'Medicaments'},
        ),
        migrations.AlterModelOptions(
            name='verordnung',
            options={'verbose_name': 'Prescription', 'verbose_name_plural': 'Prescriptions'},
        ),
        migrations.AlterModelOptions(
            name='vrdfuture',
            options={'verbose_name': 'Scheduled prescription', 'verbose_name_plural': 'Scheduled prescriptions'},
        ),
        migrations.AlterField(
            model_name='bestandsveraenderung',
            name='date',
            field=models.DateField(verbose_name='Date'),
        ),
        migrations.AlterField(
            model_name='bestandsveraenderung',
            name='ref_medikament',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='medikamente.Medikament', verbose_name='Medicament'),
        ),
        migrations.AlterField(
            model_name='verordnung',
            name='ref_medikament',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='medikamente.Medikament', verbose_name='Medicament'),
        ),
    ]