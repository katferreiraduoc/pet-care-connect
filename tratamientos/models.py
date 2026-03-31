from django.db import models
from citas.models import Cita


class Tratamiento(models.Model):
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Tratamiento - {self.cita.mascota.nombre}"