from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Rol, Usuario


class RegistroUsuarioForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, label="Nombre")
    last_name = forms.CharField(max_length=150, label="Apellido")
    email = forms.EmailField(label="Correo electronico")
    telefono = forms.CharField(max_length=20, required=False, label="Telefono")

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "telefono",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "first_name": "Ej. Catalina",
            "last_name": "Ej. Gonzalez",
            "username": "Ej. cata.petlover",
            "email": "tucorreo@ejemplo.com",
            "telefono": "+56 9 1234 5678",
            "password1": "Crea una contraseña segura",
            "password2": "Repite tu contraseña",
        }

        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "form-input",
                    "placeholder": placeholders.get(field_name, ""),
                }
            )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta registrada con este correo.")

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.telefono = self.cleaned_data["telefono"]
        user.rol = Rol.objects.filter(nombre="Cliente").first()

        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "username": "Ingresa tu usuario",
            "password": "Ingresa tu contraseña",
        }

        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "form-input",
                    "placeholder": placeholders.get(field_name, ""),
                }
            )


class PerfilUsuarioForm(forms.ModelForm):
    email = forms.EmailField(label="Correo electronico")
    telefono = forms.CharField(max_length=20, required=False, label="Telefono")

    class Meta:
        model = Usuario
        fields = ("email", "telefono")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "email": "tucorreo@ejemplo.com",
            "telefono": "+56 9 1234 5678",
        }

        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "form-input",
                    "placeholder": placeholders.get(field_name, ""),
                }
            )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if (
            Usuario.objects.filter(email__iexact=email)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError("Ya existe una cuenta registrada con este correo.")

        return email
