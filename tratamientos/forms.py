from django import forms

from .models import Tratamiento


class TratamientoForm(forms.ModelForm):
    class Meta:
        model = Tratamiento
        fields = [
            "nombre_tratamiento",
            "descripcion",
            "medicamento",
            "dosis",
            "frecuencia",
            "fecha_inicio",
            "fecha_fin",
            "estado",
        ]
        widgets = {
            "nombre_tratamiento": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Ej. Apoquel"}
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-input form-textarea",
                    "rows": 4,
                    "placeholder": "Indicaciones y cuidados del tratamiento",
                }
            ),
            "medicamento": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Medicamento indicado"}
            ),
            "dosis": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Ej. 1 comprimido"}
            ),
            "frecuencia": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Ej. Cada 24 horas"}
            ),
            "fecha_inicio": forms.DateInput(
                attrs={"type": "date", "class": "form-input"}
            ),
            "fecha_fin": forms.DateInput(
                attrs={"type": "date", "class": "form-input"}
            ),
            "estado": forms.Select(attrs={"class": "form-input"}),
        }
