import os
from enum import Enum
from django.db import models
from django.contrib.auth.models import User
from .constantes import (COMUNAS, ACTIVIDADES)
from django.core.validators import FileExtensionValidator
from .exceptions import ContrasenaDeCertificadoIncorrecta

import OpenSSL.crypto
from Crypto.Hash import MD5
from django.core.validators import MinValueValidator, MaxValueValidator
from base64 import b64decode,b64encode


class Compania(models.Model):
    """
    """
    def get_upload_to(self, filename):
        return "logos/%s/%s" % (self.rut, filename)

    def get_cert_upload_to(self, filename):

        """ 
        Crea un hash del nombre del certificado, antes de almacenarlo en 
        el servidor
        """

        #filename_base, filename_ext = os.path.splitext(filename)

        #hash = MD5.new()
        #hash.update(filename_base.encode())

        return "certificados/%s/%s" % (self.rut, filename)#(hash.hexdigest(),filename_ext.lower())
    

    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=1)     
    rut = models.CharField(max_length=128, blank=True, null=True)
    razon_social = models.CharField(max_length=128, blank=True, null=True)
    actividad_principal = models.CharField(max_length=128,choices=ACTIVIDADES, blank=True, null=True)
    giro = models.CharField(max_length=128,choices=ACTIVIDADES, blank=True, null=True)
    direccion = models.CharField(max_length=128, blank=True, null=True)
    comuna = models.CharField(max_length=128, choices=COMUNAS, blank=True, null=True)
    logo = models.FileField(upload_to=get_upload_to, blank=True, null=True)
    fecha_resolucion = models.DateField(blank=True, null=True)
    numero_resolucion = models.IntegerField(blank=True, null=True,validators=[MinValueValidator(0),MaxValueValidator(999999)])
    correo_sii = models.EmailField(blank=True, null=True)
    pass_correo_sii = models.CharField(max_length=128, blank=True, null=True)
    correo_intercambio = models.EmailField(blank=True, null=True)
    pass_correo_intercambio = models.CharField(max_length=128, blank=True, null=True)
    certificado = models.FileField('Certificado', upload_to=get_cert_upload_to,validators=[FileExtensionValidator(allowed_extensions=['pfx'])], blank=False, null=True)
    tasa_de_iva = models.IntegerField("Tasa IVA", blank=False, null=False, default=0)
    pass_certificado = models.CharField(max_length=128)
    web = models.URLField()
    


    class Meta:
        """!
        Clase que construye los meta datos del modelo
        """
        ordering = ('rut',)
        verbose_name = 'Compania'
        verbose_name_plural = 'Companias'

    def __str__(self):
        return self.razon_social

    def validar_certificado(string_archivo_pfx, password):
        """
        Recibe un archivo de certificado .pfx y su correspondiente contrasena
        y retorna una tupla con la clave privada, la clave publica y el certificado extraido del mismo
        """

        try:
            # Carga el archivo .pfx y muestra un error si la contrasena
            # es incorrecta
            p12 = OpenSSL.crypto.load_pkcs12(string_archivo_pfx, password)

        except OpenSSL.crypto.Error:

            raise ContrasenaDeCertificadoIncorrecta

        # Extraccion de clave privada
        private = OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, p12.get_privatekey()).decode()

        # Extraccion de certificado
        certificate = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, p12.get_certificate()).decode().replace('\n-----END CERTIFICATE-----\n', '').replace('-----BEGIN CERTIFICATE-----\n', '')
        # Extraccion de clave publica
        public_key = OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM,p12.get_certificate().get_pubkey()).decode()


        return (private, certificate, public_key)




class Conector(models.Model):
    """
    """
    def get_upload_to(self, filename):
        return "certificados/%s/%s" % (self.usuario, filename)

    class TIPO_DE_CONECTOR(Enum):

        factura            = ('33', 'Facturas')
        boleta             = ('39', 'Boletas')

        @classmethod
        def get_value(cls, member):
            return cls[member].value[0]

        @classmethod
        def get_default(cls):
            return cls['factura'].value[0]



    t_documento = models.CharField(max_length=128, choices=[x.value for x in TIPO_DE_CONECTOR],default=TIPO_DE_CONECTOR.get_default(),blank=True, null=True)
    empresa = models.ForeignKey(Compania, on_delete=models.CASCADE)   
    usuario = models.CharField(max_length=128, blank=True, null=True)
    url_erp = models.URLField(max_length=255, blank=True, null=True)
    url_sii = models.URLField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    certificado = models.FileField(upload_to=get_upload_to, blank=True, null=True)
    time_cron = models.IntegerField(default=10, blank=True, null=True)

    class Meta:
        """!
        Clase que construye los meta datos del modelo
        """
        ordering = ('usuario',)
        verbose_name = 'Conector'
        verbose_name_plural = 'Conectores'

    def __str__(self):
        return self.url_erp
