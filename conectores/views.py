import os
import shutil
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from .forms import *
from .models import *
from datetime import datetime
from django.views.generic.edit import DeleteView, UpdateView

from certificados.models import Certificado
from .exceptions import ContrasenaDeCertificadoIncorrecta

class ConectorViews(LoginRequiredMixin, FormView):
    """
    """
    form_class = FormConector
    template_name = 'registrar_conector.html'
    success_url =reverse_lazy('conectores:registrar_conector')
    model = Conector
    hasher = PBKDF2PasswordHasher

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            record = Conector.objects.filter(pk=1).first()
            if record:
                form = FormConector(instance=record)
            else:
                form = FormConector()
            context['form']=form
        except Exception as e:
            raise e
        return context

    def form_valid(self,form):
        """!
        Form Valid Method

        @param form Recives form object
        @return validate True
        """
        try:
            transaction = Conector.objects.update_or_create(
                pk=1,
                defaults={
                'usuario': form['usuario'].value(),
                'url_erp': form['url_erp'].value(),
                'url_sii': form['url_sii'].value(),
                #'password': self.hasher().encode(password=form['password'].value(), salt='salt', iterations=50000),
                'password': form['password'].value(),
                'time_cron': form['time_cron'].value(),
                'certificado': form['certificado'].value(),
                'empresa': Compania.objects.get(pk=form['empresa'].value())
                })
            msg = "Se configuro el Conector con éxito"
            messages.info(self.request, msg)
        except Exception as e:
           msg = "Ocurrio un problema al guardar la información"
           messages.error(self.request, msg)
        return super().form_valid(form)
    def form_invalid(self, form):
        """!
        Form Invalid Method

        @param form Recives form object
        @return errors on form
        """
        messages.error(self.request, form.errors)
    
        return super().form_invalid(form)

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()

        kwargs['request'] = self.request

        return kwargs

class CompaniaViews(LoginRequiredMixin, FormView):
    """
    """
    form_class = FormCompania
    template_name = 'registrar_compania.html'
    success_url =reverse_lazy('conectores:registrar_compania')
    model = Compania

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form']=self.form_class
        context['companias']=Compania.objects.filter(owner=self.request.user)
        return context


    def form_valid(self,form):
        """!
        Form Valid Method

        @param form Recives form object
        @return validate True
        """

        try:

            instance = form.save(commit=False)
            pfx = instance.certificado.read()
            clave_privada, certificado, clave_publica  = \
            Compania.validar_certificado(pfx, form.cleaned_data['pass_certificado'])

        except ContrasenaDeCertificadoIncorrecta:

            messages.error(self.request, "Contraseña del certificado incorrecta")
            return super().form_invalid(form)



        try:
            saved_instance = form.save()
            Certificado.objects.create(
                    empresa=saved_instance,
                    owner=self.request.user,
                    private_key=clave_privada,
                    public_key=clave_publica,
                    certificado=certificado
                )
            msg = "Se configuro la Compañia con éxito"
            messages.info(self.request, msg)
        except Exception as e:
            msg = "Ocurrio un problema al guardar la información: "+str(e)
            messages.error(self.request, msg)
        # return super().form_valid(form)
        return HttpResponseRedirect(self.success_url)

    def form_invalid(self, form):
        """!
        Form Invalid Method

        @param form Recives form object
        @return errors on form
        """
        messages.error(self.request, "No se pudo crear la compania")

        return super().form_invalid(form)
    #     return HttpResponseRedirect(self.success_url)

class CompaniaUpdate(LoginRequiredMixin, UpdateView):
    form_class = CompaniaUpdateForm
    template_name = 'actualizar_compania.html'
    success_url =reverse_lazy('conectores:registrar_compania')
    model = Compania

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.kwargs)
        context['form']=CompaniaUpdateForm(instance=Compania.objects.get(pk=self.kwargs['pk']))
        context['object'] = Compania.objects.get(pk=self.kwargs['pk'])
        context['companias']=Compania.objects.filter(owner=self.request.user)
        return context

    def form_valid(self,form):
        
        compania = get_object_or_404(self.model, pk=self.kwargs['pk'])
        
        print (str(form.cleaned_data['logo']), str(str(compania.logo).split('/')[2]), str(form.cleaned_data['logo'])==str(str(compania.logo).split('/')[2]))

        if not str(form.cleaned_data['logo']) == str(compania.logo):
            files = self.request.FILES
            print (files['logo'].size)
            ruta_archivo = settings.MEDIA_ROOT+str(compania.logo)
            ruta = '/'.join(ruta_archivo.split('/')[:-1])
            if os.path.exists(ruta):
                shutil.rmtree(ruta)

        if not str(form.cleaned_data['certificado']) == str(compania.certificado):
            if form.cleaned_data['pass_certificado'] == '':
                msg = "Necesitas ingresar la contraseña del certificado"
                messages.error(self.request, msg)
                return super().form_invalid(form)
            ruta_archivo = settings.MEDIA_ROOT+str(compania.certificado)
            ruta = '/'.join(ruta_archivo.split('/')[:-1])
            if os.path.exists(ruta):
                shutil.rmtree(ruta)

        if form.cleaned_data['pass_certificado'] != '':
            try:

                instance = form.save(commit=False)
                pfx = instance.certificado.read()
                clave_privada, certificado, clave_publica  = \
                Compania.validar_certificado(pfx, form.cleaned_data['pass_certificado'])

            except ContrasenaDeCertificadoIncorrecta:

                messages.error(self.request, "Contraseña del certificado incorrecta")
                return super().form_invalid(form)

        try:
            update_compania = form.save()
    
            msg = "Se Actualizo la Compañia con éxito"
            messages.info(self.request, msg)
        except Exception as e:
            msg = "Ocurrio un problema al guardar la información: "+str(e)
            messages.error(self.request, msg)
        return super().form_invalid(form)
    
    def form_invalid(self, form):
        """!
        Form Invalid Method

        @param form Recives form object
        @return errors on form
        """
        messages.error(self.request, form.errors)
        return super().form_invalid(form)

class CompaniaDelete(LoginRequiredMixin, DeleteView):
    template_name = 'compania_confirm_delete.html'
    model = Compania
    success_url =reverse_lazy('conectores:registrar_compania')
