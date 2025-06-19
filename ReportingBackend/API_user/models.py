from django.db import models
from django.utils.translation import gettext_lazy as _
from API.models import Salle

class Reglement(models.Model):
    ID_reglement = models.AutoField(primary_key=True, verbose_name=_('Settlement ID'))
    id_salle = models.ForeignKey('API.Salle', on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Gym'))
    CONTRAT = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Contract'))
    CLIENT = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Client'))
    DATE_CONTRAT = models.DateTimeField(null=True, blank=True, verbose_name=_('Contract Date'))
    DATE_DEBUT = models.DateTimeField(null=True, blank=True, verbose_name=_('Start Date'))
    DATE_FIN = models.DateTimeField(null=True, blank=True, verbose_name=_('End Date'))
    USERC = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Agent'))
    FAMILLE = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Family'))
    SOUSFAMILLE = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Sub-family'))
    LIBELLE = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Label'))
    DATE_ASSURANCE = models.DateTimeField(null=True, blank=True, verbose_name=_('Insurance Date'))
    MONTANT = models.DecimalField(max_digits=18, decimal_places=2, verbose_name=_('Amount'))
    MODE = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Payment Method'))
    TARIFAIRE = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Rate'))
    DATE_REGLEMENT = models.DateTimeField(null=True, blank=True, verbose_name=_('Settlement Date'))

    class Meta:
        verbose_name = _('Reglement')
        verbose_name_plural = _('Reglements')

    def __str__(self):
        return f"{_('Contract')} {self.CONTRAT} - {_('Client')} {self.CLIENT}"