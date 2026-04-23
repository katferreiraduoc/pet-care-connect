from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import (
    CustomAuthenticationForm,
    PerfilUsuarioForm,
    RegistroUsuarioForm,
)
from .models import Veterinaria

class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    next_page = reverse_lazy("mis_mascotas")
    template_name = "usuarios/login.html"

def registro(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Cuenta creada correctamente. Ahora puedes iniciar sesión.",
            )
            return redirect("login")
    else:
        form = RegistroUsuarioForm()

    return render(request, "usuarios/register.html", {"form": form})


@login_required
def perfil(request):
    if request.method == "POST":
        form = PerfilUsuarioForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu perfil se actualizo correctamente.")
            return redirect("perfil")
        messages.error(request, "Revisa los datos del formulario antes de guardar.")
    else:
        form = PerfilUsuarioForm(instance=request.user)

    return render(
        request,
        "usuarios/perfil.html",
        {
            "usuario": request.user,
            "form": form,
        },
    )

def api_veterinarias(request):
    vets = Veterinaria.objects.exclude(latitud__isnull=True).exclude(
        longitud__isnull=True
    )

    data = [
        {
            "nombre": v.nombre,
            "direccion": v.direccion,
            "ciudad": v.ciudad,
            "lat": float(v.latitud),
            "lng": float(v.longitud),
        }
        for v in vets
    ]
    return JsonResponse(data, safe=False)