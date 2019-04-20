"""UserManager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf.urls.static import static
from .router import router

from users.forms import SetPasswordForm
from users.views import ResetPassConfirm, ResetPassSuccess

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^sources/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
    path(
        'user/password/reset/<uidb64>/<token>/',
        ResetPassConfirm.as_view(),
        name='password_reset_confirm',
    ),
    path(
        'user/password/done/',
        ResetPassSuccess.as_view(),
        name='pass_done',
    ),
    path('', include('utils.urls', namespace="utils")),
    path('', include('users.urls', namespace="users")),
    path('', include('conectores.urls', namespace="conectores")),
    path('', include('facturas.urls', namespace="facturas")),
    path('', include('folios.urls', namespace="folios")),
    path('', include('boletas.urls',namespace="boletas")),
    path('', include('guia_despacho.urls',namespace="guiaDespacho")),
    path('', include('nota_credito.urls',namespace="notaCredito")),
    path('', include('nota_debito.urls',namespace="notaDebito")),
    path('', include('reportes.urls',namespace="reportes")),
    path('', include('intercambios.urls',namespace="intercambios")),
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)