from django.urls import path
from .views import *

app_name = 'utils'
urlpatterns = [
    path('inicio/', StartView.as_view(), name='inicio'),
]
