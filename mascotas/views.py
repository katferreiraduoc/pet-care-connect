from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
import calendar

from citas.forms import CitaForm, RegistroMedicoForm
from citas.models import AtencionMedica, Cita
from .forms import MascotaForm
from .models import Mascota, Vacuna
from tratamientos.models import Tratamiento

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

@login_required
def registros_medicos(request):
    mascotas_usuario = Mascota.objects.filter(usuario=request.user).order_by("nombre")
    selected_pet = None
    selected_pet_id = request.GET.get("pet")

    if mascotas_usuario.exists():
        if selected_pet_id:
            selected_pet = mascotas_usuario.filter(id=selected_pet_id).first()
        if selected_pet is None:
            selected_pet = mascotas_usuario.first()

    if request.method == "POST":
        form = RegistroMedicoForm(
            request.POST,
            usuario=request.user,
            selected_pet=selected_pet,
        )
        if form.is_valid():
            atencion = form.save()
            mascota = atencion.mascota

            peso_actual = form.cleaned_data.get("peso_actual")
            if peso_actual is not None:
                mascota.peso = peso_actual
                mascota.save(update_fields=["peso"])

            examenes_ordenados = form.cleaned_data.get("examenes_ordenados")
            if examenes_ordenados:
                extra_texto = f"\n\nOrdenes de examenes:\n{examenes_ordenados}"
                atencion.tratamiento_indicado = (
                    (atencion.tratamiento_indicado or "") + extra_texto
                ).strip()
                atencion.save(update_fields=["tratamiento_indicado"])

            vacuna_nombre = form.cleaned_data.get("vacuna_nombre")
            if vacuna_nombre:
                Vacuna.objects.create(
                    mascota=mascota,
                    nombre_vacuna=vacuna_nombre,
                    fecha_aplicacion=atencion.fecha_atencion,
                    fecha_proxima=form.cleaned_data.get("vacuna_proxima"),
                    veterinario=atencion.veterinario,
                    observaciones=atencion.observaciones,
                )

            tratamiento_nombre = form.cleaned_data.get("tratamiento_nombre")
            medicamento = form.cleaned_data.get("medicamento")
            if tratamiento_nombre or medicamento:
                Tratamiento.objects.create(
                    atencion_medica=atencion,
                    nombre_tratamiento=tratamiento_nombre or "Tratamiento indicado",
                    descripcion=atencion.tratamiento_indicado,
                    medicamento=medicamento,
                    dosis=form.cleaned_data.get("dosis"),
                    frecuencia=form.cleaned_data.get("frecuencia"),
                    fecha_inicio=atencion.fecha_atencion,
                    fecha_fin=form.cleaned_data.get("fecha_fin_tratamiento"),
                )

            messages.success(
                request,
                f"Registro médico guardado para {mascota.nombre}.",
            )
            return HttpResponseRedirect(
                f"{reverse('registros_medicos')}?pet={mascota.id}"
            )

        messages.error(request, "Revisa los datos del registro antes de guardar.")
    else:
        form = RegistroMedicoForm(
            usuario=request.user,
            selected_pet=selected_pet,
            initial={"fecha_atencion": timezone.localdate()},
        )

    atenciones = []
    vacunas = []
    tratamientos = []
    alergias_activas = []
    proxima_vacuna = None
    veterinario_cabecera = None

    if selected_pet is not None:
        atenciones = list(
            AtencionMedica.objects.filter(mascota=selected_pet).order_by("-fecha_atencion")
        )
        vacunas = list(
            Vacuna.objects.filter(mascota=selected_pet).order_by("-fecha_aplicacion")
        )
        tratamientos = list(
            Tratamiento.objects.filter(atencion_medica__mascota=selected_pet)
            .select_related("atencion_medica")
            .order_by("-fecha_inicio")
        )

        alergias_activas = [
            alergia.strip()
            for alergia in (selected_pet.alergias or "").replace("\r", "").split("\n")
            if alergia.strip()
        ]
        if not alergias_activas and selected_pet.alergias:
            alergias_activas = [
                alergia.strip()
                for alergia in selected_pet.alergias.split(",")
                if alergia.strip()
            ]

        proxima_vacuna = (
            Vacuna.objects.filter(
                mascota=selected_pet,
                fecha_proxima__gte=timezone.localdate(),
            )
            .order_by("fecha_proxima")
            .first()
        )

        ultima_atencion = atenciones[0] if atenciones else None
        if ultima_atencion and (ultima_atencion.veterinario or ultima_atencion.clinica):
            veterinario_cabecera = ultima_atencion

    timeline = []
    for atencion in atenciones:
        timeline.append(
            {
                "kind": "atencion",
                "date": atencion.fecha_atencion,
                "title": atencion.tipo_atencion,
                "subtitle": "Atencion medica",
                "description": atencion.diagnostico or atencion.observaciones,
                "extra": atencion.tratamiento_indicado,
            }
        )

    for vacuna in vacunas:
        timeline.append(
            {
                "kind": "vacuna",
                "date": vacuna.fecha_aplicacion,
                "title": vacuna.nombre_vacuna,
                "subtitle": "Vacunacion",
                "description": vacuna.observaciones or "Vacuna aplicada y registrada.",
                "extra": (
                    f"Proxima dosis: {vacuna.fecha_proxima.strftime('%d/%m/%Y')}"
                    if vacuna.fecha_proxima
                    else ""
                ),
            }
        )

    for tratamiento in tratamientos:
        timeline.append(
            {
                "kind": "tratamiento",
                "date": tratamiento.fecha_inicio,
                "title": tratamiento.nombre_tratamiento,
                "subtitle": "Tratamiento",
                "description": tratamiento.descripcion or tratamiento.medicamento,
                "extra": tratamiento.frecuencia or "",
            }
        )

    timeline.sort(key=lambda item: item["date"], reverse=True)

    context = {
        "form": form,
        "mascotas_usuario": mascotas_usuario,
        "selected_pet": selected_pet,
        "timeline": timeline,
        "alergias_activas": alergias_activas,
        "proxima_vacuna": proxima_vacuna,
        "tratamientos_activos": [t for t in tratamientos if t.estado == "activo"][:4],
        "veterinario_cabecera": veterinario_cabecera,
    }
    return render(request, "registros_medicos.html", context)

def dieta(request):
    return render(request, 'dieta.html')

def panel_control(request):
    return render(request, 'panel_control.html')
