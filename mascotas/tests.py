from django.test import TestCase
from django.urls import reverse

from mascotas.models import Alimentacion, Mascota
from usuarios.models import Usuario


class DietaViewTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="kathy",
            password="testpass123",
        )
        self.client.force_login(self.usuario)
        self.mascota = Mascota.objects.create(
            usuario=self.usuario,
            nombre="Luna",
            especie="perro",
            sexo="hembra",
        )

    def test_crea_registro_de_dieta_para_mascota_del_usuario(self):
        response = self.client.post(
            reverse("dieta"),
            {
                "mascota": self.mascota.id,
                "tipo_alimento": "Alimento seco",
                "marca": "Pro Plan",
                "cantidad": "120 g",
                "frecuencia": "2 veces al dia",
                "horario": "08:00 y 20:00",
                "observaciones": "Siempre con agua fresca.",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Alimentacion.objects.count(), 1)
        registro = Alimentacion.objects.get()
        self.assertEqual(registro.mascota, self.mascota)
        self.assertEqual(registro.marca, "Pro Plan")

    def test_no_permite_registrar_dieta_para_mascota_de_otro_usuario(self):
        otro_usuario = Usuario.objects.create_user(
            username="otro",
            password="testpass123",
        )
        mascota_ajena = Mascota.objects.create(
            usuario=otro_usuario,
            nombre="Rocky",
            especie="perro",
            sexo="macho",
        )

        response = self.client.post(
            reverse("dieta"),
            {
                "mascota": mascota_ajena.id,
                "tipo_alimento": "Alimento humedo",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Alimentacion.objects.count(), 0)
