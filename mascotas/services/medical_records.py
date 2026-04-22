from django.db import transaction
from django.utils import timezone

from citas.models import AtencionMedica
from tratamientos.models import Tratamiento

from mascotas.models import Mascota, Vacuna


def get_selected_pet(usuario, selected_pet_id):
    mascotas_usuario = Mascota.objects.filter(usuario=usuario).order_by("nombre")
    selected_pet = None

    if mascotas_usuario.exists():
        if selected_pet_id:
            selected_pet = mascotas_usuario.filter(id=selected_pet_id).first()
        if selected_pet is None:
            selected_pet = mascotas_usuario.first()

    return mascotas_usuario, selected_pet


@transaction.atomic
def save_medical_record(form):
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

    return atencion


def build_medical_records_context(mascotas_usuario, selected_pet, form):
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
        alergias_activas = _parse_allergies(selected_pet.alergias)
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

    return {
        "form": form,
        "mascotas_usuario": mascotas_usuario,
        "selected_pet": selected_pet,
        "alergias_activas": alergias_activas,
        "proxima_vacuna": proxima_vacuna,
        "tratamientos_activos": [t for t in tratamientos if t.estado == "activo"],
        "veterinario_cabecera": veterinario_cabecera,
        "timeline": build_medical_timeline(atenciones, vacunas, tratamientos),
    }


def build_medical_timeline(atenciones, vacunas, tratamientos):
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
    return timeline


def _parse_allergies(raw_allergies):
    if not raw_allergies:
        return []

    allergies = [
        allergy.strip()
        for allergy in raw_allergies.replace("\r", "").split("\n")
        if allergy.strip()
    ]
    if allergies:
        return allergies

    return [allergy.strip() for allergy in raw_allergies.split(",") if allergy.strip()]
