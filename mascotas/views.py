import calendar
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max
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
            if tratamiento_nombre:
                Tratamiento.objects.create(
                    nombre_tratamiento=tratamiento_nombre,
                    descripcion=atencion.tratamiento_indicado,
                    medicamento=form.cleaned_data.get("medicamento"),
                    dosis=form.cleaned_data.get("dosis"),
                    frecuencia=form.cleaned_data.get("frecuencia"),
                    fecha_inicio=atencion.fecha_atencion,
                    fecha_fin=form.cleaned_data.get("fecha_fin_tratamiento"),
                    atencion_medica=atencion,
                )

            messages.success(request, f"Registro médico guardado para {mascota.nombre}.")
            return HttpResponseRedirect(f"{reverse('registros_medicos')}?pet={mascota.id}")
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
            AtencionMedica.objects.filter(mascota=selected_pet).order_by(
                "-fecha_atencion"
            )
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
                "subtitle": "Atención médica",
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
                "subtitle": "Vacunación",
                "description": vacuna.observaciones or "Vacuna aplicada y registrada.",
                "extra": (
                    f"Próxima dosis: {vacuna.fecha_proxima.strftime('%d/%m/%Y')}"
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
                "description": tratamiento.medicamento
                or tratamiento.descripcion
                or "Tratamiento registrado.",
                "extra": tratamiento.frecuencia or tratamiento.dosis,
            }
        )

    timeline.sort(key=lambda item: item["date"], reverse=True)

    context = {
        "form": form,
        "mascotas_usuario": mascotas_usuario,
        "selected_pet": selected_pet,
        "alergias_activas": alergias_activas,
        "proxima_vacuna": proxima_vacuna,
        "tratamientos_activos": [t for t in tratamientos if t.estado == "activo"],
        "veterinario_cabecera": veterinario_cabecera,
        "timeline": timeline,
    }
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
    hoy = timezone.localdate()
    ahora = timezone.now()
    semana_siguiente = hoy + timedelta(days=7)
    ventana_alertas = hoy + timedelta(days=30)

    mascotas = list(
        Mascota.objects.filter(usuario=request.user).order_by("-fecha_registro")
    )
    proximas_citas = list(
        Cita.objects.filter(
            mascota__usuario=request.user,
            fecha_cita__gte=ahora,
        )
        .select_related("mascota")
        .order_by("fecha_cita")[:5]
    )
    vacunas_proximas = list(
        Vacuna.objects.filter(
            mascota__usuario=request.user,
            fecha_proxima__isnull=False,
            fecha_proxima__lte=ventana_alertas,
        )
        .select_related("mascota")
        .order_by("fecha_proxima")[:5]
    )
    tratamientos_activos = list(
        Tratamiento.objects.filter(
            atencion_medica__mascota__usuario=request.user,
            estado="activo",
        )
        .select_related("atencion_medica", "atencion_medica__mascota")
        .order_by("fecha_inicio")[:4]
    )

    total_mascotas = len(mascotas)
    total_citas_mes = Cita.objects.filter(
        mascota__usuario=request.user,
        fecha_cita__year=hoy.year,
        fecha_cita__month=hoy.month,
    ).count()
    total_vacunas = Vacuna.objects.filter(mascota__usuario=request.user).count()
    tratamientos_activos_total = Tratamiento.objects.filter(
        atencion_medica__mascota__usuario=request.user,
        estado="activo",
    ).count()
    mascotas_con_dieta = (
        Alimentacion.objects.filter(mascota__usuario=request.user)
        .values("mascota")
        .distinct()
        .count()
    )
    mascotas_con_alergias = (
        Mascota.objects.filter(usuario=request.user)
        .exclude(alergias__isnull=True)
        .exclude(alergias="")
        .count()
    )

    ultimas_atenciones = {
        registro["mascota"]: registro["fecha_mas_reciente"]
        for registro in AtencionMedica.objects.filter(mascota__usuario=request.user)
        .values("mascota")
        .annotate(fecha_mas_reciente=Max("fecha_atencion"))
    }
    ultimas_dietas_por_mascota = {}
    for alimentacion in (
        Alimentacion.objects.filter(mascota__usuario=request.user)
        .select_related("mascota")
        .order_by("mascota_id", "-fecha_registro")
    ):
        ultimas_dietas_por_mascota.setdefault(alimentacion.mascota_id, alimentacion)

    for mascota in mascotas:
        mascota.edad_legible = _edad_legible(mascota.fecha_nacimiento, hoy)
        mascota.especie_label = (mascota.especie or "Mascota").capitalize()
        mascota.raza_label = mascota.raza or "Raza no especificada"
        mascota.inicial = mascota.nombre[:1].upper() if mascota.nombre else "M"
        mascota.proxima_cita = next(
            (cita for cita in proximas_citas if cita.mascota_id == mascota.id),
            None,
        )
        mascota.ultima_atencion = ultimas_atenciones.get(mascota.id)
        mascota.ultima_dieta = ultimas_dietas_por_mascota.get(mascota.id)

    alertas = []
    for vacuna in vacunas_proximas:
        dias = (vacuna.fecha_proxima - hoy).days
        if dias < 0:
            tono = "urgent"
            detalle = f"Vencida hace {abs(dias)} dia{'s' if abs(dias) != 1 else ''}"
        elif dias <= 7:
            tono = "warning"
            detalle = f"Vence en {dias} dia{'s' if dias != 1 else ''}"
        else:
            tono = "soft"
            detalle = f"Programada para {vacuna.fecha_proxima.strftime('%d/%m/%Y')}"

        alertas.append(
            {
                "tone": tono,
                "title": f"{vacuna.mascota.nombre}: {vacuna.nombre_vacuna}",
                "detail": detalle,
                "cta": "Revisar vacuna",
                "href": f"{reverse('registros_medicos')}?pet={vacuna.mascota.id}",
                "sort_key": (0 if tono == "urgent" else 1, vacuna.fecha_proxima),
            }
        )

    for cita in proximas_citas:
        fecha_local = timezone.localtime(cita.fecha_cita)
        dias = (fecha_local.date() - hoy).days
        if dias <= 3:
            alertas.append(
                {
                    "tone": "warning" if dias > 0 else "urgent",
                    "title": f"{cita.mascota.nombre}: {cita.motivo}",
                    "detail": fecha_local.strftime("%d/%m/%Y a las %H:%M"),
                    "cta": "Ver cita",
                    "href": reverse("citas"),
                    "sort_key": (1, fecha_local.date()),
                }
            )

    for mascota in mascotas:
        if mascota.ultima_dieta is None:
            alertas.append(
                {
                    "tone": "soft",
                    "title": f"{mascota.nombre}: dieta pendiente",
                    "detail": "Aún no tiene un plan de alimentación registrado.",
                    "cta": "Agregar dieta",
                    "href": f"{reverse('dieta')}?pet={mascota.id}",
                    "sort_key": (2, hoy),
                }
            )

    alertas.sort(key=lambda item: item["sort_key"])

    actividad_reciente = []
    for alimentacion in (
        Alimentacion.objects.filter(mascota__usuario=request.user)
        .select_related("mascota")
        .order_by("-fecha_registro")[:3]
    ):
        actividad_reciente.append(
            {
                "icon": "restaurant",
                "title": f"Dieta actualizada para {alimentacion.mascota.nombre}",
                "detail": alimentacion.tipo_alimento or "Plan de alimentación registrado",
                "date": timezone.localtime(alimentacion.fecha_registro),
                "sort_date": _normalizar_fecha_actividad(
                    timezone.localtime(alimentacion.fecha_registro)
                ),
            }
        )

    for atencion in (
        AtencionMedica.objects.filter(mascota__usuario=request.user)
        .select_related("mascota")
        .order_by("-fecha_atencion")[:3]
    ):
        actividad_reciente.append(
            {
                "icon": "medical_services",
                "title": f"Registro médico para {atencion.mascota.nombre}",
                "detail": atencion.tipo_atencion,
                "date": atencion.fecha_atencion,
                "sort_date": _normalizar_fecha_actividad(atencion.fecha_atencion),
            }
        )

    for vacuna in (
        Vacuna.objects.filter(mascota__usuario=request.user)
        .select_related("mascota")
        .order_by("-fecha_aplicacion")[:3]
    ):
        actividad_reciente.append(
            {
                "icon": "vaccines",
                "title": f"Vacuna registrada para {vacuna.mascota.nombre}",
                "detail": vacuna.nombre_vacuna,
                "date": vacuna.fecha_aplicacion,
                "sort_date": _normalizar_fecha_actividad(vacuna.fecha_aplicacion),
            }
        )

    actividad_reciente.sort(key=lambda item: item["sort_date"], reverse=True)

    context = {
        "mascotas": mascotas[:3],
        "total_mascotas": total_mascotas,
        "total_citas_mes": total_citas_mes,
        "total_vacunas": total_vacunas,
        "tratamientos_activos_total": tratamientos_activos_total,
        "mascotas_con_dieta": mascotas_con_dieta,
        "mascotas_con_alergias": mascotas_con_alergias,
        "alertas": alertas[:4],
        "proximas_citas": proximas_citas,
        "tratamientos_activos": tratamientos_activos,
        "actividad_reciente": actividad_reciente[:6],
        "sin_dieta_total": max(total_mascotas - mascotas_con_dieta, 0),
        "citas_semana_total": sum(
            1
            for cita in proximas_citas
            if timezone.localtime(cita.fecha_cita).date() <= semana_siguiente
        ),
        "saludo_nombre": request.user.first_name or request.user.username,
    }
    return render(request, "panel_control.html", context)
