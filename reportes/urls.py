from django.urls import path, re_path

from .views import (
	ReportesCreateListView,
	SeleccionarEmpresaView,
	ReporteDetailView,
	ReportesDeleteView,
)


app_name = 'reportes'
urlpatterns = [
	re_path(r'^reportes/detalle/(?P<pk>\d+)$', ReporteDetailView.as_view(), name='detalle'),
    re_path(r'^reportes/(?P<pk>\d+)/crear$', ReportesCreateListView.as_view(), name='crear'),
    re_path(r'^reportes/(?P<pk>\d+)/delete/(?P<reporte_pk>\d+)$', ReportesDeleteView.as_view(), name='borrar'),
    path('reportes/empresa/', SeleccionarEmpresaView.as_view(),name='seleccionar-empresa'),

]