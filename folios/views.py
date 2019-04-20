import datetime

from django.views.generic import CreateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import IntegrityError
from django.db.transaction import TransactionManagementError
from django.utils import timezone

from lxml import etree
from bs4 import BeautifulSoup
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import construct
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from base64 import b64decode,b64encode

from .forms import FolioCreateForm
from conectores.models import Compania
from .models import Folio

# Create your views here.


class FolioCreateView(LoginRequiredMixin, CreateView):
	template_name = 'folio-create-view.html'
	form_class = FolioCreateForm
	success_url = reverse_lazy('folios:registrar')

	def form_valid(self, form):
		instance = form.save(commit=False)
		context = super().get_context_data()
		try:
			xml = instance.caf.read()
			soup = BeautifulSoup(xml, 'xml')
			root = etree.fromstring(xml)
			rut = root.xpath('//AUTORIZACION/CAF/DA/RE/text()')[0]
			razon_social_caf = root.xpath('//AUTORIZACION/CAF/DA/RS/text()')[0]
			idk = root.xpath('//AUTORIZACION/CAF/DA/IDK/text()')[0]
			firma_da = root.xpath('//AUTORIZACION/CAF/FRMA/text()')[0]
			tipo_de_documento = root.xpath('//AUTORIZACION/CAF/DA/TD/text()')[0]
			rango_desde = root.xpath('//AUTORIZACION/CAF/DA/RNG/D/text()')[0]
			rango_hasta = root.xpath('//AUTORIZACION/CAF/DA/RNG/H/text()')[0]
			folios_disponibles = (int(rango_hasta) - int(rango_desde)) + 1
			fecha_de_autorizacion = root.xpath('//AUTORIZACION/CAF/DA/FA/text()')[0]
			pk_modulo = root.xpath('//AUTORIZACION/CAF/DA/RSAPK/M/text()')[0]
			pk_exponente = root.xpath('//AUTORIZACION/CAF/DA/RSAPK/E/text()')[0]
			pem_private = root.xpath('//AUTORIZACION/RSASK/text()')[0]
			pem_public = root.xpath('//AUTORIZACION/RSAPUBK/text()')[0]
			assert pem_public, "Error de obtencion de clave publica"
			assert pem_private, "Error de obtencion de clave privada"
		except:
			messages.error(self.request, 'Algo anda mal con el CAF')
			return super().form_invalid(form)
		try:

			decoded_exponent = int.from_bytes(b64decode(pk_exponente), 'big')
			decoded_modulus = int.from_bytes(b64decode(pk_modulo), 'big')
			assert decoded_modulus
			assert decoded_exponent
			sii_pub = construct((decoded_modulus,decoded_exponent))
			sii_final = sii_pub.exportKey('PEM').decode('ascii')
			sii_final = sii_final.replace('\n','').replace('\t','').replace('\r','')
			pem_public = pem_public.replace('\n','').replace('\t','').replace('\r','')
			print(sii_final)
			print(pem_public)
			assert sii_final == pem_public

		except:
			messages.error(self.request, 'La clave publica no fue validada correctamente')
			return super().form_invalid(form)

		try:

			RSAprivatekey = RSA.importKey(pem_private)
			private_signer = PKCS1_v1_5.new(RSAprivatekey)
			digest = SHA.new()
			digest.update(b'mensaje de prueba')
			sign = private_signer.sign(digest)
			sign = b64encode(sign)
			public_signer = PKCS1_v1_5.new(sii_pub)
			verification = public_signer.verify(digest, b64decode(sign))
			assert verification

		except:

			messages.error(self.request, 'Clave publica y clave privada no coinciden')
			return super().form_invalid(form)

		try:
			compania = Compania.objects.get(razon_social=instance.empresa)
			if compania and compania.rut.split('-') == rut.split('-'):
				instance.rut = rut
			else:
				raise ValueError
		except:

			messages.error(self.request, 'El CAF no corresponde con la compañía asignada')
			return super().form_invalid(form)


		date_list = fecha_de_autorizacion.split('-')
		fecha_de_autorizacion = timezone.make_aware(datetime.datetime(int(date_list[0]),int(date_list[1]),int(date_list[2])))
		# fecha_de_autorizacion = datetime.datetime(int(date_list[0]),int(date_list[1]),int(date_list[2]))


		instance.tipo_de_documento = int(tipo_de_documento)
		instance.rango_desde = int(rango_desde)
		instance.rango_hasta = int(rango_hasta)
		instance.folio_actual = rango_desde
		instance.folios_disponibles = folios_disponibles
		instance.fecha_de_autorizacion = fecha_de_autorizacion
		instance.pk_modulo = pk_modulo
		instance.pk_exponente = pk_exponente
		instance.pem_public = pem_public
		instance.pem_private = pem_private
		instance.razon_social = razon_social_caf
		instance.idk = idk
		instance.firma = firma_da


		try:
			hash_ = instance.hacer_hash()
			if Folio.objects.filter(unique_hash=hash_).exists():
				raise IntegrityError
			else:
				instance.unique_hash = hash_
				instance.save()
		except:
			messages.error(self.request, 'El archivo CAF ya existe')
			return super().form_invalid(form)

		messages.success(self.request, 'Archivo CAF añadido exitosamente')

		return super().form_valid(form)

	def form_invalid(self, form):

		messages.error(self.request, 'No se pudo agregar el archivo')
		return super().form_invalid(form)

	def get_context_data(self, *args, **kwargs):

		context = super().get_context_data(*args, **kwargs)
		folios_list = [folio for folio in Folio.objects.all().order_by('fecha_de_autorizacion')]
		context['folios_list'] = folios_list
		# Filtrar por usuario o empresa 

		return context


	# def get_form_kwargs(self):
		
		"""
		Genera un dropdown dinamico con las companias
		registrada por el usuario
		"""

	# 	user = self.request.user 

	# 	companias = Compania.objects.filter()

		# dropdown = tuple(tuple(compania.id, compania.name for compania in companias))

		





