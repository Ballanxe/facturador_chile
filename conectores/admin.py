from django.contrib import admin

# Register your models here.
from .models import Compania, Conector

admin.site.register(Compania)
admin.site.register(Conector)