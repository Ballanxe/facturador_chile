import OpenSSL.crypto
import codecs, dicttoxml, json, os, requests
from requests import Request, Session
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.http import FileResponse
from django.views.generic.edit import FormView
from django.shortcuts import (
    render, redirect
    )
from django.views.generic.base import TemplateView, View
from django.views.generic import ListView
from django.template.loader import render_to_string
from django_weasyprint import WeasyTemplateResponseMixin
from conectores.models import *
from conectores.forms import FormCompania
from conectores.models import *
from folios.models import Folio
from folios.exceptions import ElCafNoTieneMasTimbres, ElCAFSenEncuentraVencido
from utils.SIISdk import SII_SDK
from utils.utils import validarModelPorDoc
from .models import notaCredito
from .forms import *
from facturas.constants import NOMB_DOC, LIST_DOC

class SeleccionarEmpresaView(LoginRequiredMixin, TemplateView):
    template_name = 'seleccionar_empresa_NC.html'

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
        enviadas = self.request.GET.get('enviadas', None)
        empresa = int(request.POST.get('empresa'))
        if not empresa:
            return HttpResponseRedirect('/')
        empresa_obj = Compania.objects.get(pk=empresa)
        if empresa_obj and self.request.user == empresa_obj.owner:
            if enviadas == "1":
                return HttpResponseRedirect(reverse_lazy('notaCredito:lista-enviadas', kwargs={'pk':empresa}))
            else:
                return HttpResponseRedirect(reverse_lazy('notaCredito:lista_nota_credito', kwargs={'pk':empresa}))
        else:
            return HttpResponseRedirect('/')

class ListaNotaCreditoViews(LoginRequiredMixin, TemplateView):
    template_name = 'lista_NC.html'

    def dispatch(self, *args, **kwargs):

        compania = self.kwargs.get('pk')

        usuario = Conector.objects.filter(t_documento='33',empresa=compania).first()

        if not usuario:

            messages.info(self.request, "No posee conectores asociados a esta empresa")
            return HttpResponseRedirect(reverse_lazy('notaCredito:seleccionar-empresa'))

        return super().dispatch(*args, **kwargs)
            

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = requests.Session()
        compania = self.kwargs.get('pk')
        context['id_empresa'] = compania

        try:
            usuario = Conector.objects.filter(t_documento='33',empresa=compania).first()
        except Exception as e:

            print(e)

        payload = "{\"usr\":\"%s\",\"pwd\":\"%s\"\n}" % (usuario.usuario, usuario.password)

        headers = {'content-type': "application/json"}
        response = session.get(usuario.url_erp+'/api/method/login',data=payload,headers=headers)
        lista = session.get(usuario.url_erp+'/api/resource/Sales%20Invoice/?limit_page_length')
        erp_data = json.loads(lista.text)

        # Todas las facturas y boletas sin discriminacion 
        data = erp_data['data']

        # Consulta en la base de datos todos los numeros de facturas
        # cargadas por la empresa correspondiente para hacer una comparacion
        # con el ERP y eliminar las que ya se encuentran cargadas
        enviadas = [factura.numero_factura for factura in notaCredito.objects.filter(compania=compania).only('numero_factura')]
        # Elimina todas las boletas de la lista
        # y crea una nueva lista con todas las facturas 
        solo_facturas  = []
        for i , item in enumerate(data):

            if item['name'].startswith('NC'):

                solo_facturas.append(item['name'])
        # Verifica si la factura que vienen del ERP 
        # ya se encuentran cargadas en el sistema
        # y en ese caso las elimina de la lista
        solo_nuevas = []
        for i , item in enumerate(solo_facturas):
            if not item in enviadas:
                solo_nuevas.append(item)
        url=usuario.url_erp+'/api/resource/Sales%20Invoice/'
        context['detail']=[]
        for tmp in solo_nuevas:
            aux1=url+str(tmp)
            aux=session.get(aux1)
            context['detail'].append(json.loads(aux.text))
        session.close()
        return context

class DeatailInvoice(LoginRequiredMixin, TemplateView):
    template_name = 'detail_NC.html'

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
        url=usuario.url_erp+'/api/resource/Sales%20Invoice/'+str(kwargs['slug'])
        aux=session.get(url)
        session.close()
        aux=json.loads(aux.text)
        xml = dicttoxml.dicttoxml(aux)
        context['keys'] = list(aux['data'].keys())
        context['values'] = list(aux['data'].values())
        return context

class SendInvoice(LoginRequiredMixin, FormView):
    template_name = 'envio_sii_NC.html'
    form_class =FormNotaCredito

    def get_initial(self):
        initial = super().get_initial()
        session = requests.Session()
        url = self.kwargs['slug']
        compania = self.kwargs['pk']

        try:
            usuario = Conector.objects.filter(t_documento='33',empresa=compania).first()
        except Exception as e:
            print(e)
        payload = "{\"usr\":\"%s\",\"pwd\":\"%s\"\n}" % (usuario.usuario, usuario.password)
        headers = {'content-type': "application/json"}
        try:
            response = session.get(usuario.url_erp+'/api/method/login',data=payload,headers=headers)
        except Exception as e:
            messages.warning(self.request, "No se pudo establecer conexion con el ERP Next, se genera el siguiente error: "+str(e))
        url=usuario.url_erp+'/api/resource/Sales%20Invoice/'+url
        try:
            aux=session.get(url)
            session.close()
            aux=json.loads(aux.text)
            context={}
            context['factura'] = dict(zip(aux['data'].keys(), aux['data'].values()))
            context['factura']['sales_team'] = context['factura']['sales_team'][0]['sales_person']
            context['factura']['total_taxes_and_charges'] = round(abs(float(context['factura']['total_taxes_and_charges'])))
        except Exception as e:
            messages.warning(self.request, "No se pudo establecer conexion con el ERP Next, se genera el siguiente error: "+str(e))
        try:
            initial['status']= context['factura']['status_sii']
        except Exception as e:
            initial['status'] =""
        initial['numero_factura']=self.kwargs['slug']
        try:
            initial['senores']=context['factura']['customer_name']
        except Exception as e:
            initial['senores']=""
        try:
            initial['direccion']=context['factura']['customer_address']
        except Exception as e:
            initial['direccion']=""
        try:
            initial['transporte']=context['factura']['transporte']
        except Exception as e:
            initial['transporte']=""
        try:
            initial['despachar']=context['factura']['despachar_a']
        except Exception as e:
            initial['despachar']=""
        try:
            initial['observaciones']=context['factura']['observaciones']
        except Exception as e:
            initial['observaciones']=""
        try:
            initial['giro']=context['factura']['giro']
        except Exception as e:
            self.form_class.base_fields['giro'].initial=""
        # self.form_class.base_fields['condicion_venta'].initial=context['factura']['']
        # self.form_class.base_fields['vencimiento'].initial=context['factura']['']
        try:
            initial['vendedor']=context['factura']['sales_team']
        except Exception as e:
            initial['vendedor']=""
        try:
            initial['rut']=context['factura']['rut']
        except Exception as e:
            initial['rut']=""
        try:
            initial['fecha']=context['factura']['posting_date']
        except Exception as e:
            initial['fecha']=""
        # self.form_class.base_fields['guia'].initial=context['factura']['']
        # self.form_class.base_fields['orden_compra'].initial=context['factura']['']
        try:
            initial['nota_venta']=context['factura']['orden_de_venta']
        except Exception as e:
            initial['nota_venta']=""
        try:
            initial['productos']=context['factura']['items']
        except Exception as e:
            initial['productos']=""
        try:
            initial['monto_palabra']=context['factura']['in_words']
        except Exception as e:
            initial['monto_palabra']=""
        try:
            initial['neto']=context['factura']['net_total']
        except Exception as e:
            initial['neto']=""
        # self.form_class.base_fields['excento'].initial=context['factura']['']
        try:
            initial['iva']=context['factura']['total_taxes_and_charges']
        except Exception as e:
            initial['iva']=""
        try:
            initial['total']=context['factura']['rounded_total']
        except Exception as e:
            initial['total']=""
        return initial
    
    def get_success_url(self):

        id_ = self.kwargs.get('pk')

        return reverse_lazy('notaCredito:send-invoice', kwargs={'pk':id_,'slug':self.kwargs['slug']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = requests.Session()
        url = self.kwargs['slug']
        compania = self.kwargs['pk']

        try:
            usuario = Conector.objects.filter(pk=1).first()
        except Exception as e:
            print(e)
        payload = "{\"usr\":\"%s\",\"pwd\":\"%s\"\n}" % (usuario.usuario, usuario.password)
        headers = {'content-type': "application/json"}
        try:
            response = session.get(usuario.url_erp+'/api/method/login',data=payload,headers=headers)
        except Exception as e:
            messages.warning(self.request, "No se pudo establecer conexion con el ERP Next, se genera el siguiente error: "+str(e))
        url=usuario.url_erp+'/api/resource/Sales%20Invoice/'+url
        try:
            aux=session.get(url)
            session.close()
            aux=json.loads(aux.text)
            context['factura'] = dict(zip(aux['data'].keys(), aux['data'].values()))
        except Exception as e:
            messages.warning(self.request, "No se pudo establecer conexion con el ERP Next, se genera el siguiente error: "+str(e))
        try:
            record = Compania.objects.filter(pk=1).first()
            if record:
                form = FormCompania(instance=record)
            else:
                form = FormCompania()
            context['compania'] = form
        except Exception as e:
            raise e        
        return context

    def form_valid(self, form, **kwargs):
        compania_id = self.kwargs['pk']
        # pass_certificado = form.cleaned_data['pass_certificado']
        # if form.cleaned_data['status'] == 'En proceso':
        data = form.clean()
        print(data)
        try:
            compania = Compania.objects.get(pk=compania_id)
        except Compania.DoesNotExist:
            messages.error(self.request, "No ha seleccionado la compania")
            return super().form_invalid(form)
        assert compania, "compania no existe"
        pass_certificado = compania.pass_certificado
        data['productos']=eval(data['productos'])

        form = form.save(commit=False)
        try:
            folio = Folio.objects.filter(empresa=compania_id,is_active=True,vencido=False,tipo_de_documento=33).order_by('fecha_de_autorizacion').first()

            if not folio:
                raise Folio.DoesNotExist

        except Folio.DoesNotExist:  
            messages.error(self.request, "No posee folios para asignacion de timbre")
            return super().form_invalid(form)
        try:
            
            folio.verificar_vencimiento()
        except ElCAFSenEncuentraVencido:
            messages.error(self.request, "El CAF se encuentra vencido")
            return super().form_invalid(form)
        form.status = 'Aprobado'
        try:
            form.recibir_folio(folio)
        except (ElCafNoTieneMasTimbres, ValueError):
            messages.error(self.request, "Ya ha consumido todos sus timbres")
            return super().form_invalid(form)
        # Trae la cantidad de folios disponibles y genera una notificacion cuando quedan menos de 5
        # Si queda uno, cambia la estructura de la oracion a singular. 
        disponibles = folio.get_folios_disponibles()

        if disponibles == 1:
            messages.success(self.request, "Nota de crédito enviada exitosamente")
            messages.info(self.request, str('Queda ')+str(disponibles)+str('folio disponible'))
        elif disponibles < 50:
            messages.success(self.request, "Nota de crédito enviada exitosamente")
            messages.info(self.request, str('Quedan ')+str(disponibles)+str('folios disponibles'))
        else:
            messages.success(self.request, "Nota de crédito enviada exitosamente")
        form.compania = compania
        #form.save()

        try:
            response_dd = notaCredito._firmar_dd(data, folio, form)
            documento_firmado = notaCredito.firmar_documento(response_dd,data,folio, compania, form, pass_certificado)
            documento_final_firmado = notaCredito.firmar_etiqueta_set_dte(compania, folio, documento_firmado)
            caratula_firmada = notaCredito.generar_documento_final(compania,documento_final_firmado,pass_certificado)
            form.dte_xml = caratula_firmada
        except Exception as e:
            print(e)
            messages.error(self.request, "Ocurrió un error al firmar el documento")
            return super().form_valid(form)

        try:
            xml_dir = settings.MEDIA_ROOT +'notas_de_credito'+'/'+self.kwargs['slug']
            if(not os.path.isdir(xml_dir)):
                os.makedirs(xml_dir)
            f = open(xml_dir+'/'+self.kwargs['slug']+'.xml','w')
            f.write(caratula_firmada)
            f.close()
        except Exception as e:
            messages.error(self.request, 'Ocurrio el siguiente Error: '+str(e))
            return super().form_valid(form)

        send_sii = self.send_invoice_sii(compania,caratula_firmada,pass_certificado)
        if(not send_sii['estado']):
            messages.error(self.request, send_sii['msg'])
            return super().form_valid(form)
        else:
            form.track_id = send_sii['track_id']
            form.save()

        session = requests.Session()
        try:
            usuario = Conector.objects.filter(pk=1).first()
        except Exception as e:
            print(e)
        payload = "{\"usr\":\"%s\",\"pwd\":\"%s\"\n}" % (usuario.usuario, usuario.password)
        headers = {'content-type': "application/json"}
        response = session.get(usuario.url_erp+'/api/method/login',data=payload,headers=headers)
        url=usuario.url_erp+'/api/resource/Sales%20Invoice/'+self.kwargs['slug']
        aux=session.put(url,json={'status_sii':'Aprobado'})
        session.close()
        # else:
        #     msg = "La factura %s ya se encuentra almacenada en la base de datos del Faturador" % (self.kwargs['slug'])
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)

    def send_invoice_sii(self,compania,invoice, pass_certificado):
        """
        Método para enviar la factura al sii
        @param compania recibe el objeto compañia
        @param invoice recibe el xml de la factura
        @param pass_certificado recibe la contraseña del certificado
        @return dict con la respuesta
        """
        try:
            sii_sdk = SII_SDK()
            seed = sii_sdk.getSeed()
            try:
                sign = sii_sdk.signXml(seed, compania, pass_certificado)
                token = sii_sdk.getAuthToken(sign)
                if(token):
                    print(token)
                    try:
                        invoice_reponse = sii_sdk.sendInvoice(token,invoice,compania.rut,'60803000-K')
                        return {'estado':invoice_reponse['success'],'msg':invoice_reponse['message'],
                        'track_id':invoice_reponse['track_id']}
                    except Exception as e:
                        print(e)
                        return {'estado':False,'msg':'No se pudo enviar la factura'}    
                else:
                    return {'estado':False,'msg':'No se pudo obtener el token del sii'}
            except Exception as e:
                print(e)
                return {'estado':False,'msg':'Ocurrió un error al firmar el documento'}
            return {'estado':True}
        except Exception as e:
            print(e)
            return {'estado':False,'msg':'Ocurrió un error al comunicarse con el sii'}

class NotaCreditoEnviadasView(LoginRequiredMixin, ListView):
    template_name = 'NC_enviadas.html'


    def get_queryset(self):

        compania = self.kwargs.get('pk')
        return notaCredito.objects.filter(compania=compania).order_by('-created')

class ImprimirNC(LoginRequiredMixin, TemplateView,WeasyTemplateResponseMixin):
    """!
    Class para imprimir la factura en PDF

    @author Rodrigo Boet (rudmanmrrod at gmail.com)
    @date 21-03-2019
    @version 1.0.0
    """
    template_name = "pdf/factura.pdf.html"
    model = notaCredito

    def dispatch(self, request, *args, **kwargs):
        num_factura = self.kwargs['slug']
        compania = self.kwargs['pk']
        tipo_doc = self.kwargs['doc']
        if tipo_doc in LIST_DOC:
            self.model = validarModelPorDoc(tipo_doc) 
            try:
                factura = self.model.objects.select_related().get(numero_factura=num_factura, compania=compania)
                return super().dispatch(request, *args, **kwargs)
            except Exception as e:
                factura = self.model.objects.select_related().filter(numero_factura=num_factura, compania=compania)
                if len(factura) > 1:
                    messages.error(self.request, 'Existe mas de un registro con el mismo numero de factura: {0}'.format(num_factura))
                    return redirect(reverse_lazy('nota_credito:lista-enviadas', kwargs={'pk': compania}))
                else:
                    messages.error(self.request, "No se encuentra registrada esta factura: {0}".format(str(num_factura)))
                    return redirect(reverse_lazy('nota_credito:lista-enviadas', kwargs={'pk': compania}))
        else:
            messages.error(self.request, "No existe este tipo de documento: {0}".format(str(tipo_doc)))
            return redirect(reverse_lazy('nota_credito:lista-enviadas', kwargs={'pk': compania}))

    def get_context_data(self, *args, **kwargs):
        """!
        Method to handle data on get

        @date 21-03-2019
        @return Returns dict with data
        """
        context = super().get_context_data(*args, **kwargs)
        num_factura = self.kwargs['slug']
        compania = self.kwargs['pk']
        tipo_doc = self.kwargs['doc']
        
        context['factura'] = self.model.objects.select_related().get(numero_factura=num_factura, compania=compania)
        context['nombre_documento'] = NOMB_DOC[tipo_doc]
        etiqueta=self.kwargs['slug'].replace('º','')
        context['etiqueta'] = etiqueta
        prod = context['factura'].productos.replace('\'{','{').replace('}\'','}').replace('\'',"\"")
        productos = json.loads(prod)
        context['productos'] = productos
        ruta = settings.STATIC_URL +'notas_de_credito'+'/'+etiqueta+'/timbre.jpg'
        context['ruta']=ruta
        return context

class VerEstadoNC(LoginRequiredMixin, TemplateView):
    """!
    Clase para ver el estado de envio de una factura

    @author Rodrigo Boet (rudmanmrrod at gmail.com)
    @date 04-04-2019
    @version 1.0.0
    """
    template_name = "estado_factura.html"
    model = notaCredito

    def get_context_data(self, *args, **kwargs):
        """!
        Method to handle data on get

        @date 04-04-2019
        @return Returns dict with data
        """
        context = super().get_context_data(*args, **kwargs)
        num_factura = self.kwargs['slug']
        compania = self.kwargs['pk']

        factura = self.model.objects.get(numero_factura=num_factura, compania=compania)
        context['factura'] = factura
        
        estado = self.get_invoice_status(factura,factura.compania,)

        if(not estado['estado']):
            messages.error(self.request, estado['msg'])
        else:
            context['estado'] = estado['status']
            context['glosa'] = estado['glosa']

        return context

    def get_invoice_status(self,factura,compania):
        """
        Método para enviar la factura al sii
        @param factura recibe el objeto de la factura
        @param compania recibe el objeto compañia
        @return dict con la respuesta
        """
        try:
            sii_sdk = SII_SDK()
            seed = sii_sdk.getSeed()
            try:
                sign = sii_sdk.signXml(seed, compania, compania.pass_certificado)
                token = sii_sdk.getAuthToken(sign)
                if(token):
                    print(token)
                    estado = sii_sdk.checkDTEstatus(compania.rut,factura.track_id,token)
                    return {'estado':True,'status':estado['estado'],'glosa':estado['glosa']} 
                else:
                    return {'estado':False,'msg':'No se pudo obtener el token del sii'}
            except Exception as e:
                print(e)
                return {'estado':False,'msg':'Ocurrió un error al firmar el documento'}
            return {'estado':True}
        except Exception as e:
            print(e)
            return {'estado':False,'msg':'Ocurrió un error al comunicarse con el sii'}
