"""!
Modelo que construye los modelos de datos de los usuarios

@author Ing. Leonel P. Hernandez M. (leonelphm at gmail.com)
@author Ing. Luis Barrios (nikeven at gmail.com)
@copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
@date 09-06-2017
@version 1.0.0
"""
from django.db import models


class TipoDocumento(models.Model):
    """!
    Clase que contiene el modelo de datos del Tipo de  Documento

    @author Ing. Leonel Paolo Hernandez Macchiarulo  (leonelphm at gmail.com)
    @author Ing. Luis Barrios (nikeven at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    @date 09-06-2017
    @version 1.0.0
    """
    abreviatura = models.CharField(max_length=4, verbose_name='Acrónimo')
    descripcion = models.TextField()

    class Meta:
        ordering = ('abreviatura',)
        verbose_name = 'Tipo Documento'
        verbose_name_plural = 'Tipos Documentos'

    def __str__(self):
        return self.abreviatura