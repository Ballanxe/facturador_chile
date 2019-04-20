"""!
Modulo Forms  que construye los formularios para los templates  de la plataforma

@author Ing. Leonel P. Hernandez M. (leonelphm at gmail.com)
@author Ing. Luis Barrios (nikeven at gmail.com)
@copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
@date 09-06-2017
@version 1.0.0
"""
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
    UserCreationForm, PasswordResetForm,
    SetPasswordForm
    )
from django.forms.fields import (
    CharField, BooleanField
)
from django.forms.widgets import (
    PasswordInput, CheckboxInput
)

from .models import UserProfile


class FormularioLogin(forms.Form):
    """!
    Clase que permite crear el formulario de ingreso a la aplicación

    @author Ing. Leonel P. Hernandez M. (leonelphm at gmail.com)
    @author Ing. Luis Barrios (nikeven at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    @date 09-01-2017
    @version 1.0.0
    """
    contrasena = CharField()
    usuario = CharField()
    remember_me = BooleanField()

    class Meta:
        fields = ('usuario', 'contrasena', 'remember_me')

    def __init__(self, *args, **kwargs):
        super(FormularioLogin, self).__init__(*args, **kwargs)
        self.fields['contrasena'].widget = PasswordInput()
        self.fields['contrasena'].widget.attrs.update({'class': 'form-control',
        'placeholder': 'Contraseña'})
        self.fields['usuario'].widget.attrs.update({'class': 'form-control',
        'placeholder': 'Username o Email'})
        self.fields['remember_me'].label = "Recordar"
        self.fields['remember_me'].widget = CheckboxInput()
        self.fields['remember_me'].required = False


class PasswordResetForm(PasswordResetForm):
    """!
    Clase que permite sobrescribir el formulario para resetear la contraseña

    @author Ing. Leonel P. Hernandez M. (leonelphm at gmail.com)
    @author Ing. Luis Barrios (nikeven at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    @date 09-01-2017
    @version 1.0.0
    """

    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control',
                                                  'placeholder': 'Email Address'})

    def clean(self):
        cleaned_data = super(PasswordResetForm, self).clean()
        email = cleaned_data.get("email")

        if email:
            msg = "Error este email: %s, no se encuentra asociado a una cuenta\
                  " % (email)
            try:
                User.objects.get(email=email)
            except:
                self.add_error('email', msg)


class SetPasswordForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)

        self.fields['new_password1'].widget.attrs.update({'class': 'form-control',
                                                  'placeholder': 'Ingresa la nueva contraseña'})

        self.fields['new_password2'].widget.attrs.update({'class': 'form-control',
                                                  'placeholder': 'Repite la nueva contraseña'})


class FormularioUpdate(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'groups',
                  'is_staff', 'is_active']

    def __init__(self, *args, **kwargs):
        super(FormularioUpdate, self).__init__(*args, **kwargs)

        self.fields['first_name'].widget.attrs.update({'class': 'form-control',
        'placeholder': 'Nombres'})
        self.fields['first_name'].required=True
        self.fields['last_name'].widget.attrs.update({'class': 'form-control',
        'placeholder': 'Apellidos'})
        self.fields['last_name'].required=True
        self.fields['email'].widget.attrs.update({'class': 'form-control',
        'placeholder': 'Email'})
        self.fields['email'].required=True
        self.fields['is_staff'].label= 'Es Administrador?'
        self.fields['is_staff'].widget.attrs.update({'class': 'form-control'})
        self.fields['is_active'].label= 'Estara Activo?'
        self.fields['is_active'].widget.attrs.update({'class': 'form-control', 'checked': 'checked'})
        self.fields['groups'].widget.attrs.update({'class': 'form-control'})


class FormularioAdminRegistro(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2',
                  'first_name', 'last_name', 'email',
                  'groups', 'is_staff', 'is_active']

    def __init__(self, *args, **kwargs):
        super(FormularioAdminRegistro, self).__init__(*args, **kwargs)

        self.fields['first_name'].widget.attrs.update({'class': 'form-control',
                                                       'placeholder':
                                                       'Nombres'})
        self.fields['first_name'].required = True
        self.fields['last_name'].widget.attrs.update({'class': 'form-control',
                                                      'placeholder':
                                                      'Apellidos'})
        self.fields['last_name'].required = True
        self.fields['username'].widget.attrs.update({'class': 'form-control',
                                                     'placeholder':
                                                     'Nombre de usuario \
                                                     (Username)'})
        self.fields['username'].required = True
        self.fields['password1'].widget.attrs.update({'class': 'form-control',
                                                      'placeholder':
                                                      'Contraseña'})
        self.fields['password1'].required = True
        self.fields['password2'].widget.attrs.update({'class': 'form-control',
                                                      'placeholder':
                                                      'Repite la Contraseña'})
        self.fields['password2'].required = True
        self.fields['email'].widget.attrs.update({'class': 'form-control',
                                                  'placeholder': 'Email'})
        self.fields['email'].required = True
        self.fields['is_staff'].label = 'Es Administrador?'
        self.fields['is_staff'].widget.attrs.update({'class': 'form-control'})
        self.fields['is_active'].label = 'Estara Activo?'
        self.fields['is_active'].widget.attrs.update({'class': 'form-control'})
        self.fields['groups'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super(FormularioAdminRegistro, self).clean()
        email = cleaned_data.get("email")

        if email:
            msg = "Error este email: %s, ya se encuentra asociado a una cuenta\
                  " % (email)
            try:
                User.objects.get(email=email)
                self.add_error('email', msg)
            except:
                pass


class FormularioAdminRegPerfil(ModelForm):

    class Meta:
        model = UserProfile
        fields = ['fk_tipo_documento', 'id_perfil']

    def __init__(self, *args, **kwargs):
        super(FormularioAdminRegPerfil, self).__init__(*args, **kwargs)
        self.fields['fk_tipo_documento'].widget.attrs.update({'class': 'form-control'})
        self.fields['fk_tipo_documento'].label= 'Tipo de Documento'
        self.fields['fk_tipo_documento'].required=True
        self.fields['id_perfil'].widget.attrs.update({'class': 'form-control',
                                                      'placeholder':'Documento de identidad'})
        self.fields['id_perfil'].label= 'Cargo que tiene'
        self.fields['id_perfil'].required=True


class FormularioRegistroComun(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2',
                  'first_name', 'last_name', 'email']

    def __init__(self, arg):
        super(FormularioRegistroComun, self).__init__()
        self.fields['first_name'].widget.attrs.update({'class': 'form-control',
                                                       'placeholder':
                                                       'Nombres'})
        self.fields['first_name'].required = True
        self.fields['last_name'].widget.attrs.update({'class': 'form-control',
                                                      'placeholder':
                                                      'Apellidos'})
        self.fields['last_name'].required = True
        self.fields['username'].widget.attrs.update({'class': 'form-control',
                                                     'placeholder':
                                                     'Nombre de usuario \
                                                     (Username)'})
        self.fields['username'].required = True
        self.fields['password1'].widget.attrs.update({'class': 'form-control',
                                                      'placeholder':
                                                      'Contraseña'})
        self.fields['password1'].required = True
        self.fields['password2'].widget.attrs.update({'class': 'form-control',
                                                      'placeholder':
                                                      'Repite la Contraseña'})
        self.fields['password2'].required = True
        self.fields['email'].widget.attrs.update({'class': 'form-control',
                                                  'placeholder': 'Email'})
        self.fields['email'].required = True

    def clean(self):
        cleaned_data = super(FormularioRegistroComun, self).clean()
        email = cleaned_data.get("email")

        if email:
            msg = "Error este email: %s, ya se encuentra asociado a una cuenta\
                  " % (email)
            try:
                User.objects.get(email=email)
                self.add_error('email', msg)
            except:
                pass


class FormTwoStepLogin(forms.Form):
    contrasena_validate = CharField()
    usuario_validate = CharField()
    serial_validate = forms.IntegerField()
    remember_me_validate = BooleanField()

    class Meta:
        fields = ('contrasena_validate', 'usuario_validate',
                  'serial_validate', 'remember_me_validate')

    def __init__(self, *args, **kwargs):
        super(FormTwoStepLogin, self).__init__(*args, **kwargs)
        self.fields['contrasena_validate'].widget = PasswordInput()
        self.fields['contrasena_validate'].widget.attrs.update({'class': 'form-control',
        'placeholder': 'Contraseña', 'style':'display:none'})
        self.fields['usuario_validate'].widget.attrs.update({'class': 'form-control',
        'placeholder': 'Username o Email', 'style':'display:none'})
        self.fields['serial_validate'].widget.attrs.update({'class': 'form-control',
        'placeholder': 'Serial'})
        self.fields['remember_me_validate'].label = "Recordar"
        self.fields['remember_me_validate'].widget = CheckboxInput()
        self.fields['remember_me_validate'].required = False
        self.fields['remember_me_validate'].widget.attrs.update({'style':'display:none'})


class RegisterUserForm(UserCreationForm):
    """!
    Class that allows you to create the form to register users

    @author Ing. Leonel P. Hernandez M. (leonelphm@gmail.com)
    @author Ing. Luis Barrios (nikeven at gmail.com)
    @date 12-04-2018
    @version 1.0.0
    """

    class Meta:
        model = User
        fields = ['password1', 'password2', 'first_name',
                  'last_name', 'email', 'username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({'class': 'form-control',
                                                     'placeholder':
                                                     'Username', 'autofocus': False})

        self.fields['password1'].widget.attrs.update({'class': 'form-control',
                                                      'placeholder': 'Contraseña'})
        self.fields['password1'].required = True
        self.fields['password2'].widget.attrs.update({'class': 'form-control',
                                                      'placeholder': 'Repetir contraseña'})
        self.fields['password2'].required = True
        self.fields['email'].widget.attrs.update({'class': 'form-control',
                                                  'placeholder': 'Email'})
        self.fields['email'].required = True

        self.fields['first_name'].widget.attrs.update({'class': 'form-control',
                                                     'placeholder': 'Nombres'})
        self.fields['first_name'].required = True
        self.fields['last_name'].widget.attrs.update({'class': 'form-control',
                                                     'placeholder': 'Apellidos'})
        self.fields['last_name'].required = True

    def clean(self):
        cleaned_data = super(RegisterUserForm, self).clean()
        email = cleaned_data.get("email")
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            msg = "Password not match"
            self.add_error('password1', msg)

        if email:
            msg = "Error on mail: %s, has been used" % (email)
            try:
                User.objects.get(email=email)
                self.add_error('email', msg)
            except:
                pass