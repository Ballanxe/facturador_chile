from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic.base import TemplateView
from .views import *

app_name = 'facturas'
urlpatterns = [
    re_path(r'lista-facturas/(?P<pk>\d+)', ListaFacturasViews.as_view(), name='lista_facturas'),
    re_path(r'^lista-facturas/empresa/$', SeleccionarEmpresaView.as_view(),name='seleccionar-empresa'),
    re_path(r'^factura/(?P<slug>[a-zA-Z0-9º-]+)/$', DeatailInvoice.as_view(),name='detail-invoice'),
    re_path(r'^facturas-enviadas/(?P<pk>\d+)/$', FacturasEnviadasView.as_view(),name='lista-enviadas'),
    path('enviar-factura/<int:pk>/<str:slug>/', SendInvoice.as_view(),name='send-invoice'),
    path('imprimir-factura/<int:pk>/<str:slug>/<str:doc>/', ImprimirFactura.as_view(),name="imprimir_factura"),
    path('estado-factura/<int:pk>/<str:slug>/',VerEstadoFactura.as_view(),name="ver_estado"),
]



