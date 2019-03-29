import datetime
from base64 import b64decode,b64encode

from django.db import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from conectores.constantes import (COMUNAS, ACTIVIDADES)
from conectores.models import Compania
from facturas.models import Factura
from folios.models import Folio
from folios.exceptions import ElCafNoTieneMasTimbres
from mixins.models import CreationModificationDateMixin

from bs4 import BeautifulSoup
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5


class notaCredito(CreationModificationDateMixin):
	"""!
	Modelo Nota de Credito
	"""
	status = models.CharField(max_length=128,blank=True, null=True)
	compania = models.ForeignKey(Compania, on_delete=models.CASCADE, blank=True, null=True)
	ref_factura = models.ForeignKey(Factura, on_delete=models.CASCADE, blank=True, null=True)
	numero_factura = models.CharField(max_length=128, blank=True, null=True, db_index=True)
	senores = models.CharField(max_length=128, blank=True, null=True)
	direccion = models.CharField(max_length=128, blank=True, null=True)
	transporte = models.CharField(max_length=128, blank=True, null=True)
	despachar = models.CharField(max_length=128, blank=True, null=True)
	observaciones = models.CharField(max_length=255, blank=True, null=True)
	giro = models.CharField(max_length=128, blank=True, null=True)
	condicion_venta = models.CharField(max_length=128, blank=True, null=True)
	vencimiento = models.DateField(blank=True, null=True)
	vendedor = models.CharField(max_length=128, blank=True, null=True)
	rut = models.CharField(max_length=128, blank=True, null=True)
	fecha = models.DateField(blank=True, null=True)
	guia = models.CharField(max_length=128, blank=True, null=True)
	orden_compra = models.CharField(max_length=128, blank=True, null=True)
	nota_venta = models.CharField(max_length=128, blank=True, null=True)
	productos = models.TextField(blank=True, null=True)
	monto_palabra = models.CharField(max_length=128, blank=True, null=True)
	neto = models.CharField(max_length=128, blank=True, null=True)
	excento = models.CharField(max_length=128, blank=True, null=True)
	iva = models.CharField(max_length=128, blank=True, null=True)
	total = models.CharField(max_length=128, blank=True, null=True)
	n_folio = models.IntegerField(null=True, default=0)
	dte_xml = models.TextField(null=True, blank=True)
	
	class Meta:
		ordering = ('numero_factura',)
		verbose_name = 'Nota de Credito'
		verbose_name_plural = 'Notas de Credito'
		def __str__(self):
			return self.numero_factura

	def recibir_folio(self, folio):
		if isinstance(folio, Folio):
			try:
				n_folio = folio.asignar_folio()
			except (ElCafNoTieneMasTimbres, ValueError):
				raise ElCafNoTieneMasTimbres
			assert type(n_folio) == int, "folio no es entero"
			self.n_folio = n_folio 
		else: 
			return 

	def _firmar_dd(data, folio, instance): 
		timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
		#timestamp = "{}T{}".format(now[0],now[1])
		sin_aplanar = render_to_string('snippets/DD_tag_nc.xml', {'data':data,'folio':folio, 'instance':instance, 'timestamp':timestamp})
		digest_string = sin_aplanar.replace('\n','').replace('\t','').replace('\r','')
		RSAprivatekey = RSA.importKey(folio.pem_private)
		private_signer = PKCS1_v1_5.new(RSAprivatekey)
		digest = SHA.new()
		digest.update(digest_string.encode('iso8859-1'))
		sign = private_signer.sign(digest)
		firma = '<FRMT algoritmo="SHA1withRSA">{}</FRMT>'.format(b64encode(sign).decode())
		sin_aplanar += firma
		return sin_aplanar

	
	def firmar_documento(etiqueta_DD, datos, folio, compania, instance):

		"""
		Llena los campos de la etiqueta <Documento>, y la firma usando la 
		plantilla signature.xml. Retorna la etiquta <Documento> con sus datos y 
		la correspondiente firma con la clave privada cargada por el usuario en
		el certificado.
		"""

		now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").split()

		# Crea timestamp en formato correspondiente
		timestamp = "{}T{}".format(now[0],now[1])

		# Llena los datos de la plantilla Documento_tag.xml con la informacion pertinente
		documento_sin_aplanar = render_to_string(
			'snippets/Documento_tag_nc.xml', {
				'datos':datos,
				'folio':folio, 
				'compania':compania, 
				'timestamp':timestamp,
				'DD':etiqueta_DD,
				'instance':instance
			})


		# sii_sdk = SII_SDK()
		# set_dte_sin_aplanar = sii_sdk.generalSign(compania,documento_sin_aplanar,pass_certificado)


		# Elimina tabulaciones y espacios para la generacion del digest
		# digest_string = documento_sin_aplanar.replace('\n','').replace('\t','').replace('\r','')

		# Crea firma electronica compuesta utilizando la plantillka signature.xml
		# firma_electronica = generar_firma_con_certificado(compania, digest_string)

		# Llena la plantilla signature.xml con los datos de la firma electronica 
		# signature_tag = render_to_string('snippets/signature.xml', {'signature':firma_electronica})

		# Agrega la plantilla signature.xml al final del documento
		# documento_sin_aplanar += "\n{}".format(signature_tag)
	
		return documento_sin_aplanar

	def firmar_etiqueta_set_dte(compania, folio, etiqueta_Documento):


		# Genera timestamp en formato correspondiente
		timestamp_firma = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
		#timestamp_firma = "{}T{}".format(now[0],now[1])

		# LLena la plantilla set_DTE_tag.xml con los datos correspondientes
		set_dte_sin_aplanar = render_to_string(
			'snippets/set_DTE_tag.xml', {
				'compania':compania, 
				'folio':folio, 
				'timestamp_firma':timestamp_firma,
				'documento': etiqueta_Documento
			}
		)

		# Se firmó el archivo xml
		#sii_sdk = SII_SDK()
		#set_dte_sin_aplanar = sii_sdk.generalSign(compania,set_dte_sin_aplanar,pass_certificado)

		# Crea el digest eliminando espacios y tabulaciones
		# digest_string = set_dte_sin_aplanar.replace('\n','').replace('\t','').replace('\r','')

		# Firma el digest y retorna diccionario con datos de la firma
		# firma_electronica = generar_firma_con_certificado(compania, digest_string)

		# Llena los datos de la plantilla signature.xml con los datos de la firma
		# signature_tag = render_to_string('snippets/signature.xml', {'signature':firma_electronica})


		# Agrega la firma al final del documento 
		# set_dte_sin_aplanar += "\n{}".format(signature_tag)

		return set_dte_sin_aplanar

	def generar_documento_final(compania,etiqueta_SetDte,pass_certificado=None):

		"""
		Incorpora todo el documento firmado al la presentacion final y elimina 
		las tabulaciones.

		"""
		# Incorpora todo el documento firmado al la presentacion final y elimina 
		# las tabulaciones.

		documento_final = render_to_string('nc_base.xml', {'set_DTE':etiqueta_SetDte})

		# Se firmó el archivo xml
		# sii_sdk = SII_SDK()
		# set_dte_sin_aplanar = sii_sdk.multipleSign(compania,documento_final,pass_certificado,1)
		#set_dte_sin_aplanar = sii_sdk.generalSign(compania,set_dte_sin_aplanar,pass_certificado,1)

		#documento_final_sin_tabs = documento_final.replace('\t','').replace('\r','')

		#print(set_dte_sin_aplanar)

		# return '<?xml version="1.0" encoding="ISO-8859-1"?>'+set_dte_sin_aplanar
		# return documento_final_sin_tabs

		return documento_final
