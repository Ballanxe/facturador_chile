from django.contrib import messages
from django.views.generic.base import TemplateView
from django.views.generic import ListView
import requests
from requests import Request, Session
import dicttoxml
import json
from django.http import HttpResponseRedirect
from conectores.models import *
import codecs
from conectores.models import *
from django.urls import reverse_lazy
from django.conf import settings
from .models import *

class SeleccionarEmpresaView(TemplateView):
    template_name = 'seleccionar_empresa.html'

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
            if enviadas == "1":
                return HttpResponseRedirect(reverse_lazy('guiaDespacho:lista-guias-enviadas', kwargs={'pk':empresa}))
            else:
                return HttpResponseRedirect(reverse_lazy('guiaDespacho:lista_guias', kwargs={'pk':empresa}))
        else:
            return HttpResponseRedirect('/')

class ListaGuiasViews(TemplateView):
    template_name = 'lista_guias.html'

    def dispatch(self, *args, **kwargs):
        compania = self.kwargs.get('pk')
        usuario = Conector.objects.filter(t_documento='33',empresa=compania).first()
        if not usuario:
            messages.info(self.request, "No posee conectores asociados a esta empresa")
            return HttpResponseRedirect(reverse_lazy('guisDespacho:seleccionar-empresa'))
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = requests.Session()
        compania = self.kwargs.get('pk')
        context['id_empresa'] = compania
        try:
            usuario = Conector.objects.filter(t_documento='33',empresa=compania).first()
        except Exception as e:
            messages.info(self.request, "No posee conectores asociados a esta empresa")
            return HttpResponseRedirect(reverse_lazy('guisDespacho:seleccionar-empresa'))
        payload = "{\"usr\":\"%s\",\"pwd\":\"%s\"\n}" % (usuario.usuario, usuario.password)
        headers = {'content-type': "application/json"}
        response = session.get(usuario.url_erp+'/api/method/login',data=payload,headers=headers)
        lista = session.get(usuario.url_erp+'/api/resource/Delivery%20Note/')
        erp_data = json.loads(lista.text)
        # Todas las facturas y boletas sin discriminacion 
        data = erp_data['data']
        # Consulta en la base de datos todos los numeros de facturas
        # cargadas por la empresa correspondiente para hacer una comparacion
        # con el ERP y eliminar las que ya se encuentran cargadas
        enviadas = [factura.numero_factura for factura in guiaDespacho.objects.filter(compania=compania).only('numero_factura')]
        # Elimina todas las boletas de la lista
        # y crea una nueva lista con todas las facturas 
        solo_facturas  = []
        for i , item in enumerate(data):
            solo_facturas.append(item['name'])
        # Verifica si la factura que vienen del ERP 
        # ya se encuentran cargadas en el sistema
        # y en ese caso las elimina de la lista
        solo_nuevas = []
        for i , item in enumerate(solo_facturas):
            if not item in enviadas:
                solo_nuevas.append(item)
        url=usuario.url_erp+'/api/resource/Delivery%20Note/'
        context['detail']=[]
        for tmp in solo_nuevas:
            aux1=url+str(tmp)
            aux=session.get(aux1)
            context['detail'].append(json.loads(aux.text))
        session.close()
        return context

class DetailGuia(TemplateView):
    template_name = 'detail_guia.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = requests.Session()
        try:
            usuario = Conector.objects.filter(pk=1).first()
        except Exception as e:
            print(e)
        payload = "{\"usr\":\"%s\",\"pwd\":\"%s\"\n}" % (usuario.usuario, usuario.password)
        headers = {'content-type': "application/json"}
        response = session.get(usuario.url_erp+'/api/method/login',data=payload,headers=headers)
        url=usuario.url_erp+'/api/resource/Delivery%20Note/'+str(kwargs['slug'])
        aux=session.get(url)
        session.close()
        aux=json.loads(aux.text)
        xml = dicttoxml.dicttoxml(aux)
        context['keys'] = list(aux['data'].keys())
        context['values'] = list(aux['data'].values())
        return context

class GuiasEnviadasView(ListView):
    template_name = 'guias_enviadas.html'
    def get_queryset(self):
        compania = self.kwargs.get('pk')
        return guiaDespacho.objects.filter(compania=compania).order_by('-created')