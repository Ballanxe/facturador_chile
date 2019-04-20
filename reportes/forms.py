import datetime 
from django import forms 
from django.contrib.admin.widgets import AdminDateWidget

from .models import Reporte
from conectores.models import Compania


class ReporteCreateForm(forms.ModelForm):

    class Meta:
        model = Reporte
        fields = [

            'tipo_de_operacion',
            'tipo_de_envio',
            'tipo_de_libro',
            'fecha_de_inicio', 
            'fecha_de_culminacion',
            'folio_notificacion'

        ]

    def __init__(self, *args, **kwargs):

        self.request = kwargs.pop('request', None) 
        super().__init__(*args, **kwargs)

        self.fields['tipo_de_operacion'].widget.attrs.update({'class': 'form-control'})
        self.fields['tipo_de_envio'].widget.attrs.update({'class': 'form-control'})
        self.fields['tipo_de_libro'].widget.attrs.update({'class': 'form-control'}) 
        self.fields['folio_notificacion'].widget.attrs.update({'class': 'form-control'})
        self.fields['fecha_de_inicio'].widget.attrs.update({'autocomplete':'off','class': 'form-control datepicker', 'data-provide': 'datepicker','placeholder':'DD/MM/YYYY'})
        self.fields['fecha_de_culminacion'].widget.attrs.update({'autocomplete':'off','class': 'form-control datepicker', 'data-provide': 'datepicker','placeholder':'DD/MM/YYYY'})

    def clean(self):        

        cleaned_data = super(ReporteCreateForm, self).clean()
        today = datetime.date.today()
        fecha_de_inicio = cleaned_data.get('fecha_de_inicio')
        fecha_de_culminacion = cleaned_data.get('fecha_de_culminacion')

        if fecha_de_culminacion < fecha_de_inicio: 

            raise forms.ValidationError('Fecha de inicio no debe ser mayor a fecha de culminacion',code='invalid_date')

        if fecha_de_inicio > today:

            raise forms.ValidationError('Fecha de inicio no puede ser mayor a la fecha actual',code='inicio_mayor_actual')

        if fecha_de_culminacion > today:

            raise forms.ValidationError('Fecha de culminacion no puede ser mayor a la fecha actual',code='inicio_mayor_actual')

        return cleaned_data 




# self.fields['b2b_reviewer'].queryset = Affiliates.objects.filter(owner=self.request.user,verified=True,activated=True)