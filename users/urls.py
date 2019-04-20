from django.urls import path

from .forms import PasswordResetForm
from .ajaxs import *
from .views import *

app_name = 'users'
urlpatterns = [
    path('', LoginView.as_view(), name="login"),
    path('login_validate/', LoginValidateView.as_view(), name="login_validate"),
    path('logout/', LogOutView.as_view(), name="logout"),
    
    # Reset password all users
    path('accounts/password/reset/', ResetPass.as_view(), name='forgot'),
    path('accounts/password/done/', ResetPassDone.as_view(), name='reset_done'),
    path('registrar-cuenta', RegisterAccountView.as_view(), name='registrar_cuenta'),
    
    # Urls Access Super Admin
    path('lista-usuarios/', ListUsersView.as_view(), name="lista_users"),
    path('perfil/<int:pk>/', ModalsPerfil.as_view(),
        name="modal_perfil"),
    path('registrar/', RegisterView.as_view(), name="registrar"),

    # Ajax list Users, for Super Admin
    path('listar-usuarios/', ListUsersAjaxView.as_view(),
        name="listar_users"),
    path('error-403/', Error403.as_view(),
        name="403error"),
]