from django.db import models
from mascotas.models import Mascota


class Cita(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
    ]

    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    fecha_cita = models.DateTimeField()
    motivo = models.CharField(max_length=150)
    veterinario = models.CharField(max_length=100, blank=True, null=True)
    clinica = models.CharField(max_length=120, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.mascota.nombre} - {self.fecha_cita}"


class AtencionMedica(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    fecha_atencion = models.DateField()
    tipo_atencion = models.CharField(max_length=100)
    diagnostico = models.TextField(blank=True, null=True)
    tratamiento_indicado = models.TextField(blank=True, null=True)
    veterinario = models.CharField(max_length=100, blank=True, null=True)
    clinica = models.CharField(max_length=120, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.mascota.nombre} - {self.fecha_atencion}"