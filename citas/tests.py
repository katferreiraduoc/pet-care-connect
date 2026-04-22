from django.test import TestCase
from django.urls import reverse

from mascotas.models import Mascota
from usuarios.models import Usuario

from .models import Cita


class CitasViewTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="citas-user",
            password="testpass123",
        )
        self.otro_usuario = Usuario.objects.create_user(
            username="otro-user",
            password="testpass123",
        )
        self.client.force_login(self.usuario)
        self.mascota = Mascota.objects.create(
            usuario=self.usuario,
            nombre="Luna",
            especie="perro",
            sexo="hembra",
        )
        self.mascota_ajena = Mascota.objects.create(
            usuario=self.otro_usuario,
            nombre="Rocky",
            especie="perro",
            sexo="macho",
        )

    def get_valid_payload(self, **overrides):
        payload = {
            "mascota": self.mascota.id,
            "motivo": "Vacunacion anual",
            "fecha": "2026-05-15",
            "hora": "10:30",
            "clinica": "Clinica San Francisco",
            "veterinario": "Dra. Camila Soto",
            "observaciones": "Llevar carnet de vacunas.",
        }
        payload.update(overrides)
        return payload

    def test_usuario_puede_agendar_cita_para_mascota_propia(self):
        response = self.client.post(
            reverse("citas"),
            self.get_valid_payload(),
            follow=True,
        )

        self.assertRedirects(response, reverse("citas"))
        self.assertEqual(Cita.objects.count(), 1)
        cita = Cita.objects.get()
        self.assertEqual(cita.mascota, self.mascota)
        self.assertEqual(cita.motivo, "Vacunacion anual")
        mensajes = list(response.context["messages"])
        self.assertTrue(any("Cita agendada para" in str(m) for m in mensajes))

    def test_no_permite_agendar_cita_para_mascota_ajena(self):
        response = self.client.post(
            reverse("citas"),
            self.get_valid_payload(mascota=self.mascota_ajena.id),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Cita.objects.count(), 0)
        self.assertTrue(response.context["form"].errors)

    def test_post_invalido_no_guarda_cita_y_muestra_errores(self):
        response = self.client.post(
            reverse("citas"),
            self.get_valid_payload(fecha="", hora=""),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Cita.objects.count(), 0)
        self.assertIn("fecha", response.context["form"].errors)
        self.assertIn("hora", response.context["form"].errors)

    def test_listado_de_citas_muestra_datos_basicos(self):
        Cita.objects.create(
            mascota=self.mascota,
            motivo="Control general",
            clinica="Clinica Central",
            veterinario="Dr. Perez",
            fecha_cita="2026-05-20T11:00:00+00:00",
        )

        response = self.client.get(reverse("citas"))

        self.assertEqual(response.status_code, 200)
        citas_contexto = response.context["proximas_citas"]
        self.assertEqual(len(citas_contexto), 1)
        self.assertEqual(citas_contexto[0].motivo, "Control general")
        self.assertEqual(citas_contexto[0].mascota, self.mascota)
        self.assertEqual(citas_contexto[0].clinica, "Clinica Central")

    def test_listado_de_citas_vacio_entrega_contexto_sin_registros(self):
        response = self.client.get(reverse("citas"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["proximas_citas"], [])
        self.assertEqual(response.context["total_citas_mes"], 0)

    def test_usuario_puede_acceder_al_detalle_de_una_cita(self):
        cita = Cita.objects.create(
            mascota=self.mascota,
            motivo="Control general",
            clinica="Clinica Central",
            veterinario="Dr. Perez",
            fecha_cita="2026-05-20T11:00:00+00:00",
        )

        response = self.client.get(reverse("detalle_cita", args=[cita.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["cita"], cita)
        self.assertContains(response, "Control general")

    def test_usuario_no_puede_ver_detalle_de_cita_ajena(self):
        cita_ajena = Cita.objects.create(
            mascota=self.mascota_ajena,
            motivo="Revision",
            fecha_cita="2026-05-20T11:00:00+00:00",
        )

        response = self.client.get(reverse("detalle_cita", args=[cita_ajena.id]))

        self.assertEqual(response.status_code, 404)
