# Generated by Django 5.1.6 on 2025-06-17 17:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0001_initial'),
        ('API_user', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reglement',
            options={'verbose_name': 'Settlement', 'verbose_name_plural': 'Settlements'},
        ),
        migrations.AlterField(
            model_name='reglement',
            name='CLIENT',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Client'),
        ),
        migrations.AlterField(
            model_name='reglement',
            name='CONTRAT',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Contract'),
        ),
        migrations.AlterField(
            model_name='reglement',
            name='DATE_ASSURANCE',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Insurance Date'),
        ),
        migrations.AlterField(
            model_name='reglement',
            name='DATE_CONTRAT',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Contract Date'),
        ),
        migrations.AlterField(
            model_name='reglement',
            name='DATE_DEBUT',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Start Date'),
        ),
        migrations.AlterField(
            model_name='reglement',
            name='DATE_FIN',
            field=models.DateTimeField(blank=True, null=True, verbose_name='End Date'),
        ),
        migrations.AlterField(
            model_name='reglement',
            name='DATE_REGLEMENT',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Settlement Date'),
        ),
        migrations.AlterField(
            model_name='reglement',
            name='FAMILLE',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Family'),
        ),
        migrations.AlterField(
            model_name='reglement',
            name='ID_reglement',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='Settlement ID'),
        ),
        migrations.AlterField(
            model_name='reglement',
            name='LIBELLE',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Label'),
        ),
        migrations.AlterField(
            model_name='reglement',
            name='MODE',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Payment Method'),
        ),
        migrations.AlterField(
            model_name='reglement',
            name='MONTANT',
            field=models.DecimalField(decimal_places=2, max_digits=18, verbose_name='Amount'),
        ),
        migrations.AlterField(
            model_name='reglement',
            name='SOUSFAMILLE',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Sub-family'),
        ),
        migrations.AlterField(
            model_name='reglement',
            name='TARIFAIRE',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Rate'),
        ),
        migrations.AlterField(
            model_name='reglement',
            name='USERC',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Agent'),
        ),
        migrations.AlterField(
            model_name='reglement',
            name='id_salle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='API.salle', verbose_name='Gym'),
        ),
    ]
