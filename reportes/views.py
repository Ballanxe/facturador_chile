import datetime

from django.shortcuts import render
from django.views.generic import CreateView, DetailView, TemplateView, RedirectView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.template.loader import render_to_string
# from django.views.generic.edit import DeleteView
from .forms import ReporteCreateForm
from facturas.models import Factura
from nota_credito.models import notaCredito
from nota_debito.models import notaDebito
from boletas.models import Boleta
from conectores.models import Compania
from .models import Reporte



class SeleccionarEmpresaView(TemplateView):
    template_name = 'reportes_seleccionar_empresa.html'

    def get_context_data(self, *args, **kwargs): 

        context = super().get_context_data(*args, **kwargs)
        context['empresas'] = Compania.objects.filter(owner=self.request.user)
        if Compania.objects.filter(owner=self.request.user).exists():
            context['tiene_empresa'] = True
        else:
            messages.info(self.request, "Registre una empresa para continuar")
            context['tiene_empresa'] = False
        return context

    def post(self, request):

        enviadas = self.request.POST.get('enviadas', None)
        empresa = int(request.POST.get('empresa'))
        if not empresa:
            return HttpResponseRedirect('/')
        empresa_obj = Compania.objects.get(pk=empresa)
        if empresa_obj and self.request.user == empresa_obj.owner:

            return HttpResponseRedirect(reverse_lazy('reportes:crear', kwargs={'pk':empresa}))
        else:
            return HttpResponseRedirect('/')

class ReportesCreateListView(CreateView):


	template_name = "reporte_create_list.html"
	form_class = ReporteCreateForm
	get_success_url = reverse_lazy("reportes:crear")
	def form_valid(self, form):
		"""
		
		"""
		context = super().get_context_data()
		instance = form.save(commit=False)
		compania = get_object_or_404(Compania, pk=self.kwargs.get('pk'))
		instance.compania = compania
		fecha_de_inicio = instance.fecha_de_inicio
		fecha_de_culminacion = instance.fecha_de_culminacion
		tipo_de_operacion = instance.tipo_de_operacion
		report_context = {
			'compania': compania,
			'reporte': instance,
			'periodo_tributario': fecha_de_inicio.strftime("%Y-%m"),
			'resumen_periodos':[],
			'detalles':[]
		}

		if tipo_de_operacion == "VENTAS":

			facturas_queryset_ = [
				factura 
				for factura in Factura.objects.filter(
					compania=compania, 
					created__gte=fecha_de_inicio, 
					created__lte=fecha_de_culminacion
				)
			]
			nota_credito_queryset = [
				nota_credito
				for nota_credito in notaCredito.objects.filter(
					compania=compania,
					created__gte=fecha_de_inicio,
					created__lte=fecha_de_culminacion
				)
			]
			nota_debito_queryset = [
				nota_debito
				for nota_debito in notaDebito.objects.filter(
					compania=compania,
					created__gte=fecha_de_inicio,
					created__lte=fecha_de_culminacion
				)
			]
			facturas_data = self.generar_resumen_periodos(facturas_queryset_)
			nota_credito_data = self.generar_resumen_periodos(nota_credito_queryset)
			nota_debito_data = self.generar_resumen_periodos(nota_debito_queryset)

			if facturas_data:
				report_context['resumen_periodos'].append(
					facturas_data)
			if nota_credito_data:
				report_context['resumen_periodos'].append(
					nota_credito_data)


			report_context['detalles'].extend(facturas_queryset_+nota_credito_queryset+nota_debito_queryset)
			print(report_context['detalles'])
		elif tipo_de_operacion == "COMPRAS":

			messages.info(self.request, "No posee documentos de intercambio")
			return HttpResponseRedirect(reverse_lazy('reportes:crear', kwargs={'pk': compania.pk}))



		try: 
			Reporte.check_reporte_len(report_context['detalles'])
		except Exception as e:

			messages.error(self.request, e)
			return super().form_invalid(form)

		caratula = render_to_string('xml_templates/caratula_.xml', report_context)
		report_context['caratula'] = caratula
		envio_libro = render_to_string('xml_templates/envioLibro_.xml', report_context)
		instance.xml_reporte = envio_libro

		print(envio_libro)

		instance.save()
		messages.info(self.request, "Reporte creado exitosamente")
		return HttpResponseRedirect(reverse_lazy('reportes:crear', kwargs={'pk': compania.pk}))

	def get_context_data(self, *args, **kwargs):

		context = super().get_context_data(*args, **kwargs)
		compania = get_object_or_404(Compania, pk=self.kwargs.get('pk'))
		context['lista_de_reportes'] = Reporte.objects.filter(compania=compania).reverse()
		context['compania'] = compania	
		return context

	def generar_resumen_periodos(self, queryset):

		if len(queryset) == 0:

			return 

		tot_mnt_exe=0
		tot_mnt_neto=0
		tot_op_iva_rec=0
		tot_mnt_iva=0
		tot_mnt_total=0

		for item in queryset: 

			if item.excento:
				tot_mnt_exe += float(item.excento)
			if item.neto:
				tot_mnt_neto += float(item.neto)
			if item.total:
				tot_mnt_total += float(item.total)


		data = dict(
			tpo_doc=queryset[0].TIPO_DE_DOCUMENTO,
			tot_doc=len(queryset),
			tot_mnt_exe=int(tot_mnt_exe),
			tot_mnt_neto=int(tot_mnt_neto),
			tot_op_iva_rec=int(tot_op_iva_rec),
			tot_mnt_iva=int(tot_mnt_iva),
			tot_mnt_total=int(tot_mnt_total)
		)

		return data

	# def generar_detalles(self, **kwargs): 

class ReporteDetailView(DetailView):


	template_name="reportes_detail.html"

	def get_context_data(self, *args, **kwargs):

		context = super().get_context_data(*args, **kwargs)
		reporte = self.get_object()
		print(reporte)
		context['facturas_del_reporte'] = Factura.objects.filter(
			created__gte=reporte.fecha_de_inicio, 
			created__lte=reporte.fecha_de_culminacion
			)
		print(context['facturas_del_reporte'])

		return context

	def get_object(self):

		return get_object_or_404(Reporte, pk=self.kwargs.get('pk'))



class ReportesDeleteView(LoginRequiredMixin,DeleteView):


	template_name="reportes_delete.html"
	# model = Reporte
	# success_url = reverse_lazy('reportes:crear', kwargs={'pk':compania_pk})

	def get_object(self):

		user = self.request.user
		compania_pk = compania_pk = self.kwargs.get("pk")
		compania = get_object_or_404(Compania, owner=user)
		reporte_pk = self.kwargs.get("reporte_pk")
		reporte = get_object_or_404(Reporte, pk=reporte_pk)


		return reporte

	def delete(self, request, *args, **kwargs):

	    self.object = self.get_object()
	    success_url = self.get_success_url()
	    self.object.delete()
	    messages.success(self.request, "Reporte borrado exitosamente")
	    return HttpResponseRedirect(success_url)


	def get_success_url(self):

		compania_pk = self.kwargs.get("pk")

		return reverse_lazy('reportes:crear', kwargs={'pk':compania_pk})

class EnviarReporteRedirectView(LoginRequiredMixin,RedirectView):


	def get(self, *args, **kwargs):

		reporte = get_object_or_404(Reporte, pk=self.kwargs.get('pk'))
		compania = get_object_or_404(Compania, pk=self.kwargs.get('compania_pk'))


		documentos_del_reporte = Factura.objects.filter(created__gte=reporte.fecha_de_inicio, created__lte=reporte.fecha_de_culminacion)

		context = {
			'documentos_del_reporte': documentos_del_reporte,
			'compania': compania
		}

		signature_tag = render_to_string('snippets/signature.xml', {'signature':firma_electronica})

		return context


