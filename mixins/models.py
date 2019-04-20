import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

class CreationModificationDateMixin(models.Model):
	"""
	Abstract base class with a creation and modification date and time	

	"""
	created = models.DateField(
		_("Tiempo y fecha de creación"),
		editable=True,
		auto_now_add=False,
		null=True,

	)
	modified = models.DateField(
		_("Tiempo y fecha de modificación"),
		null=True,
		editable=True,
		auto_now=False,
	)

	def save(self, *args, **kwargs):

		if not self.id:
			# Elimina las horas minutos y segundos para que sea mas facil buscar por fecha
			# a la hora de generar reportes de libro de venta o compra
			# date = timezone.now()
			date = datetime.date.today()
			self.created = date
		self.modified = timezone.now()
		return super(CreationModificationDateMixin, self).save(*args, **kwargs)


	class Meta:

		abstract = True