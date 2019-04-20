from django.urls import path
from .views import *

app_name = 'conectores'
urlpatterns = [
    path('registrar-conector/', ConectorViews.as_view(), name='registrar_conector'),
    path('registrar-compania/', CompaniaViews.as_view(), name='registrar_compania'),
    path('registrar_compania/update/<pk>/',CompaniaUpdate.as_view(), name='update_compania'),
    path('registrar_compania/delete/<pk>/',CompaniaDelete.as_view(), name='delete_compania'),

]