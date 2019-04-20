"""!
Modelo que construye los modelos de datos de los usuarios

@author Ing. Leonel P. Hernandez M. (leonelphm at gmail.com)
@author Ing. Luis Barrios (nikeven at gmail.com)
@copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
@date 18-01-2017
@version 1.0.0
"""
from django.db import models
from django.contrib.auth.models import (
    Group, User
    )

from utils.models import (
    TipoDocumento
    )

"""
Se agrega un campo de descripcion al modelo group para describir el grupo de usuarios
"""
Group.add_to_class('descripcion', models.TextField(blank=True))


class UserProfile(models.Model):
    """!
    Clase que construye el modelo de datos para el perfil de usuario

    @author Ing. Leonel P. Hernandez M. (leonelphm at gmail.com)
    @author Ing. Luis Barrios (nikeven at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    @date 18-01-2017
    @version 1.0.0
    """
    fk_user = models.OneToOneField(User, on_delete=models.CASCADE)
    fk_tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE)
    id_perfil = models.PositiveIntegerField(verbose_name='Documento de identidad')

    class Meta:
        """!
        Clase que construye los meta datos del modelo

        @author Ing. Leonel P. Hernandez M. (leonelphm at gmail.com)
        @author Ing. Luis Barrios (nikeven at gmail.com)
        @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
        @date 18-01-2017
        @version 1.0.0
        """
        ordering = ('fk_user',)
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuarios'
        unique_together = (("fk_tipo_documento", "id_perfil"),)
        db_table = 'users_perfil'

    def __str__(self):
        return self.fk_user.username


class TwoFactToken(models.Model):
    """!
    Class for store Two Fact Token from user
    @author Rodrigo Boet (rudmanmrrod at gmail.com)
    @author Ing. Luis Barrios (nikeven at gmail.com)
    @date 16-04-2017
    @version 1.0.0
    """
    # Relation to user model
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Field to store Token
    token = models.CharField(max_length=128)

    # Field to store serial id
    serial = models.PositiveIntegerField()

