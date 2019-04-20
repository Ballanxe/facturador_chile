"""
Facturador TIMG
@package config.router

Router del api de Rest Framework
@copyright TIMG
@version 1.0
"""
from rest_framework import routers
from facturas.viewset import *

router = routers.DefaultRouter()
router.register(r'facturas', FacturaViewSet, basename='facturas')