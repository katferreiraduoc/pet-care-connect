from django.db import models
from usuarios.models import Usuario


class Mascota(models.Model):
    SEXO_CHOICES = [
        ('macho', 'Macho'),
        ('hembra', 'Hembra'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=50)
    raza = models.CharField(max_length=80, blank=True, null=True)
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.nombre


class Alimentacion(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    tipo_alimento = models.CharField(max_length=100, blank=True, null=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    cantidad = models.CharField(max_length=50, blank=True, null=True)
    frecuencia = models.CharField(max_length=50, blank=True, null=True)
    horario = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.mascota.nombre} - {self.tipo_alimento}"