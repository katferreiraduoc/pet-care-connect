from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import MascotaForm

def home(request):
    return render(request, 'home.html')


@login_required
def agregar_mascota(request):
    if request.method == "POST":
        form = MascotaForm(request.POST)
        if form.is_valid():
            mascota = form.save(commit=False)
            mascota.usuario = request.user
            mascota.save()
            messages.success(request, f"{mascota.nombre} fue registrada(o) correctamente.")
            return redirect("agregar_mascota")
        messages.error(request, "Revisa los datos del formulario antes de guardar.")
    else:
        form = MascotaForm(initial={"sexo": "macho", "peso": "12.5"})

    return render(request, 'mascota_add.html', {"form": form})

def mis_mascotas(request):
    return render(request, 'mis_mascotas.html')

def citas(request):
    return render(request, 'citas.html')

def registros_medicos(request):
    return render(request, 'registros_medicos.html')

def dieta(request):
    return render(request, 'dieta.html')

def panel_control(request):
    return render(request, 'panel_control.html')