from datetime import datetime

from django import forms
from django.utils import timezone

from mascotas.models import Mascota

from .models import AtencionMedica, Cita


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
                attrs={"class": "form-input", "placeholder": "Ej. Vacunación anual"}
            ),
            "clinica": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Ej. Clínica San Francisco"}
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


class RegistroMedicoForm(forms.ModelForm):
    mascota = forms.ModelChoiceField(
        queryset=Mascota.objects.none(),
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    peso_actual = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        max_digits=5,
        widget=forms.NumberInput(
            attrs={
                "class": "form-input",
                "placeholder": "Ej. 12.40",
                "step": "0.1",
                "min": "0",
            }
        ),
    )
    vacuna_nombre = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "Ej. Rabia anual"}
        ),
    )
    vacuna_proxima = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-input"}),
    )
    tratamiento_nombre = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "Ej. Apoquel"}
        ),
    )
    medicamento = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "Medicamento indicado"}
        ),
    )
    dosis = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "Ej. 1 comprimido cada 24h"}
        ),
    )
    frecuencia = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "Ej. Diario por 10 dias"}
        ),
    )
    fecha_fin_tratamiento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-input"}),
    )
    examenes_ordenados = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-input form-textarea",
                "rows": 3,
                "placeholder": "Ej. Hemograma, perfil bioquímico, ecografía abdominal",
            }
        ),
    )

    class Meta:
        model = AtencionMedica
        fields = [
            "mascota",
            "fecha_atencion",
            "tipo_atencion",
            "diagnostico",
            "tratamiento_indicado",
            "examenes_ordenados",
            "veterinario",
            "clinica",
            "observaciones",
        ]
        widgets = {
            "fecha_atencion": forms.DateInput(
                attrs={"type": "date", "class": "form-input"}
            ),
            "tipo_atencion": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Ej. Consulta general"}
            ),
            "diagnostico": forms.Textarea(
                attrs={
                    "class": "form-input form-textarea",
                    "rows": 4,
                    "placeholder": "Diagnóstico o hallazgos clínicos",
                }
            ),
            "tratamiento_indicado": forms.Textarea(
                attrs={
                    "class": "form-input form-textarea",
                    "rows": 4,
                    "placeholder": "Indicaciones médicas y cuidados a seguir",
                }
            ),
            "veterinario": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Nombre del veterinario"}
            ),
            "clinica": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Clínica u hospital"}
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-input form-textarea",
                    "rows": 4,
                    "placeholder": "Notas adicionales de la atención",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop("usuario", None)
        selected_pet = kwargs.pop("selected_pet", None)
        super().__init__(*args, **kwargs)
        if usuario is not None:
            queryset = Mascota.objects.filter(usuario=usuario).order_by("nombre")
            self.fields["mascota"].queryset = queryset
            if selected_pet is not None:
                self.fields["mascota"].initial = selected_pet
