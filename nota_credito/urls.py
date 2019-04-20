from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic.base import TemplateView
from .views import *

app_name = 'nota_credito'
urlpatterns = [
    re_path(r'lista-nota-credito/(?P<pk>\d+)', ListaNotaCreditoViews.as_view(), name='lista_nota_credito'),
    re_path(r'^lista-nota-credito/empresa/$', SeleccionarEmpresaView.as_view(),name='seleccionar-empresa'),
    re_path(r'^nota-credito/(?P<slug>[a-zA-Z0-9º-]+)/$', DeatailInvoice.as_view(),name='detail-invoice'),
    re_path(r'^NC-enviadas/(?P<pk>\d+)/$', NotaCreditoEnviadasView.as_view(),name='lista-enviadas'),
    path('enviar-nota-credito/<int:pk>/<str:slug>/', SendInvoice.as_view(),name='send-invoice'),
    path('imprimir-nc/<int:pk>/<str:slug>/<str:doc>/', ImprimirNC.as_view(),name="imprimir_nc"),
    path('estado-nc/<int:pk>/<str:slug>/',VerEstadoNC.as_view(),name="ver_estado_nc"),
]



