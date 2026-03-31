from django.contrib import admin
from .models import Rol, Usuario, Mascota, Cita, Tratamiento

admin.site.register(Rol)
admin.site.register(Usuario)
admin.site.register(Mascota)
admin.site.register(Cita)
admin.site.register(Tratamiento)