import imaplib, email, os, json

from datetime import datetime
from base64 import b64decode,b64encode

from django.conf import settings
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseRedirect

from django.views.generic import TemplateView, RedirectView, ListView, DetailView
from django.shortcuts import get_object_or_404
from conectores.models import Compania
from .models import Intercambio, DteIntercambio


class SeleccionarEmpresaIntercambioView(TemplateView):
    template_name = 'intercambio_seleccionar_empresa.html'

    def get_context_data(self, *args, **kwargs): 

        context = super().get_context_data(*args, **kwargs)
        context['empresas'] = Compania.objects.filter(owner=self.request.user)
        if Compania.objects.filter(owner=self.request.user).exists():
            context['tiene_empresa'] = True
        else:
            messages.info(self.request, "Registre una empresa para continuar")
            context['tiene_empresa'] = False
        return context

    def post(self, request):

        empresa = int(request.POST.get('empresa'))

        if not empresa:
            return HttpResponseRedirect('/')
        empresa_obj = Compania.objects.get(pk=empresa)
        if empresa_obj and self.request.user == empresa_obj.owner:

            return HttpResponseRedirect(reverse_lazy('intercambios:lista', kwargs={'pk':empresa}))
        else:
            return HttpResponseRedirect('/')

class IntercambiosListView(ListView):
	template_name = "intercambios.html"
	
	def get_queryset(self):
		pk=self.kwargs.get('pk')
		user = self.request.user
		compania = Compania.objects.get(pk=pk)

		queryset = Intercambio.objects.filter(receptor=compania).order_by('-codigo_email')
		print(queryset)
		return queryset



class IntercambiosDetailView(DetailView):
	template_name="intercambio_detail.html"

	def get_object(self):

		compania_pk=self.kwargs.get('pk')
		intercambio_pk=self.kwargs.get('inter_pk')
		intercambio = get_object_or_404(
			Intercambio, 
			receptor=compania_pk, 
			pk=intercambio_pk
		)
		return intercambio



class RefrescarBandejaRedirectView(RedirectView):

	def get_redirect_url(self, *args, **kwargs):

		pk=self.kwargs.get('pk')
		mail = imaplib.IMAP4_SSL('imap.gmail.com')
		user = self.request.user
		compania = Compania.objects.get(pk=pk)
		print(compania)
		assert compania.correo_intercambio, "No hay correo"
		assert compania.pass_correo_intercambio, "No hay password"
		correo = compania.correo_intercambio.strip()
		passw = compania.pass_correo_intercambio.strip()
		print(correo,passw)
		try:

			mail.login(correo,passw)
		except imaplib.IMAP4.error as e:
			
			messages.error(self.request, str(e))
			return reverse_lazy('intercambios:lista', kwargs={'pk':pk})
		mail.list()
		mail.select("inbox")
		result, data = mail.search(None, "ALL")
		id_list = data[0].split()
		try:
			last_email = Intercambio.objects.latest('codigo_email')
		except Intercambio.DoesNotExist:
			last_email = 0

		last_email_code = int(id_list[-1].decode())
		if last_email == 0:

			local_last_email_code = last_email
		else:

			local_last_email_code = int(last_email.codigo_email)
		if last_email_code > local_last_email_code:

			new_elements = last_email_code - local_last_email_code
		else:
			messages.info(self.request, "No posee nuevos correos")
			return reverse_lazy('intercambios:lista', kwargs={'pk':pk})
		if new_elements == 1:

			latest_emails = [id_list[-1]]
		else:

			latest_emails = id_list[-new_elements:]
		for element in latest_emails:

			result, email_data = mail.fetch(element, "(RFC822)")
			raw_email = email_data[0][1]
			raw_multipart = email.message_from_bytes(raw_email)
			raw_email_string = raw_email.decode('utf-8')
			email_message = email.message_from_string(raw_email_string)
			attachment_count, attachments = self.get_attachment(raw_multipart)
			remisor_name, remisor_email = self.get_remisor(str(email.header.make_header(email.header.decode_header(email_message['From']))))
			Intercambio.objects.create(
				codigo_email = element.decode(),
				receptor = compania,
				remisor = remisor_name,
				email_remisor = remisor_email,
				fecha_de_recepcion = self.get_received_time(str(email.header.make_header(email.header.decode_header(email_message['Received'])))),
				cantidad_dte = attachment_count,
				titulo = str(email.header.make_header(email.header.decode_header(email_message['Subject']))),
				contenido = self.get_body(raw_multipart).decode('latin-1')
			) 

		messages.success(self.request, "Cantidad de correos nuevos: {}".format(new_elements))
		return reverse_lazy('intercambios:lista', kwargs={'pk':pk})

	def search(self, key, value, con):

		result, data = con.search(None,key,'"{}"'.format(value))
		return data

	def get_emails(self,results_bytes, mail):

		msgs = []
		for num in results_bytes[0].split():

			type, data = mail.fetch(num, "(RFC822)")
			msgs.append(data)
			print(email_from,email_to, subject)
		return msgs

	def get_body(self, msg):

		if msg.is_multipart():
			return self.get_body(msg.get_payload(0))
		else:
			return msg.get_payload(None, True)

	def get_attachment(self, msg):

		attachment_count = 0
		attachment_dict = dict() 
		for part in msg.walk():
			if part.get_content_maintype() == 'multipart':
				continue
			if part.get('Content-Disposition') is None:
				continue
			attachment_count += 1
			fileName = part.get_filename()
			if fileName is not None:
				decoded_filename = str(email.header.make_header(email.header.decode_header(fileName)))
				attachment_dict[decoded_filename] = part.get_payload(decode=True)
			else:
				attachment_dict["dte"+str(attachment_count)] = part.get_payload(decode=True)
		return (attachment_count,attachment_dict)

	def get_received_time(self, received_string):

		list_ = received_string.split('\r\n')
		final_date = list_[1].split()
		string_date = "{} {} {}".format(final_date[2], final_date[1], final_date[3])
		datef = datetime.strptime(string_date, '%b %d %Y')

		return datef

	def get_remisor(self, remisor_string):

		remisor = remisor_string.split('<')
		if len(remisor) > 1: 
			remisor_mail = remisor[1].strip('<>')
			remisor_name = remisor[0].strip()
			return remisor_name, remisor_mail
		else:
			return "Desconocido", remisor[0]



