from django.contrib import admin

# Register your models here.
from .models import Intercambio, DteIntercambio

admin.site.register(Intercambio)
admin.site.register(DteIntercambio)