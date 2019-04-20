import datetime

from django.views.generic import CreateView
from django.contrib import messages
from django.urls import reverse_lazy

from lxml import etree
from bs4 import BeautifulSoup

from .forms import FolioCreateForm
from conectores.models import Compania
from .models import Folio

# Create your views here.


class FolioCreateView(CreateView):
	template_name = 'folio-create-view.html'
	form_class = FolioCreateForm
	success_url = reverse_lazy('folios:registrar')

	def form_valid(self, form):

		instance = form.save(commit=False)



		try:


			xml = instance.caf.read()

			# soup = BeautifulSoup(xml, 'xml')

			# print(soup.CAF)
			# print(type(soup.CAF))
			# print(str(soup.CAF).strip())



			root = etree.fromstring(xml)
			rut = root.xpath('//AUTORIZACION/CAF/DA/RE/text()')[0]
			tipo_de_documento = root.xpath('//AUTORIZACION/CAF/DA/TD/text()')[0]
			rango_desde = root.xpath('//AUTORIZACION/CAF/DA/RNG/D/text()')[0]
			rango_hasta = root.xpath('//AUTORIZACION/CAF/DA/RNG/H/text()')[0]
			folios_disponibles = int(rango_hasta) - int(rango_desde)
			fecha_de_autorizacion = root.xpath('//AUTORIZACION/CAF/DA/FA/text()')[0]
			pk_modulo = root.xpath('//AUTORIZACION/CAF/DA/RSAPK/M/text()')[0]
			pk_exponente = root.xpath('//AUTORIZACION/CAF/DA/RSAPK/E/text()')[0]

		except:

			messages.error(self.request, 'Algo anda mal con el CAF')
			return super().form_invalid(form)


		date_list = fecha_de_autorizacion.split('-')
		fecha_de_autorizacion = datetime.datetime(int(date_list[0]),int(date_list[1]),int(date_list[2]))

		instance.rut = rut
		instance.tipo_de_documento = tipo_de_documento
		instance.rango_desde = rango_desde
		instance.rango_hasta = rango_hasta
		instance.folios_disponibles = folios_disponibles
		instance.fecha_de_autorizacion = fecha_de_autorizacion
		instance.pk_modulo = pk_modulo
		instance.pk_exponente = pk_exponente

		instance.save()
		messages.success(self.request, 'Archivo CAF añadido exitosamente')

		return super().form_valid(form)

	def form_invalid(self, form):

		messages.error(self.request, 'No se pudo agregar el archivo')

		return super().form_invalid(form)

	def get_context_data(self, *args, **kwargs):

		context = super().get_context_data(*args, **kwargs)

		# Filtrar por usuario o empresa 
		folios_list = [folio for folio in Folio.objects.all()]

		context['folios_list'] = folios_list

		return context


	# def get_form_kwargs(self):
		
		"""
		Genera un dropdown dinamico con las companias
		registrada por el usuario
		"""

	# 	user = self.request.user 

	# 	companias = Compania.objects.filter()

		# dropdown = tuple(tuple(compania.id, compania.name for compania in companias))

		





