from django.db import models
from django.contrib.auth.models import AbstractUser

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.nombre

class Usuario(AbstractUser):
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

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

class Cita(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    motivo = models.CharField(max_length=200)
    estado = models.CharField(max_length=20, default='pendiente')

    def __str__(self):
        return f"{self.mascota.nombre} - {self.fecha}"

class Tratamiento(models.Model):
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Tratamiento - {self.cita.mascota.nombre}"

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