from django.urls import path, re_path
from .views import (
	IntercambiosListView, 
	RefrescarBandejaRedirectView,
	SeleccionarEmpresaIntercambioView,
	IntercambiosDetailView
)

app_name = 'intercambios'
urlpatterns = [
    # re_path(r'^invoice/(?P<pk>\d+)/enviadas/$', FacturasEnviadasView.as_view(),name='lista-enviadas'),
    re_path(r'^intercambio/(?P<pk>\d+)/lista', IntercambiosListView.as_view(),name='lista'),
    re_path(r'^intercambio/(?P<pk>\d+)/(?P<inter_pk>\d+)', IntercambiosDetailView.as_view(),name='detalle'),
    re_path(r'^intercambio/(?P<pk>\d+)/actualizar', RefrescarBandejaRedirectView.as_view(),name='actualizar'),
    path('intercambio/empresa/', SeleccionarEmpresaIntercambioView.as_view(),name='empresa'),
]
