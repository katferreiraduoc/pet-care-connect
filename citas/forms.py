from datetime import datetime

from django import forms
from django.utils import timezone

from mascotas.models import Mascota

from .models import Cita


class CitaForm(forms.ModelForm):
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-input"})
    )
    hora = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-input"})
    )

    class Meta:
        model = Cita
        fields = ["mascota", "motivo", "clinica", "veterinario", "observaciones"]
        widgets = {
            "mascota": forms.Select(attrs={"class": "form-input"}),
            "motivo": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Ej. Vacunacion anual"}
            ),
            "clinica": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Ej. Clinica San Francisco"}
            ),
            "veterinario": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Ej. Dra. Camila Soto"}
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-input form-textarea",
                    "rows": 4,
                    "placeholder": "Detalles adicionales de la visita",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop("usuario", None)
        super().__init__(*args, **kwargs)
        if usuario is not None:
            self.fields["mascota"].queryset = Mascota.objects.filter(usuario=usuario)

    def save(self, commit=True):
        cita = super().save(commit=False)
        fecha = self.cleaned_data["fecha"]
        hora = self.cleaned_data["hora"]
        fecha_hora = datetime.combine(fecha, hora)
        cita.fecha_cita = timezone.make_aware(
            fecha_hora, timezone.get_current_timezone()
        )

        if commit:
            cita.save()
        return cita