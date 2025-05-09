# Generated by Django 5.1.6 on 2025-04-21 15:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('API', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reglement',
            fields=[
                ('ID_reglement', models.AutoField(primary_key=True, serialize=False)),
                ('CONTRAT', models.CharField(blank=True, max_length=50, null=True)),
                ('CLIENT', models.CharField(blank=True, max_length=255, null=True)),
                ('DATE_CONTRAT', models.DateTimeField(blank=True, null=True)),
                ('DATE_DEBUT', models.DateTimeField(blank=True, null=True)),
                ('DATE_FIN', models.DateTimeField(blank=True, null=True)),
                ('USERC', models.CharField(blank=True, max_length=50, null=True)),
                ('FAMILLE', models.CharField(blank=True, max_length=50, null=True)),
                ('SOUSFAMILLE', models.CharField(blank=True, max_length=50, null=True)),
                ('LIBELLE', models.CharField(blank=True, max_length=255, null=True)),
                ('DATE_ASSURANCE', models.DateTimeField(blank=True, null=True)),
                ('MONTANT', models.DecimalField(decimal_places=2, max_digits=18)),
                ('MODE', models.CharField(blank=True, max_length=50, null=True)),
                ('TARIFAIRE', models.CharField(blank=True, max_length=50, null=True)),
                ('DATE_REGLEMENT', models.DateTimeField(blank=True, null=True)),
                ('id_salle', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='API.salle')),
            ],
        ),
    ]
