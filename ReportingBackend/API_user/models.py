from django.db import models
from API.models import Salle

class Reglement(models.Model):
    ID_reglement = models.AutoField(primary_key=True)
    id_salle = models.ForeignKey('API.Salle', on_delete=models.CASCADE, null=True, blank=True)
    CONTRAT = models.CharField(max_length=50, null=True, blank=True)
    CLIENT = models.CharField(max_length=255, null=True, blank=True)
    DATE_CONTRAT = models.DateTimeField(null=True, blank=True)
    DATE_DEBUT = models.DateTimeField(null=True, blank=True)
    DATE_FIN = models.DateTimeField(null=True, blank=True)
    USERC = models.CharField(max_length=50, null=True, blank=True)
    FAMILLE = models.CharField(max_length=50, null=True, blank=True)
    SOUSFAMILLE = models.CharField(max_length=50, null=True, blank=True)
    LIBELLE = models.CharField(max_length=255, null=True, blank=True)
    DATE_ASSURANCE = models.DateTimeField(null=True, blank=True)
    MONTANT = models.DecimalField(max_digits=18, decimal_places=2)
    MODE = models.CharField(max_length=50, null=True, blank=True)
    TARIFAIRE = models.CharField(max_length=50, null=True, blank=True)
    DATE_REGLEMENT = models.DateTimeField(null=True, blank=True)

    def __str__(self):
            return f"Contrat {self.CONTRAT} - Client {self.CLIENT}"
