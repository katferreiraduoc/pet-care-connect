from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import MascotaForm
from .models import Mascota

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

@login_required
def mis_mascotas(request):
    mascotas = list(
        Mascota.objects.filter(usuario=request.user).order_by("-fecha_registro")
    )
    hoy = timezone.localdate()

    for mascota in mascotas:
        if mascota.fecha_nacimiento:
            edad_anios = hoy.year - mascota.fecha_nacimiento.year - (
                (hoy.month, hoy.day)
                < (mascota.fecha_nacimiento.month, mascota.fecha_nacimiento.day)
            )
            mascota.edad_legible = (
                f"{edad_anios} año" if edad_anios == 1 else f"{edad_anios} años"
            )
        else:
            mascota.edad_legible = "Edad no registrada"

        mascota.especie_label = (mascota.especie or "Mascota").capitalize()
        mascota.raza_label = mascota.raza or "Raza no especificada"
        mascota.inicial = mascota.nombre[:1].upper() if mascota.nombre else "M"

    pesos = [float(mascota.peso) for mascota in mascotas if mascota.peso is not None]
    
    context = {
        "mascotas": mascotas,
        "total_mascotas": len(mascotas),
        "ultima_mascota": mascotas[0].nombre if mascotas else "Aún sin mascotas",
    }
    return render(request, "mis_mascotas.html", context)

def citas(request):
    return render(request, 'citas.html')

def registros_medicos(request):
    return render(request, 'registros_medicos.html')

def dieta(request):
    return render(request, 'dieta.html')

def panel_control(request):
    return render(request, 'panel_control.html')