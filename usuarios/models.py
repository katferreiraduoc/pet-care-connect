from django.db import models

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.nombre

from django.contrib.auth.models import AbstractUser

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