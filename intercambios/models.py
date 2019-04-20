from django.db import models

from mixins.models import CreationModificationDateMixin
from conectores.models import Compania
# Create your models here.


class Intercambio(CreationModificationDateMixin):

	codigo_email = models.IntegerField(null=True, default=0)
	receptor = models.ForeignKey(Compania, on_delete=models.CASCADE, blank=True, null=True)
	remisor = models.CharField(max_length=128,blank=True, null=True)
	email_remisor = models.EmailField(blank=True, null=True)
	fecha_de_recepcion = models.DateTimeField(auto_now=False, auto_now_add=False,blank=True, null=True)
	cantidad_dte = models.IntegerField(null=True, default=0)
	titulo = models.CharField(max_length=128,blank=True, null=True)
	contenido = models.TextField(null=True, blank=True)

class DteIntercambio(models.Model):

	id_intercambio = models.ForeignKey(Intercambio, on_delete=models.CASCADE, blank=True, null=True)
	dte = models.TextField(null=True, blank=True)
