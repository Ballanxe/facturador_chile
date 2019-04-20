# -*- encoding: utf-8 -*-
"""!
Modulo donde se construyen los ajax´s llamados desde los templates

@author Ing. Leonel Paolo Hernandez Macchiarulo  (leonelphm at gmail.com)
@author Ing. Luis Barrios (nikeven at gmail.com)
@copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
@date 09-01-2017
@version 1.0.0
"""
from django.conf import settings
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.contrib.auth.models import (
    User
    )
from utils.views import (
    LoginRequeridoPerAuth
)

class ListUsersAjaxView(LoginRequeridoPerAuth, BaseDatatableView):
    """!
    Prepara la data para mostrar en el datatable

    @author Ing. Leonel P. Hernandez M. (leonelphm at gmail.com)
    @author Ing. Luis Barrios (nikeven at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    @date 09-01-2017
    @version 1.0.0
    """
    # The model we're going to show
    model = User
    # define the columns that will be returned
    columns = ['pk', 'first_name', 'last_name', 'username', 'email',
                          'date_joined', 'last_joined', 'is_active', 'groups']
    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['pk', 'username', 'first_name', 'last_name', 'email',
                                        'date_joined', 'last_login', 'is_active', 'groups',
                                        'acciones']
    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500
    group_required = [u"Super Admin"]

    def __init__(self):
        super(ListUsersAjaxView, self).__init__()

    def get_initial_queryset(self):
        """!
        Consulta el modelo User

        @return: Objeto de la consulta
        """
        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        # You should not filter data returned here by any filter values entered by user. This is because
        # we need some base queryset to count total number of records.
        return self.model.objects.all()

    def prepare_results(self, qs):
        """!
        Prepara la data para mostrar en el datatable
        @return: Objeto json con los datos de los usuarios
        """
        # prepare list with output column data
        json_data = []
        for item in qs:
            user = "<a data-toggle='modal' data-target='#myModal' \
                    class='btn btn-block btn-info btn-xs fa fa-edit' \
                    onclick='modal_user(%s)'>%s</a>\
                    " % (str(item.pk), str(item.username))
            if item.last_login:
                last_login = item.last_login.strftime("%Y-%m-%d %H:%M:%S")
            else:
                last_login = "No ha ingresado"
            if item.is_active:
                activo = "Activo"
                activar = "<input type='checkbox' id='user-" + str(item.pk) + "' value='" + str(item.pk) + "' name='inactivar' onclick='$(\"#forma_activar\").submit();'/>\
                            <label for='user-" + str(item.pk) + "'>\
                                <img  src='" + settings.MEDIA_URL +\
                                "imagenes/inactivar.png' id='inactivo'\
                                title='Inactivar Usuario' \
                                />\
                            </label>"

            else:
                activo = "Inactivo"
                activar = "<input type='checkbox' id='user-" + str(item.pk) + "' value='" + str(item.pk) + "' name='activar' onclick='$(\"#forma_activar\").submit();'/>\
                            <label for='user-" + str(item.pk) + "'>\
                                <img  src='" + settings.MEDIA_URL + \
                                "imagenes/activar.png' id='activo' \
                                title='Activar Usuario'/>\
                            </label>"
            try:
                grupos = item.groups.all()
                grupo = []
                if len(grupos) > 1:
                    for g in grupos:
                        grupo += str(g),
                else:
                    grupo = str(item.groups.get())
            except:
                grupo = "No pertenece a un grupo"
            json_data.append([
                user,
                "{0} {1}".format(str(item.first_name), str(item.last_name)),
                item.email,
                item.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
                last_login,
                activo,
                grupo,
                activar
            ])
            grupo = ""
        return json_data
