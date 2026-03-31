from django.contrib import admin
from .models import Mascota, Alimentacion, Vacuna, Recordatorio

admin.site.register(Mascota)
admin.site.register(Alimentacion)
admin.site.register(Vacuna)
admin.site.register(Recordatorio)