from django.db import models
from mascotas.models import Mascota


class Cita(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    motivo = models.CharField(max_length=200)
    estado = models.CharField(max_length=20, default='pendiente')

    def __str__(self):
        return f"{self.mascota.nombre} - {self.fecha}"