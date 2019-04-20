"""
Facturador TIMG
@package factura.viewset

Router del api de Rest Framework
@copyright TIMG
@version 1.0
"""
from rest_framework import viewsets
from rest_framework.response import Response

class FacturaViewSet(viewsets.ViewSet):
  """
  Clase para la vista en rest de la factura
  @author Rodrigo Boet (rodrigoale.b at timg.cl)
  @copyright TIMG
  @date 15-04-19 (dd-mm-YY)
  @version 1.0
  """

  def create(self, request):
    return Response("hello")