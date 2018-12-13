from django.db import models
from django.contrib.auth.models import User

class Conector(models.Model):
    """
    """
    def get_upload_to(self, filename):
        return "certificados/%s/%s" % (self.usuario, filename)

    usuario = models.CharField(max_length=128)
    url_erp = models.URLField(max_length=255)
    url_sii = models.URLField(max_length=255)
    password = models.CharField(max_length=128)
    certificado = models.FileField(upload_to=get_upload_to)
    time_cron = models.IntegerField(default=10)

    class Meta:
        """!
        Clase que construye los meta datos del modelo
        """
        ordering = ('usuario',)
        verbose_name = 'Conector'
        verbose_name_plural = 'Conectores'

    def __str__(self):
        return self.url_erp

class Compania(models.Model):
    """
    """
    def get_upload_to(self, filename):
        return "logos/%s/%s" % (self.rut, filename)
        
    rut = models.CharField(max_length=128)
    razon_social = models.CharField(max_length=128)
    actividad_principal = models.CharField(max_length=128)
    giro = models.CharField(max_length=128)
    direccion = models.CharField(max_length=128)
    comuna = models.CharField(max_length=128)
    logo = models.FileField(upload_to=get_upload_to)

    class Meta:
        """!
        Clase que construye los meta datos del modelo
        """
        ordering = ('rut',)
        verbose_name = 'Compania'
        verbose_name_plural = 'Companias'

    def __str__(self):
        return self.rut
