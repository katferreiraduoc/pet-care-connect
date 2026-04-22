from django.utils import timezone


MESES = [
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


def build_calendar_context(proximas_citas, hoy, calendar_factory):
    cal = calendar_factory(firstweekday=6)
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

    return {
        "calendar_weeks": semanas,
        "calendar_title": f"{MESES[hoy.month - 1]} {hoy.year}",
    }
