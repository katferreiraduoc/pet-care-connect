def decorate_pet(mascota, hoy):
    mascota.edad_legible = _edad_legible(mascota.fecha_nacimiento, hoy)
    mascota.especie_label = (mascota.especie or "Mascota").capitalize()
    mascota.raza_label = mascota.raza or "Raza no especificada"
    mascota.inicial = mascota.nombre[:1].upper() if mascota.nombre else "M"
    return mascota


def decorate_pets(mascotas, hoy):
    return [decorate_pet(mascota, hoy) for mascota in mascotas]


def _edad_legible(fecha_nacimiento, hoy):
    if not fecha_nacimiento:
        return "Edad no registrada"

    edad_anios = hoy.year - fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )
    return f"{edad_anios} año" if edad_anios == 1 else f"{edad_anios} años"
