from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic.base import TemplateView
from .views import *

app_name = 'guiaDespacho'
urlpatterns = [
    re_path(r'lista-guias/(?P<pk>\d+)', ListaGuiasViews.as_view(), name='lista_guias'),
    re_path(r'^lista-guias/empresa/$', SeleccionarEmpresaView.as_view(),name='seleccionar-empresa'),
    path('guia/<str:slug>/',DetailGuia.as_view(),name='detail-guia'),
    re_path(r'^guia/(?P<pk>\d+)/enviadas/$', GuiasEnviadasView.as_view(),name='lista-guias-enviadas'),
    # re_path(r'^enviar-boleta/(?P<pk>\d+)/(?P<slug>[a-zA-Z0-9º-]+)/$', SendInvoice.as_view(),name='send-invoice'),
]



