# Generated by Django 4.0.6 on 2022-08-08 12:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medicament', '0007_alter_stockchange_reason'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='medicament',
            options={'ordering': ['name', 'strength'], 'verbose_name': 'Medicament', 'verbose_name_plural': 'Medikamente'},
        ),
        migrations.AlterModelOptions(
            name='stockchange',
            options={'ordering': ['-date'], 'verbose_name': 'Bestandsveränderung', 'verbose_name_plural': 'Bestandsveränderungen'},
        ),
        migrations.AddField(
            model_name='medicament',
            name='last_calc',
            field=models.DateField(null=True, verbose_name='Last stock calculation'),
        ),
        migrations.AlterField(
            model_name='medicament',
            name='package',
            field=models.PositiveIntegerField(help_text='Tablette(n)', verbose_name='Packungsgröße'),
        ),
        migrations.AlterField(
            model_name='medicament',
            name='producer',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Hersteller'),
        ),
        migrations.AlterField(
            model_name='medicament',
            name='stock',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=6, verbose_name='Bestand'),
        ),
        migrations.AlterField(
            model_name='medicament',
            name='strength',
            field=models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Stärke'),
        ),
        migrations.AlterField(
            model_name='stockchange',
            name='medicament',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='medicament.medicament', verbose_name='Medicament'),
        ),
        migrations.AlterField(
            model_name='stockchange',
            name='reason',
            field=models.CharField(choices=[('00', 'Verbrauch (-)'), ('01', 'Neue Packung (+)'), ('02', 'Einnahme vergessen (+)'), ('03', 'Einnahme ausgesetzt (+)'), ('04', 'Verfallsdatum erreicht (-)'), ('05', 'Dosis erhöht (-)'), ('98', 'Sonstiges (+)'), ('99', 'Sonstiges (-)')], max_length=2, verbose_name='Grund'),
        ),
    ]