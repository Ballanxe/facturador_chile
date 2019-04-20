from django.contrib import admin

# Register your models here.

from .models import Certificado


class CertificadoAdmin(admin.ModelAdmin):
	readonly_fields = ["private_key", "public_key", "certificado"]

admin.site.register(Certificado, CertificadoAdmin)
