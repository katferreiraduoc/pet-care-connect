from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
import calendar

from citas.forms import CitaForm
from citas.models import Cita
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

@login_required
def citas(request):
    mascotas_usuario = Mascota.objects.filter(usuario=request.user).order_by("nombre")

    if request.method == "POST":
        form = CitaForm(request.POST, usuario=request.user)
        if form.is_valid():
            cita = form.save()
            messages.success(
                request,
                f"Cita agendada para {cita.mascota.nombre} el {timezone.localtime(cita.fecha_cita).strftime('%d/%m/%Y a las %H:%M')}.",
            )
            return redirect("citas")
        messages.error(request, "Revisa los datos del formulario antes de confirmar la cita.")
    else:
        form = CitaForm(usuario=request.user)

    proximas_citas = list(
        Cita.objects.filter(
            mascota__usuario=request.user,
            fecha_cita__gte=timezone.now(),
        ).select_related("mascota").order_by("fecha_cita")
    )

    hoy = timezone.localdate()
    cal = calendar.Calendar(firstweekday=6)
    semanas = []

    for semana in cal.monthdatescalendar(hoy.year, hoy.month):
        dias_semana = []
        for dia in semana:
            citas_dia = [
                cita
                for cita in proximas_citas
                if timezone.localtime(cita.fecha_cita).date() == dia
            ]
            dias_semana.append(
                {
                    "date": dia,
                    "is_current_month": dia.month == hoy.month,
                    "is_today": dia == hoy,
                    "appointments": citas_dia[:2],
                }
            )
        semanas.append(dias_semana)

    meses = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]

    context = {
        "form": form,
        "mascotas_usuario": mascotas_usuario,
        "proximas_citas": proximas_citas[:5],
        "total_citas_mes": sum(
            1
            for cita in proximas_citas
            if timezone.localtime(cita.fecha_cita).month == hoy.month
            and timezone.localtime(cita.fecha_cita).year == hoy.year
        ),
        "calendar_weeks": semanas,
        "calendar_title": f"{meses[hoy.month - 1]} {hoy.year}",
    }
    return render(request, 'citas.html', context)

def registros_medicos(request):
    return render(request, 'registros_medicos.html')

def dieta(request):
    return render(request, 'dieta.html')

def panel_control(request):
    return render(request, 'panel_control.html')