from django.urls import path

from .views import FolioCreateView


app_name = 'folios'
urlpatterns = [
    path('registrar-folio/', FolioCreateView.as_view(), name='registrar'),

]