from django.urls import path

from .views import (
    agregar_mascota,
    citas,
    detalle_alimentacion,
    detalle_cita,
    editar_mascota,
    detalle_mascota,
    detalle_tratamiento,
    descargar_ficha_pdf,
    dieta,
    home,
    mis_mascotas,
    panel_control,
    registros_medicos,
    veterinarias_cercanas,
)

urlpatterns = [
    path("", home, name="home"),
    path("agregar-mascota/", agregar_mascota, name="agregar_mascota"),
    path("mis_mascotas/", mis_mascotas, name="mis_mascotas"),
    path("mis_mascotas/<int:mascota_id>/", detalle_mascota, name="detalle_mascota"),
    path("mis_mascotas/<int:mascota_id>/editar/", editar_mascota, name="editar_mascota"),
    path("citas/", citas, name="citas"),
    path("citas/<int:cita_id>/", detalle_cita, name="detalle_cita"),
    path("registros-medicos/", registros_medicos, name="registros_medicos"),
    path(
        "tratamientos/<int:tratamiento_id>/",
        detalle_tratamiento,
        name="detalle_tratamiento",
    ),
    path("mascota/<int:mascota_id>/pdf/", descargar_ficha_pdf, name="descargar_ficha_pdf"),
    path("dieta/", dieta, name="dieta"),
    path("dieta/<int:alimentacion_id>/", detalle_alimentacion, name="detalle_alimentacion"),
    path("veterinarias-cercanas/", veterinarias_cercanas, name="veterinarias_cercanas"),
    path("panel-control/", panel_control, name="panel_control"),
]
