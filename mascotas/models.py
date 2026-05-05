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
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    esterilizado = models.BooleanField(default=False)
    alergias = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    foto = models.ImageField(upload_to='mascotas/', blank=True, null=True)

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
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mascota.nombre} - {self.tipo_alimento}"


class Vacuna(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    nombre_vacuna = models.CharField(max_length=100)
    fecha_aplicacion = models.DateField()
    fecha_proxima = models.DateField(blank=True, null=True)
    dosis = models.CharField(max_length=50, blank=True, null=True)
    veterinario = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.mascota.nombre} - {self.nombre_vacuna}"


class Recordatorio(models.Model):
    TIPO_RECORDATORIO_CHOICES = [
        ('vacuna', 'Vacuna'),
        ('tratamiento', 'Tratamiento'),
        ('cita', 'Cita'),
        ('control', 'Control'),
        ('otro', 'Otro'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('enviado', 'Enviado'),
        ('completado', 'Completado'),
    ]

    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    tipo_recordatorio = models.CharField(max_length=20, choices=TIPO_RECORDATORIO_CHOICES)
    titulo = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True, null=True)
    fecha_recordatorio = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    def __str__(self):
        return f"{self.mascota.nombre} - {self.titulo}"