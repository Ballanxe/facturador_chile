from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic.base import TemplateView
from .views import *

app_name = 'guia_despacho'
urlpatterns = [
    re_path(r'lista-guias/(?P<pk>\d+)', ListaGuiasViews.as_view(), name='lista_guias'),
    re_path(r'^lista-guias/empresa/$', SeleccionarEmpresaView.as_view(),name='seleccionar-empresa'),
    path('guia/<str:slug>/',DetailGuia.as_view(),name='detail-guia'),
    re_path(r'^guias-enviadas/(?P<pk>\d+)/$', GuiasEnviadasView.as_view(),name='lista-guias-enviadas'),
    path('enviar-guia/<int:pk>/<str:slug>/', SendInvoice.as_view(),name='send-invoice'),
    path('imprimir-guia/<int:pk>/<str:slug>/<str:doc>/', ImprimirGuia.as_view(),name="imprimir_guia"),
    path('estado-guia/<int:pk>/<str:slug>/',VerEstadoGuia.as_view(),name="ver_estado_guia"),
]



