from django.db import migrations


def seed_roles(apps, schema_editor):
    Rol = apps.get_model('usuarios', 'Rol')

    roles = [
        ('Admin', 'Administrador del sistema'),
        ('Veterinario', 'Encargado de atenciones veterinarias'),
        ('Cliente', 'Dueño de mascotas'),
    ]

    for nombre, descripcion in roles:
        Rol.objects.get_or_create(
            nombre=nombre,
            defaults={'descripcion': descripcion}
        )


def unseed_roles(apps, schema_editor):
    Rol = apps.get_model('usuarios', 'Rol')
    Rol.objects.filter(nombre__in=['Admin', 'Veterinario', 'Cliente']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_roles, unseed_roles),
    ]