import calendar

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from xhtml2pdf import pisa

from citas.forms import CitaForm, RegistroMedicoForm
from citas.models import AtencionMedica, Cita
from tratamientos.models import Tratamiento

from .forms import AlimentacionForm, MascotaForm
from .models import Alimentacion, Mascota, Vacuna
from .services import (
    build_dashboard_context,
    build_medical_records_context,
    get_selected_pet,
    save_medical_record,
)


def home(request):
    return render(request, "home.html")


@login_required
def veterinarias_cercanas(request):
    return render(request, "veterinarias_cercanas.html")


def _edad_legible(fecha_nacimiento, hoy):
    if not fecha_nacimiento:
        return "Edad no registrada"

    edad_anios = hoy.year - fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )
    return f"{edad_anios} año" if edad_anios == 1 else f"{edad_anios} años"


def _normalizar_fecha_actividad(valor):
    if hasattr(valor, "hour"):
        return valor
    return timezone.make_aware(
        timezone.datetime.combine(valor, timezone.datetime.min.time())
    )


@login_required
def agregar_mascota(request):
    if request.method == "POST":
        form = MascotaForm(request.POST)
        if form.is_valid():
            mascota = form.save(commit=False)
            mascota.usuario = request.user
            mascota.save()
            messages.success(
                request, f"{mascota.nombre} fue registrada(o) correctamente."
            )
            return redirect("agregar_mascota")
        messages.error(request, "Revisa los datos del formulario antes de guardar.")
    else:
        form = MascotaForm(initial={"sexo": "macho", "peso": "12.5"})
    return render(request, "mascota_add.html", {"form": form})


@login_required
def mis_mascotas(request):
    mascotas = list(
        Mascota.objects.filter(usuario=request.user).order_by("-fecha_registro")
    )
    hoy = timezone.localdate()

    for mascota in mascotas:
        mascota.edad_legible = _edad_legible(mascota.fecha_nacimiento, hoy)
        mascota.especie_label = (mascota.especie or "Mascota").capitalize()
        mascota.raza_label = mascota.raza or "Raza no especificada"
        mascota.inicial = mascota.nombre[:1].upper() if mascota.nombre else "M"

    context = {
        "mascotas": mascotas,
        "total_mascotas": len(mascotas),
        "ultima_mascota": mascotas[0].nombre if mascotas else "Aún sin mascotas",
    }
    return render(request, "mis_mascotas.html", context)


@login_required
def detalle_mascota(request, mascota_id):
    mascota = get_object_or_404(Mascota, id=mascota_id, usuario=request.user)
    hoy = timezone.localdate()
    mascota.edad_legible = _edad_legible(mascota.fecha_nacimiento, hoy)
    mascota.especie_label = (mascota.especie or "Mascota").capitalize()
    mascota.raza_label = mascota.raza or "Raza no especificada"
    mascota.inicial = mascota.nombre[:1].upper() if mascota.nombre else "M"

    context = {
        "mascota": mascota,
    }
    return render(request, "mascota_detalle.html", context)


@login_required
def detalle_cita(request, cita_id):
    cita = get_object_or_404(
        Cita.objects.select_related("mascota"),
        id=cita_id,
        mascota__usuario=request.user,
    )
    return render(request, "cita_detalle.html", {"cita": cita})


@login_required
def detalle_tratamiento(request, tratamiento_id):
    tratamiento = get_object_or_404(
        Tratamiento.objects.select_related("atencion_medica__mascota"),
        id=tratamiento_id,
        atencion_medica__mascota__usuario=request.user,
    )
    return render(request, "tratamiento_detalle.html", {"tratamiento": tratamiento})


@login_required
def detalle_alimentacion(request, alimentacion_id):
    registro = get_object_or_404(
        Alimentacion.objects.select_related("mascota"),
        id=alimentacion_id,
        mascota__usuario=request.user,
    )
    return render(request, "alimentacion_detalle.html", {"registro": registro})


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
        messages.error(
            request, "Revisa los datos del formulario antes de confirmar la cita."
        )
    else:
        form = CitaForm(usuario=request.user)

    proximas_citas = list(
        Cita.objects.filter(
            mascota__usuario=request.user,
            fecha_cita__gte=timezone.now(),
        )
        .select_related("mascota")
        .order_by("fecha_cita")
    )

    hoy = timezone.localdate()
    cal = calendar.Calendar(firstweekday=6)
    semanas = []
    for semana in cal.monthdatescalendar(hoy.year, hoy.month):
        dias_semana = []
        for dia in semana:
            citas_dia = [
                c for c in proximas_citas if timezone.localtime(c.fecha_cita).date() == dia
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
        ),
        "calendar_weeks": semanas,
        "calendar_title": f"{meses[hoy.month - 1]} {hoy.year}",
    }
    return render(request, "citas.html", context)


@login_required
def registros_medicos(request):
    mascotas_usuario, selected_pet = get_selected_pet(
        request.user, request.GET.get("pet")
    )

    if request.method == "POST":
        form = RegistroMedicoForm(
            request.POST,
            usuario=request.user,
            selected_pet=selected_pet,
        )
        if form.is_valid():
            atencion = save_medical_record(form)
            mascota = atencion.mascota
            messages.success(request, f"Registro médico guardado para {mascota.nombre}.")
            return HttpResponseRedirect(f"{reverse('registros_medicos')}?pet={mascota.id}")
    else:
        form = RegistroMedicoForm(
            usuario=request.user,
            selected_pet=selected_pet,
            initial={"fecha_atencion": timezone.localdate()},
        )

    context = build_medical_records_context(mascotas_usuario, selected_pet, form)
    return render(request, "registros_medicos.html", context)


@login_required
def descargar_ficha_pdf(request, mascota_id):
    mascota = get_object_or_404(Mascota, id=mascota_id, usuario=request.user)
    vacunas = Vacuna.objects.filter(mascota=mascota).order_by("-fecha_aplicacion")
    atenciones = AtencionMedica.objects.filter(mascota=mascota).order_by(
        "-fecha_atencion"
    )

    template = get_template("mascotaficha/mascota_ficha.html")
    html = template.render(
        {
            "mascota": mascota,
            "vacunas": vacunas,
            "atenciones": atenciones,
            "hoy": timezone.now(),
        }
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="ficha_{mascota.nombre}.pdf"'
    )

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error al generar PDF", status=500)

    return response


@login_required
def dieta(request):
    mascotas_usuario = Mascota.objects.filter(usuario=request.user).order_by("nombre")
    selected_pet = None
    selected_pet_id = request.GET.get("pet")

    if mascotas_usuario.exists():
        if selected_pet_id:
            selected_pet = mascotas_usuario.filter(id=selected_pet_id).first()
        if selected_pet is None:
            selected_pet = mascotas_usuario.first()

    if request.method == "POST":
        form = AlimentacionForm(
            request.POST,
            usuario=request.user,
            selected_pet=selected_pet,
        )
        if form.is_valid():
            alimentacion = form.save()
            messages.success(
                request,
                f"Dieta registrada para {alimentacion.mascota.nombre}.",
            )
            return HttpResponseRedirect(
                f"{reverse('dieta')}?pet={alimentacion.mascota.id}"
            )
        messages.error(request, "Revisa los datos de alimentación antes de guardar.")
    else:
        form = AlimentacionForm(usuario=request.user, selected_pet=selected_pet)

    registros_dieta = []
    dieta_actual = None

    if selected_pet is not None:
        registros_dieta = list(
            Alimentacion.objects.filter(mascota=selected_pet).order_by("-fecha_registro")
        )
        dieta_actual = registros_dieta[0] if registros_dieta else None

    resumen_frecuencia = (
        dieta_actual.frecuencia
        if dieta_actual and dieta_actual.frecuencia
        else "Sin definir"
    )
    resumen_horario = (
        dieta_actual.horario
        if dieta_actual and dieta_actual.horario
        else "Sin horario registrado"
    )

    context = {
        "form": form,
        "mascotas_usuario": mascotas_usuario,
        "selected_pet": selected_pet,
        "registros_dieta": registros_dieta,
        "dieta_actual": dieta_actual,
        "resumen_frecuencia": resumen_frecuencia,
        "resumen_horario": resumen_horario,
    }
    return render(request, "dieta.html", context)


@login_required
def panel_control(request):
    context = build_dashboard_context(
        request.user,
        edad_legible_fn=_edad_legible,
        normalizar_fecha_fn=_normalizar_fecha_actividad,
    )
    return render(request, "panel_control.html", context)