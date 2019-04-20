from django import forms 

from .models import Folio


class FolioCreateForm(forms.ModelForm):

	class Meta:
		model = Folio
		fields = [

			'caf',
			'empresa'

		]

	def __init__(self, *args, **kwargs):

	    super().__init__(*args, **kwargs)

	    self.fields['caf'].widget.attrs.update({'class': 'form-control'})
	    self.fields['empresa'].widget.attrs.update({'class': 'form-control'})
	    self.fields['caf'].required = True
	    self.fields['caf'].empty_label = 'Seleccione archivo CAF'
