"""!
Vista que controla los procesos de los usuarios

@author Ing. Leonel P. Hernandez M. (leonelphm at gmail.com)
@author Ing. Luis Barrios (nikeven at gmail.com)
@copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
@date 09-01-2017
@version 1.0.0
"""
from django.core import serializers
from django import forms
from django.db.models import Q
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    authenticate, logout, login
)
from django.contrib.auth.views import (
    redirect_to_login, PasswordResetView,
    PasswordResetDoneView, PasswordResetConfirmView,
    INTERNAL_RESET_URL_TOKEN,
    INTERNAL_RESET_SESSION_TOKEN,
    PasswordResetCompleteView
)

from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.auth.models import (
    Group, Permission, User
)
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.mixins import (
    LoginRequiredMixin
)
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import (
    JsonResponse, HttpResponseRedirect
)
from django.urls import (
    reverse_lazy, reverse
)
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.debug import sensitive_post_parameters

from django.shortcuts import (
    render, redirect, get_object_or_404
)
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.views.generic.edit import (
    FormView, UpdateView
)
from multi_form_view import MultiModelFormView

from .models import *
from .forms import *

from utils.views import (
    LoginRequeridoPerAuth, IpClient,
    TokenGenerator
)
from utils.logConstant import (
    ERROR, AUTHENTICATE, VALIDATE,
    LOGIN, LOGOUT, FORGOT
    )
from utils.messages import MENSAJES_LOGIN, MENSAJES_START


class LoginView(FormView):
    form_class = FormularioLogin
    template_name = 'users_login.html'
    success_url = '/inicio/'
    model = UserProfile
    form_vali = FormTwoStepLogin

    def dispatch(self, request, *args, **kwargs):
        """
        Returns the initial data to use for forms on this view.
        """
        dispatch = super(LoginView,self).dispatch(request, *args, **kwargs)
        if request.user.is_authenticated:
            print('utenticado')
            return redirect('utils:inicio')
        return dispatch

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_validationcode'] = self.form_vali
        return context


    def form_valid(self, form):
        """
        Validate the logeo form
        @return: Direct to the initial screen of the platform
        """
        usuario = form.cleaned_data['usuario']

        contrasena = form.cleaned_data['contrasena']

        validate = False
        try:
            validate_email(usuario)
            try:
                usuario = User.objects.get(email=usuario).username
            except:
                #messages.error(self.request, MENSAJES_LOGIN['CORREO_INVALIDO'] % (usuario))
                pass
        except Exception as e:
            pass
        ip_client = IpClient()
        get_ip = ip_client.get_client_ip(self.request)
        model_token = ContentType.objects.get_for_model(TwoFactToken).pk
        model_user = ContentType.objects.get_for_model(User).pk
        username = usuario
        usuario = authenticate(username=usuario, password=contrasena)
        if usuario is not None:
            #send mail token validations
            user = User.objects.get(username=username)
            token_gen = TokenGenerator()
            generate_token = token_gen.generate_token(user)
            obj = TwoFactToken.objects.get(serial=generate_token, user=user)
            msg = 'Successfully authenticated user'
            message = [{'athenticate': {'ip_client': get_ip, 'message': msg}}]
            LogEntry.objects.log_action(
                        user_id=user.pk,
                        content_type_id=model_user,
                        object_id=user.pk,
                        object_repr=str(user.username),
                        action_flag=AUTHENTICATE,
                        change_message=message
                        )
            if generate_token:
                msj_mail = 'This is the security token that you must enter before 5 minutes: %s' % (generate_token)
                try:
                    send_mail(
                                    'Validate Security',
                                    str(msj_mail),
                                    'info@user.com',
                                    [user.email],
                                    fail_silently=False,
                                )
                    validate = True
                    msg = 'Message sent succesfully'
                    message = [{'added': {'ip_client': get_ip, 'mail_send': msg}}]
                    LogEntry.objects.log_action(
                        user_id=user.pk,
                        content_type_id=model_token,
                        object_id=obj.pk,
                        object_repr=str(obj.serial),
                        action_flag=ADDITION,
                        change_message=message
                        )
                    # Time left to validation token expires
                    time = 5*60
                    return JsonResponse({'msg': msg, 'validate': validate,'time':time})
                except Exception as e:
                    validate = validate
                    msg = 'Error sent mail'
                    message = [{'error': {'ip_client': get_ip, 'mail_send': msg + str(e)}}]
                    LogEntry.objects.log_action(
                        user_id=user.pk,
                        content_type_id=model_token,
                        object_id=obj.pk,
                        object_repr=str(obj.serial),
                        action_flag=ERROR,
                        change_message=message
                        )
                    return JsonResponse({'msg': msg, 'validate': validate})

            else:
                validate = validate
                msg = 'User error does not exist'
                message = [{'error': {'ip_client': get_ip, 'message': msg}}]
                LogEntry.objects.log_action(
                    user_id=user.pk,
                    content_type_id=model_token,
                    object_id=user.pk,
                    object_repr='None',
                    action_flag=ERROR,
                    change_message=message
                    )
                return JsonResponse({'msg': msg, 'validate': validate})

        else:
            user = User.objects.filter(username=form.cleaned_data['usuario'])
            if user:
                user = user.get()
                if not user.is_active:
                    #messages.error(self.request, MENSAJES_LOGIN['CUENTA_INACTIVA'])
                    validate = validate
                    msg = str(MENSAJES_LOGIN['CUENTA_INACTIVA'])
                    message = [{'athenticate': {'ip_client': get_ip, 'message': msg}}]
                    LogEntry.objects.log_action(
                                user_id=user.pk,
                                content_type_id=model_user,
                                object_id=user.pk,
                                object_repr=str(user.username),
                                action_flag=AUTHENTICATE,
                                change_message=message
                                )
                    return JsonResponse({'msg': msg, 'validate': validate})
                elif usuario is None:
                    validate = validate
                    msg = str(MENSAJES_LOGIN['LOGIN_USUARIO_NO_VALIDO'])
                    message = [{'athenticate': {'ip_client': get_ip, 'message': msg}}]
                    user = User.objects.filter(groups__name="Super Admin").first()
                    LogEntry.objects.log_action(
                                user_id=user.pk,
                                content_type_id=model_user,
                                object_id=user.pk,
                                object_repr='None',
                                action_flag=AUTHENTICATE,
                                change_message=message
                                )
                    return JsonResponse({'msg': msg, 'validate': validate})

            else:
                #messages.warning(self.request, MENSAJES_LOGIN['LOGIN_USUARIO_NO_VALIDO'])
                validate = validate
                msg = str(MENSAJES_LOGIN['LOGIN_USUARIO_NO_VALIDO'])
                message = [{'athenticate': {'ip_client': get_ip, 'message': msg}}]
                user = User.objects.filter(groups__name="Super Admin").first()
                LogEntry.objects.log_action(
                            user_id=user.pk,
                            content_type_id=model_user,
                            object_id=user.pk,
                            object_repr='None',
                            action_flag=AUTHENTICATE,
                            change_message=message
                            )
                return JsonResponse({'msg': msg, 'validate': validate})

        return super().form_valid(form)

        def form_invalid(self, form):
            print(form.errors)
            return super().form_valid(form)


@method_decorator(csrf_exempt, name='dispatch')
class LoginValidateView(FormView):
    """!
    class that validates authentication in two stages

    @author Ing. Leonel P. Hernandez M. (leonelphm@gmail.com)
    @author Ing. Luis Barrios (nikeven at gmail.com)
    @date 12-04-2018
    @version 1.0.0
    """
    form_class= FormTwoStepLogin
    template_name = 'users_login.html'

    def form_valid(self, form):
        valuenext = self.request.POST.get('next')
        if valuenext.strip() != 'None':
            redirect_url = valuenext
        else:
            redirect_url = '/inicio'
        usuario = form.cleaned_data['usuario_validate']

        contrasena = form.cleaned_data['contrasena_validate']

        validation_code = form.cleaned_data['serial_validate']

        remember_me = form.cleaned_data['remember_me_validate']

        model_token = ContentType.objects.get_for_model(TwoFactToken).pk
        model_user = ContentType.objects.get_for_model(User).pk

        token_check = TokenGenerator()
        ip_client = IpClient()
        get_ip = ip_client.get_client_ip(self.request)
        validate = False
        try:
            validate_email(usuario)
            try:
                usuario = User.objects.get(email=usuario).username
            except:
                #messages.error(self.request, MENSAJES_LOGIN['CORREO_INVALIDO'] % (usuario))
                pass
        except Exception as e:
            pass
        username = usuario
        try:
            user = User.objects.get(username=username)
        except Exception as e:
            msg = 'User error does not exist'
            user = User.objects.filter(groups__name="Super Admin").first()
            message = [{'athenticate': {'ip_client': get_ip, 'message': msg}}]
            LogEntry.objects.log_action(
                    user_id=user.pk,
                    content_type_id=model_user,
                    object_id=user.pk,
                    object_repr='None',
                    action_flag=ERROR,
                    change_message=message
                    )
            return JsonResponse({'msg': msg, 'validate': validate})
        check_token = token_check.check_token(user.id, validation_code)
        if check_token:
            usuario = authenticate(username=usuario, password=contrasena)
            obj = TwoFactToken.objects.get(serial=validation_code, user=user)
            if usuario is not None:
                msg = 'Successfully authenticated user'
                message = [{'athenticate': {'ip_client': get_ip, 'message': msg}}]
                LogEntry.objects.log_action(
                            user_id=user.pk,
                            content_type_id=model_user,
                            object_id=user.pk,
                            object_repr=str(user.username),
                            action_flag=AUTHENTICATE,
                            change_message=message
                            )
                login(self.request, usuario)
                messages.info(self.request, MENSAJES_START['INICIO_SESION'] % (usuario.first_name, usuario.username))
                try:
                    parameter_location = ConfigParameter.objects.get(active=True)
                    parameter_location = parameter_location.geolocation
                except:
                    parameter_location = True
                self.request.session['permisos'] = list(usuario.get_all_permissions())
                self.request.session['location'] = parameter_location
                try:
                    grupos = usuario.groups.all()
                    grupo = []
                    if len(grupos) > 1:
                        for g in grupos:
                            grupo += str(g),
                    else:
                        grupo = str(usuario.groups.get())
                except:
                    grupo = "Does not belong to a group"

                self.request.session['grupos'] = grupo
            
                msg = 'Success when validating the user'
                validate = True
                message = [{'validate': {'ip_client': get_ip, 'message': msg}}]
                LogEntry.objects.log_action(
                        user_id=user.pk,
                        content_type_id=model_token,
                        object_id=obj.pk,
                        object_repr=str(validation_code),
                        action_flag=VALIDATE,
                        change_message=message
                        )
                message = [{'login': {'ip_client': get_ip, 'message': msg}}]
                LogEntry.objects.log_action(
                        user_id=user.pk,
                        content_type_id=model_user,
                        object_id=user.pk,
                        object_repr=str(user.username),
                        action_flag=LOGIN,
                        change_message=message
                        )
                return JsonResponse({'msg': msg, 'validate': validate, 'url_redirect': redirect_url})
            else:
                user = User.objects.filter(username=form.cleaned_data['usuario_validate'])
                if user:
                    user = user.get()
                    if not user.is_active:
                        #messages.error(self.request, MENSAJES_LOGIN['CUENTA_INACTIVA'])
                        validate = validate
                        msg = MENSAJES_LOGIN['CUENTA_INACTIVA']
                        message = [{'athenticate': {'ip_client': get_ip, 'message': msg}}]
                        LogEntry.objects.log_action(
                                    user_id=user.pk,
                                    content_type_id=model_user,
                                    object_id=user.pk,
                                    object_repr=str(user.username),
                                    action_flag=AUTHENTICATE,
                                    change_message=message
                                    )
                        return JsonResponse({'msg': msg, 'validate': validate})
                    elif usuario is None:
                        validate = validate
                        msg = str(MENSAJES_LOGIN['LOGIN_USUARIO_NO_VALIDO'])
                        message = [{'athenticate': {'ip_client': get_ip, 'message': msg}}]
                        user = User.objects.filter(groups__name="Super Admin").first()
                        LogEntry.objects.log_action(
                                    user_id=user.pk,
                                    content_type_id=model_user,
                                    object_id=user.pk,
                                    object_repr='None',
                                    action_flag=AUTHENTICATE,
                                    change_message=message
                                    )
                        return JsonResponse({'msg': msg, 'validate': validate})
                else:
                    #messages.warning(self.request, MENSAJES_LOGIN['LOGIN_USUARIO_NO_VALIDO'])
                    validate = validate
                    msg = str(MENSAJES_LOGIN['LOGIN_USUARIO_NO_VALIDO'])
                    message = [{'athenticate': {'ip_client': get_ip, 'message': msg}}]
                    user = User.objects.filter(groups__name="Super Admin").first()
                    LogEntry.objects.log_action(
                                user_id=user.pk,
                                content_type_id=model_user,
                                object_id=user.pk,
                                object_repr='None',
                                action_flag=AUTHENTICATE,
                                change_message=message
                                )
                    return JsonResponse({'msg': msg, 'validate': validate})
        else:
            msg = 'Token error invalid or expired'
            message = [{'error': {'ip_client': get_ip, 'message': msg}}]
            LogEntry.objects.log_action(
                        user_id=user.pk,
                        content_type_id=model_token,
                        object_id='None',
                        object_repr=str(validation_code),
                        action_flag=ERROR,
                        change_message=message
                        )
            return JsonResponse({'msg': msg, 'validate': validate})



class LogOutView(RedirectView):
    """!
    Salir de la apliacion

    @author Ing. Leonel P. Hernandez M. (leonelphm at gmail.com)
    @author Ing. Luis Barrios (nikeven at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    @date 09-01-2017
    @version 1.0.0
    """
    permanent = False
    query_string = True

    def get_redirect_url(self):
        """!
        Dirige a la pantalla del login
        @return: A la url del login
        """
        logout(self.request)
        return reverse_lazy('users:login')


class ListUsersView(LoginRequeridoPerAuth, TemplateView):
    """!
    Listar usuarios de la apliacion

    @author Ing. Leonel P. Hernandez M. (leonelphm at gmail.com)
    @author Ing. Luis Barrios (nikeven at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    @date 09-01-2017
    @version 1.0.0
    """
    template_name = "users_list.html"
    model = User
    success_url = reverse_lazy('users:lista_users')
    group_required = [u"Super Admin"]

    def __init__(self):
        super(ListUsersView, self).__init__()


    def post(self, *args, **kwargs):
        '''
        Cambia el estado activo a el usuario
        @return: Dirige a la tabla que muestra los usuarios de la apliacion
        '''
        accion = self.request.POST
        activar = accion.get('activar', None)
        inactivar = accion.get('inactivar', None)
        estado = False

        if activar is not None:
            user = activar
            estado = True
        elif inactivar is not None:
            user = inactivar
            estado = False
        else:
            messages.error(self.request, "Esta intentando hacer una accion incorrecta")      
        try:
            user_act = self.model.objects.get(pk=user)
            user_act.is_active = estado
            user_act.save()
            if estado:
                messages.success(self.request, "Se ha activado el usuario: %s" % (str(user_act)))
            else:
                messages.warning(self.request, "Se ha inactivado el usuario: %s" % (str(user_act)))
        except:
            messages.info(self.request, "El usuario no existe")
        return redirect(self.success_url)


class StartView(LoginRequiredMixin, TemplateView):
    """!
    Muestra el inicio de la plataforma

    @author Ing. Leonel P. Hernandez M. (leonelphm at gmail.com)
    @author Ing. Luis Barrios (nikeven at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    @date 09-01-2017
    @version 1.0.0
    @return: El template inicial de la plataforma
    """
    template_name = "home.html"

    def dispatch(self, request, *args, **kwargs):
        """
        Envia una alerta al usuario que intenta acceder sin estar logeado
        @return: Direcciona al login en caso de no poseer permisos, en caso contrario usa la clase
        """
        if not request.user.is_authenticated:
            messages.warning(self.request, "Debes iniciar Sessón")
            return self.handle_no_permission()
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        """Use this to add extra context."""
        try:
            perfil = UserProfile.objects.select_related().get(fk_user=self.request.user.id)
        except:
            perfil = None
        context = super(StartView, self).get_context_data(**kwargs)
        context['userprofile'] = perfil
        return context


class RegisterView(LoginRequeridoPerAuth, MultiModelFormView):
    """!
    Muestra el formulario de registro de usuarios

    @author Ing. Leonel P. Hernandez M. (leonelphm at gmail.com)
    @author Ing. Luis Barrios (nikeven at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    @date 09-01-2017
    @version 1.0.0
    """
    template_name = "users_register.html"
    form_classes = {
      'user': FormularioAdminRegistro,
      'user_perfil': FormularioAdminRegPerfil,
    }
    success_url = reverse_lazy('utils:inicio')
    model = Group
    model_permi = Permission
    group_required = [u"Super Admin"]
    record_id=None

    def get_context_data(self, **kwargs):
        """
        Carga el formulario en la vista,para registrar usuarios
        @return: El contexto con los objectos para la vista
        """
        return super(RegisterView, self).get_context_data(**kwargs)

    def forms_valid(self, forms, **kwargs):
        """
        Valida el formulario de registro del perfil de usuario
        @return: Dirige con un mensaje de exito a el home
        """
        nuevo_usuario = forms['user'].save()
        nuevo_perfil = forms['user_perfil'].save(commit=False)
        nuevo_perfil.fk_user = nuevo_usuario
        nuevo_perfil.save()
        usuario = forms['user'].cleaned_data['username']
        grupos = forms['user'].cleaned_data['groups']
        for group in grupos:
            # Agrega a el usuario al(los) grupo(s) seleccionado(s)
            nuevo_usuario.groups.add(group.pk)
        model_user = ContentType.objects.get_for_model(User).pk
        LogEntry.objects.log_action(
            user_id=self.request.user.id,
            content_type_id=model_user,
            object_id=nuevo_usuario.id,
            object_repr=str(nuevo_usuario.username),
            action_flag=ADDITION)
        messages.success(self.request, "Usuario %s creado con exito\
                                       " % (str(usuario)))
        return super(RegisterView, self).forms_valid(forms)

    def forms_invalid(self, forms, **kwargs):
        return super(RegisterView, self).forms_invalid(forms)

        
class ModalsPerfil(LoginRequeridoPerAuth, MultiModelFormView):
    """!
    Construye el modals para la actualizacion del usuario

    @author Ing. Leonel P. Hernandez M. (leonelphm at gmail.com)
    @author Ing. Luis Barrios (nikeven at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    @date 09-01-2017
    @version 1.0.0
    """
    model = UserProfile
    form_classes = {
      'user': FormularioUpdate,
      'user_perfil': FormularioAdminRegPerfil,
    }
    template_name = 'users_modalsProfile.html'
    success_url = reverse_lazy('users:lista_users')
    success_message = 'Usuario Actualizado con exito'
    group_required = [u"Super Admin"]
    record_id = None


    def get_context_data(self, **kwargs):
        """
        Carga el formulario en la vista,para registrar usuarios
        @return: El contexto con los objectos para la vista
        """
        context = super(ModalsPerfil, self).get_context_data(**kwargs)
        self.record_id = self.kwargs.get('pk', None)
        try:
            record = self.model.objects.select_related().get(fk_user=self.record_id)
        except UserProfile.DoesNotExist:
            record = None
        context['upUser'] = record
        return context

    def get_objects(self, **kwargs):
        """
        Carga el formulario en la vista,para actualizar el perfil del  usuario
        @return: El contexto con los objectos para la vista
        """
        self.record_id = self.kwargs.get('pk', None)
        try:
            record = self.model.objects.select_related().get(fk_user=self.record_id)
        except UserProfile.DoesNotExist:
            record = None
        return {
          'user_perfil': record,
          'user': record.fk_user if record else None}

    def get_success_url(self):
        return reverse('users:lista_users')

    def forms_valid(self, forms, **kwargs):
        """
        Valida el formulario de registro del perfil de usuario
        @return: Dirige con un mensaje de exito a el home
        """
        self.record_id = self.kwargs.get('pk', None)
        if self.record_id is not None:
            objeto = get_object_or_404(User, pk=self.record_id)
            update_usuario = FormularioUpdate(self.request.POST, instance=objeto)
            update_perfil = FormularioAdminRegPerfil(self.request.POST, instance=objeto)

            messages.success(self.request, "Usuario %s Actualizado con exito\
                                           " % (str(objeto.username)))
        return super(ModalsPerfil, self).forms_valid(forms)


class Error403(LoginRequiredMixin, TemplateView):
    template_name = "403.html"


class ResetPassConfirm(PasswordResetConfirmView):
    """!
    Class that inherits from the PasswordResetConfirmView which overwrites\
    the triggers and the form_view to make the respective saved in the log

    @author Ing. Leonel P. Hernandez M. (leonelphm@gmail.com)
    @author Ing. Luis Barrios (nikeven at gmail.com)
    @date 24-04-2018
    @version 1.0.0
    """
    form_class = SetPasswordForm
    template_name = 'users_confirm_reset.html'
    success_url = reverse_lazy('pass_done')

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        self.user = self.get_user(kwargs['uidb64'])
        ip_client = IpClient()
        get_ip = ip_client.get_client_ip(self.request)
        model_user = ContentType.objects.get_for_model(User).pk

        if self.user is not None:
            token = kwargs['token']
            if token == INTERNAL_RESET_URL_TOKEN:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    msg = 'The token is valid, you can recover the password'
                    message = [{'forgot': {'ip_client': get_ip,
                                                        'message': msg,
                                                        'validate': self.validlink}}]
                    LogEntry.objects.log_action(
                        user_id=self.user .pk,
                        content_type_id=model_user,
                        object_id=self.user .pk,
                        object_repr=str(self.user .username),
                        action_flag=FORGOT,
                        change_message=message
                        )
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(token, INTERNAL_RESET_URL_TOKEN)
                    return HttpResponseRedirect(redirect_url)

        # Display the "Password reset unsuccessful" page.
        msg = 'The token is invalid, you can not recover the password, verify the mail and try again, but request a new token'
        message = [{'forgot': {'ip_client': get_ip,
                                            'message': msg,
                                            'validate': self.validlink}}]
        LogEntry.objects.log_action(
            user_id=self.user .pk,
            content_type_id=model_user,
            object_id=self.user .pk,
            object_repr=str(self.user .username),
            action_flag=FORGOT,
            change_message=message
            )
        return self.render_to_response(self.get_context_data())

    def form_valid(self, form):
        ip_client = IpClient()
        get_ip = ip_client.get_client_ip(self.request)
        model_user = ContentType.objects.get_for_model(User).pk
        user = form.save()
        msg = 'The reset of the password is confirmed, the %s, has a new password' % (user.username)
        message = [{'forgot': {'ip_client': get_ip,
                                            'message': msg}}]
        LogEntry.objects.log_action(
            user_id=self.user .pk,
            content_type_id=model_user,
            object_id=self.user .pk,
            object_repr=str(self.user .username),
            action_flag=FORGOT,
            change_message=message
        )
        if self.post_reset_login:
            login(self.request, user, self.post_reset_login_backend)
        messages.success(self.request, msg)
        return super().form_valid(form)


class ResetPassSuccess(PasswordResetCompleteView):
    """!
    Class that inherits from the PasswordResetCompleteView which overwrites\
    the initial parameter of the template_name

    @author Ing. Leonel P. Hernandez M. (leonelphm@gmail.com)
    @author Ing. Luis Barrios (nikeven at gmail.com)
    @date 24-04-2018
    @version 1.0.0
    """
    template_name = 'users_pass_done.html'


class ResetPass(PasswordResetView):
    """!
    Class that inherits from the PasswordResetView which overwrites\
    the form to add the log of forgetfulness the password

    @author Ing. Leonel P. Hernandez M. leonelphm@gmail.com
    @date 24-04-2018
    @version 1.0.0
    """
    template_name = 'users_forgot.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy('users:reset_done')

    def form_valid(self, form):
        """!
        Form Valid Method

        @param form Recives form object
        @return send mail and save forgot log
        """
        ip_client = IpClient()
        get_ip = ip_client.get_client_ip(self.request)
        model_user = ContentType.objects.get_for_model(User).pk
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': self.html_email_template_name,
            'extra_email_context': self.extra_email_context,
        }
        form.save(**opts)
        email = form.cleaned_data['email']
        msg = 'The email was sent successfully to recover the password of the user %s' % (email)
        message = [{'forgot': {'ip_client': get_ip, 'mail_send': msg}}]
        user = User.objects.get(email=email)
        LogEntry.objects.log_action(
                        user_id=user.pk,
                        content_type_id=model_user,
                        object_id=user.pk,
                        object_repr=str(user.username),
                        action_flag=FORGOT,
                        change_message=message
                        )
        messages.success(self.request, "Se envio el correo electronico con exito")
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class ResetPassDone(PasswordResetDoneView):
    """!
    Class that inherits from the PasswordResetDoneView which overwrites\
    the initial parameter of the template_name

    @author Ing. Leonel P. Hernandez M. (leonelphm@gmail.com)
    @author Ing. Luis Barrios (nikeven at gmail.com)
    @date 24-04-2018
    @version 1.0.0
    """
    template_name = 'users_pass_reset_done.html'



class RegisterAccountView(FormView):
    """!
    Register View

    @author Rodrigo Boet (rudmanmrrod@gmail.com)
    @author Ing. Luis Barrios (nikeven at gmail.com)
    @date 17-04-2018
    @version 1.0.0
    """
    form_class = RegisterUserForm
    template_name = 'register.html'
    success_url = '/'

    def form_valid(self,form):
        """!
        Form Valid Method

        @param form Recives form object
        @return validate True
        """
        new_user = form.save(commit=False)

        new_user.save()
        new_user.groups.add(3)
        ip_client = IpClient()
        get_ip = ip_client.get_client_ip(self.request)
        model_user = ContentType.objects.get_for_model(User).pk
        msg = 'User registered successfully'
        LogEntry.objects.log_action(
                        user_id=new_user.pk,
                        content_type_id=model_user,
                        object_id=new_user.pk,
                        object_repr=str(new_user.username),
                        action_flag=ADDITION,
                        change_message=[{"added": {'ip_client': get_ip, 'message': msg}}]
                        )
        messages.info(self.request, msg)
        return super().form_valid(form)

    def form_invalid(self, form):
        """!
        Form Invalid Method

        @param form Recives form object
        @return errors on form
        """
        messages.error(self.request, form.errors)
    
        return super().form_invalid(form)
