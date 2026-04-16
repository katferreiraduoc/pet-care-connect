from django import forms

from .models import Mascota


class MascotaForm(forms.ModelForm):
    ESPECIE_CHOICES = [
        ("perro", "Perro"),
        ("gato", "Gato"),
        ("ave", "Ave"),
        ("otro", "Otro"),
    ]

    especie = forms.ChoiceField(
        choices=ESPECIE_CHOICES,
        widget=forms.Select(attrs={"class": "form-input"}),
    )

    class Meta:
        model = Mascota
        fields = [
            "nombre",
            "especie",
            "raza",
            "fecha_nacimiento",
            "sexo",
            "peso",
        ]
        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Ej. Luna"}
            ),
            "raza": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Ej. Golden Retriever"}
            ),
            "fecha_nacimiento": forms.DateInput(
                attrs={"class": "form-input", "type": "date"}
            ),
            "sexo": forms.HiddenInput(),
            "peso": forms.NumberInput(
                attrs={
                    "class": "form-input peso-input",
                    "type": "range",
                    "min": "1",
                    "max": "50",
                    "step": "0.1",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sexo"].initial = (
            self.initial.get("sexo") or self.data.get("sexo") or "macho"
        )
        self.fields["peso"].initial = (
            self.initial.get("peso") or self.data.get("peso") or "12.5"
        )
