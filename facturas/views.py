from django.contrib import messages
from django.views.generic.edit import FormView
from django.shortcuts import render
from django.views.generic.base import TemplateView
import mysql.connector
import requests
from requests import Request, Session
import json

class ListaFacturasViews(TemplateView):
    template_name = 'lista_facturas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = requests.Session()
        payload = "{\"usr\":\"luis.be@timg.cl\",\"pwd\":\"Yayu115.\"\n}"
        headers = {'content-type': "application/json"}
        response = session.get('http://erp.timg.cl/api/method/login',data=payload,headers=headers)
        lista = session.get('http://erp.timg.cl/api/resource/Sales%20Invoice/')
        context['invoices'] = json.loads(lista.text)
        url='http://erp.timg.cl/api/resource/Sales%20Invoice/'
        context['detail']=[]
        for tmp in  context['invoices']['data']:
            aux1=url+str(tmp['name'])
            aux=session.get(aux1)
            context['detail'].append(json.loads(aux.text))
        return context

class DeatailInvoice(TemplateView):
    template_name = 'detail_invoice.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = requests.Session()
        payload = "{\"usr\":\"luis.be@timg.cl\",\"pwd\":\"Yayu115.\"\n}"
        headers = {'content-type': "application/json"}
        response = session.get('http://erp.timg.cl/api/method/login',data=payload,headers=headers)
        url='http://erp.timg.cl/api/resource/Sales%20Invoice/'+str(kwargs['slug'])
        aux=session.get(url)
        aux=json.loads(aux.text)
        context['keys'] = list(aux['data'].keys())
        context['values'] = list(aux['data'].values())
        return context
