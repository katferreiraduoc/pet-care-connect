from django import forms

from .models import Alimentacion, Mascota


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
            "foto",
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


class AlimentacionForm(forms.ModelForm):
    mascota = forms.ModelChoiceField(
        queryset=Mascota.objects.none(),
        widget=forms.Select(attrs={"class": "form-input"}),
        empty_label="Selecciona una mascota",
    )

    class Meta:
        model = Alimentacion
        fields = [
            "mascota",
            "tipo_alimento",
            "marca",
            "cantidad",
            "frecuencia",
            "horario",
            "observaciones",
        ]
        widgets = {
            "tipo_alimento": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Ej. Alimento seco"}
            ),
            "marca": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Ej. Royal Canin"}
            ),
            "cantidad": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Ej. 120 g por porcion"}
            ),
            "frecuencia": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Ej. 2 veces al dia"}
            ),
            "horario": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Ej. 08:00 y 20:00"}
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-input form-textarea",
                    "placeholder": "Alergias, premios permitidos, agua, indicaciones especiales...",
                    "rows": 4,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop("usuario", None)
        selected_pet = kwargs.pop("selected_pet", None)
        super().__init__(*args, **kwargs)

        queryset = Mascota.objects.none()
        if usuario is not None:
            queryset = Mascota.objects.filter(usuario=usuario).order_by("nombre")

        self.fields["mascota"].queryset = queryset
        if selected_pet is not None:
            self.fields["mascota"].initial = selected_pet
