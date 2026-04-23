from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import CustomAuthenticationForm, RegistroUsuarioForm
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
    return render(request, "usuarios/perfil.html", {"usuario": request.user})

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