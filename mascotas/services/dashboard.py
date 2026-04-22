from datetime import timedelta

from django.db.models import Max
from django.urls import reverse
from django.utils import timezone

from citas.models import AtencionMedica, Cita
from mascotas.models import Alimentacion, Mascota, Vacuna
from tratamientos.models import Tratamiento


def build_dashboard_context(usuario, edad_legible_fn, normalizar_fecha_fn):
    hoy = timezone.localdate()
    ahora = timezone.now()
    semana_siguiente = hoy + timedelta(days=7)
    ventana_alertas = hoy + timedelta(days=30)

    mascotas = list(Mascota.objects.filter(usuario=usuario).order_by("-fecha_registro"))
    proximas_citas = list(
        Cita.objects.filter(
            mascota__usuario=usuario,
            fecha_cita__gte=ahora,
        )
        .select_related("mascota")
        .order_by("fecha_cita")[:5]
    )
    vacunas_proximas = list(
        Vacuna.objects.filter(
            mascota__usuario=usuario,
            fecha_proxima__isnull=False,
            fecha_proxima__lte=ventana_alertas,
        )
        .select_related("mascota")
        .order_by("fecha_proxima")[:5]
    )
    tratamientos_activos = list(
        Tratamiento.objects.filter(
            atencion_medica__mascota__usuario=usuario,
            estado="activo",
        )
        .select_related("atencion_medica", "atencion_medica__mascota")
        .order_by("fecha_inicio")[:4]
    )

    total_mascotas = len(mascotas)
    total_citas_mes = Cita.objects.filter(
        mascota__usuario=usuario,
        fecha_cita__year=hoy.year,
        fecha_cita__month=hoy.month,
    ).count()
    total_vacunas = Vacuna.objects.filter(mascota__usuario=usuario).count()
    tratamientos_activos_total = Tratamiento.objects.filter(
        atencion_medica__mascota__usuario=usuario,
        estado="activo",
    ).count()
    mascotas_con_dieta = (
        Alimentacion.objects.filter(mascota__usuario=usuario)
        .values("mascota")
        .distinct()
        .count()
    )
    mascotas_con_alergias = (
        Mascota.objects.filter(usuario=usuario)
        .exclude(alergias__isnull=True)
        .exclude(alergias="")
        .count()
    )

    ultimas_atenciones = {
        registro["mascota"]: registro["fecha_mas_reciente"]
        for registro in AtencionMedica.objects.filter(mascota__usuario=usuario)
        .values("mascota")
        .annotate(fecha_mas_reciente=Max("fecha_atencion"))
    }
    ultimas_dietas_por_mascota = {}
    for alimentacion in (
        Alimentacion.objects.filter(mascota__usuario=usuario)
        .select_related("mascota")
        .order_by("mascota_id", "-fecha_registro")
    ):
        ultimas_dietas_por_mascota.setdefault(alimentacion.mascota_id, alimentacion)

    for mascota in mascotas:
        mascota.edad_legible = edad_legible_fn(mascota.fecha_nacimiento, hoy)
        mascota.especie_label = (mascota.especie or "Mascota").capitalize()
        mascota.raza_label = mascota.raza or "Raza no especificada"
        mascota.inicial = mascota.nombre[:1].upper() if mascota.nombre else "M"
        mascota.proxima_cita = next(
            (cita for cita in proximas_citas if cita.mascota_id == mascota.id),
            None,
        )
        mascota.ultima_atencion = ultimas_atenciones.get(mascota.id)
        mascota.ultima_dieta = ultimas_dietas_por_mascota.get(mascota.id)

    alertas = _build_alerts(hoy, mascotas, proximas_citas, vacunas_proximas)
    actividad_reciente = _build_recent_activity(usuario, normalizar_fecha_fn)

    return {
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
        "saludo_nombre": usuario.first_name or usuario.username,
    }


def _build_alerts(hoy, mascotas, proximas_citas, vacunas_proximas):
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
    return alertas


def _build_recent_activity(usuario, normalizar_fecha_fn):
    actividad_reciente = []

    for alimentacion in (
        Alimentacion.objects.filter(mascota__usuario=usuario)
        .select_related("mascota")
        .order_by("-fecha_registro")[:3]
    ):
        actividad_reciente.append(
            {
                "icon": "restaurant",
                "title": f"Dieta actualizada para {alimentacion.mascota.nombre}",
                "detail": alimentacion.tipo_alimento or "Plan de alimentación registrado",
                "date": timezone.localtime(alimentacion.fecha_registro),
                "sort_date": normalizar_fecha_fn(
                    timezone.localtime(alimentacion.fecha_registro)
                ),
            }
        )

    for atencion in (
        AtencionMedica.objects.filter(mascota__usuario=usuario)
        .select_related("mascota")
        .order_by("-fecha_atencion")[:3]
    ):
        actividad_reciente.append(
            {
                "icon": "medical_services",
                "title": f"Registro médico para {atencion.mascota.nombre}",
                "detail": atencion.tipo_atencion,
                "date": atencion.fecha_atencion,
                "sort_date": normalizar_fecha_fn(atencion.fecha_atencion),
            }
        )

    for vacuna in (
        Vacuna.objects.filter(mascota__usuario=usuario)
        .select_related("mascota")
        .order_by("-fecha_aplicacion")[:3]
    ):
        actividad_reciente.append(
            {
                "icon": "vaccines",
                "title": f"Vacuna registrada para {vacuna.mascota.nombre}",
                "detail": vacuna.nombre_vacuna,
                "date": vacuna.fecha_aplicacion,
                "sort_date": normalizar_fecha_fn(vacuna.fecha_aplicacion),
            }
        )

    actividad_reciente.sort(key=lambda item: item["sort_date"], reverse=True)
    return actividad_reciente
