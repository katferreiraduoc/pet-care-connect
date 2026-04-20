from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.template.loader import get_template
import calendar


from xhtml2pdf import pisa

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
                (hoy.month, hoy.day) < (mascota.fecha_nacimiento.month, mascota.fecha_nacimiento.day)
            )
            mascota.edad_legible = f"{edad_anios} año" if edad_anios == 1 else f"{edad_anios} años"
        else:
            mascota.edad_legible = "Edad no registrada"

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
            citas_dia = [c for c in proximas_citas if timezone.localtime(c.fecha_cita).date() == dia]
            dias_semana.append({
                "date": dia,
                "is_current_month": dia.month == hoy.month,
                "is_today": dia == hoy,
                "appointments": citas_dia[:2],
            })
        semanas.append(dias_semana)

    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

    context = {
        "form": form,
        "mascotas_usuario": mascotas_usuario,
        "proximas_citas": proximas_citas[:5],
        "total_citas_mes": sum(1 for c in proximas_citas if timezone.localtime(c.fecha_cita).month == hoy.month),
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
        form = RegistroMedicoForm(request.POST, usuario=request.user, selected_pet=selected_pet)
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

            messages.success(request, f"Registro médico guardado para {mascota.nombre}.")
            return HttpResponseRedirect(f"{reverse('registros_medicos')}?pet={mascota.id}")

    else:
        form = RegistroMedicoForm(usuario=request.user, selected_pet=selected_pet, initial={"fecha_atencion": timezone.localdate()})

    atenciones = []
    vacunas = []
    tratamientos = []
    timeline = []

    if selected_pet:
        atenciones = AtencionMedica.objects.filter(mascota=selected_pet).order_by("-fecha_atencion")
        vacunas = Vacuna.objects.filter(mascota=selected_pet).order_by("-fecha_aplicacion")
        tratamientos = Tratamiento.objects.filter(atencion_medica__mascota=selected_pet).order_by("-fecha_inicio")

        for a in atenciones:
            timeline.append({"kind": "atencion", "date": a.fecha_atencion, "title": a.tipo_atencion, "description": a.diagnostico})
        for v in vacunas:
            timeline.append({"kind": "vacuna", "date": v.fecha_aplicacion, "title": v.nombre_vacuna, "description": v.observaciones})
        
        timeline.sort(key=lambda x: x["date"], reverse=True)

    context = {
        "form": form,
        "mascotas_usuario": mascotas_usuario,
        "selected_pet": selected_pet,
        "timeline": timeline,
    }
    return render(request, "registros_medicos.html", context)

@login_required
def descargar_ficha_pdf(request, mascota_id):
    mascota = get_object_or_404(Mascota, id=mascota_id, usuario=request.user)
    vacunas = Vacuna.objects.filter(mascota=mascota).order_by("-fecha_aplicacion")
    atenciones = AtencionMedica.objects.filter(mascota=mascota).order_by("-fecha_atencion")
    
    template_path = 'mascotaficha/mascota_ficha.html'
    context = {
        'mascota': mascota,
        'vacunas': vacunas,
        'atenciones': atenciones,
        'hoy': timezone.now()
    }
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ficha_{mascota.nombre}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
       return HttpResponse('Error al generar PDF')
       
    return response
def dieta(request):
    return render(request, 'dieta.html')

def panel_control(request):
    return render(request, 'panel_control.html')