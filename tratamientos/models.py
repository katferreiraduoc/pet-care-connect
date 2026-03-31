from django.db import models
from citas.models import AtencionMedica


class Tratamiento(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('finalizado', 'Finalizado'),
        ('suspendido', 'Suspendido'),
    ]

    nombre_tratamiento = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True, null=True)
    medicamento = models.CharField(max_length=120, blank=True, null=True)
    dosis = models.CharField(max_length=50, blank=True, null=True)
    frecuencia = models.CharField(max_length=50, blank=True, null=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    atencion_medica = models.ForeignKey(AtencionMedica, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.nombre_tratamiento