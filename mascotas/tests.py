from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from citas.models import AtencionMedica, Cita
from tratamientos.models import Tratamiento
from usuarios.models import Usuario

from mascotas.models import Alimentacion, Mascota


class ProtectedViewsAccessTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="protegido",
            password="testpass123",
        )
        self.mascota = Mascota.objects.create(
            usuario=self.usuario,
            nombre="Luna",
            especie="gato",
            sexo="hembra",
        )
        self.cita = Cita.objects.create(
            mascota=self.mascota,
            fecha_cita=timezone.now() + timedelta(days=2),
            motivo="Control general",
        )
        self.atencion = AtencionMedica.objects.create(
            mascota=self.mascota,
            fecha_atencion=timezone.localdate(),
            tipo_atencion="Consulta general",
        )
        self.tratamiento = Tratamiento.objects.create(
            nombre_tratamiento="Apoquel",
            fecha_inicio=timezone.localdate(),
            atencion_medica=self.atencion,
        )
        self.alimentacion = Alimentacion.objects.create(
            mascota=self.mascota,
            tipo_alimento="Alimento seco",
        )

    def test_vistas_protegidas_redirigen_al_login_en_get(self):
        urls = [
            reverse("agregar_mascota"),
            reverse("mis_mascotas"),
            reverse("detalle_mascota", args=[self.mascota.id]),
            reverse("editar_mascota", args=[self.mascota.id]),
            reverse("citas"),
            reverse("detalle_cita", args=[self.cita.id]),
            reverse("registros_medicos"),
            reverse("detalle_tratamiento", args=[self.tratamiento.id]),
            reverse("descargar_ficha_pdf", args=[self.mascota.id]),
            reverse("dieta"),
            reverse("detalle_alimentacion", args=[self.alimentacion.id]),
            reverse("veterinarias_cercanas"),
            reverse("panel_control"),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_formularios_protegidos_redirigen_al_login_en_post(self):
        casos = [
            (
                reverse("agregar_mascota"),
                {
                    "nombre": "Luna",
                    "especie": "perro",
                    "sexo": "hembra",
                },
            ),
            (
                reverse("citas"),
                {
                    "mascota": self.mascota.id,
                    "motivo": "Vacunacion anual",
                    "fecha": "2026-05-15",
                    "hora": "10:30",
                },
            ),
            (
                reverse("registros_medicos"),
                {
                    "mascota": self.mascota.id,
                    "fecha_atencion": "2026-05-05",
                    "tipo_atencion": "Consulta general",
                },
            ),
            (
                reverse("dieta"),
                {
                    "mascota": self.mascota.id,
                    "tipo_alimento": "Alimento seco",
                },
            ),
        ]

        for url, payload in casos:
            with self.subTest(url=url):
                response = self.client.post(url, payload)
                self.assertRedirects(response, f"{reverse('login')}?next={url}")


class AgregarMascotaViewTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="registro-mascota",
            password="testpass123",
            first_name="Kathy",
        )
        self.client.force_login(self.usuario)

    def get_valid_payload(self, **overrides):
        payload = {
            "nombre": "Luna",
            "especie": "perro",
            "raza": "Golden Retriever",
            "fecha_nacimiento": "2022-04-10",
            "sexo": "hembra",
            "peso": "12.5",
        }
        payload.update(overrides)
        return payload

    def test_formulario_agregar_mascota_esta_disponible(self):
        response = self.client.get(reverse("agregar_mascota"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'method="post"', html=False)
        self.assertContains(response, 'name="nombre"', html=False)
        self.assertContains(response, 'type="submit"', html=False)

    def test_registro_mascota_guarda_datos_correctamente(self):
        response = self.client.post(reverse("agregar_mascota"), self.get_valid_payload())

        self.assertRedirects(response, reverse("agregar_mascota"))
        self.assertEqual(Mascota.objects.count(), 1)

        mascota = Mascota.objects.get()
        self.assertEqual(mascota.nombre, "Luna")
        self.assertEqual(mascota.especie, "perro")
        self.assertEqual(mascota.raza, "Golden Retriever")
        self.assertEqual(str(mascota.peso), "12.50")

    def test_mascota_queda_asociada_al_usuario_autenticado(self):
        self.client.post(reverse("agregar_mascota"), self.get_valid_payload())

        mascota = Mascota.objects.get()
        self.assertEqual(mascota.usuario, self.usuario)

    def test_registro_mascota_muestra_confirmacion(self):
        response = self.client.post(
            reverse("agregar_mascota"),
            self.get_valid_payload(),
            follow=True,
        )

        self.assertRedirects(response, reverse("agregar_mascota"))
        mensajes = list(response.context["messages"])
        self.assertTrue(any("fue registrada(o) correctamente" in str(m) for m in mensajes))


class MisMascotasViewTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="mis-mascotas",
            password="testpass123",
            first_name="Kathy",
        )
        self.otro_usuario = Usuario.objects.create_user(
            username="otro-usuario",
            password="testpass123",
        )
        self.client.force_login(self.usuario)
        self.mascota = Mascota.objects.create(
            usuario=self.usuario,
            nombre="Luna",
            especie="gato",
            raza="Siames",
            sexo="hembra",
            peso="4.80",
        )
        self.mascota_ajena = Mascota.objects.create(
            usuario=self.otro_usuario,
            nombre="Rocky",
            especie="perro",
            raza="Beagle",
            sexo="macho",
            peso="10.20",
        )

    def test_mis_mascotas_muestra_listado_del_usuario(self):
        response = self.client.get(reverse("mis_mascotas"))

        self.assertEqual(response.status_code, 200)
        mascotas = response.context["mascotas"]
        self.assertEqual(len(mascotas), 1)
        self.assertEqual(mascotas[0], self.mascota)
        self.assertContains(response, "Luna")
        self.assertNotContains(response, "Rocky")

    def test_mis_mascotas_muestra_datos_basicos(self):
        response = self.client.get(reverse("mis_mascotas"))

        self.assertContains(response, "Siames")
        self.assertContains(response, "4,80 kg")
        self.assertContains(response, "Hembra")

    def test_usuario_puede_acceder_al_detalle_de_su_mascota(self):
        response = self.client.get(reverse("detalle_mascota", args=[self.mascota.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["mascota"], self.mascota)
        self.assertContains(response, "Luna")
        self.assertContains(response, "Siames")

    def test_usuario_no_puede_acceder_al_detalle_de_mascota_ajena(self):
        response = self.client.get(reverse("detalle_mascota", args=[self.mascota_ajena.id]))

        self.assertEqual(response.status_code, 404)


class EditarMascotaViewTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="editar-mascota",
            password="testpass123",
        )
        self.otro_usuario = Usuario.objects.create_user(
            username="otro-editar",
            password="testpass123",
        )
        self.client.force_login(self.usuario)
        self.mascota = Mascota.objects.create(
            usuario=self.usuario,
            nombre="Luna",
            especie="gato",
            raza="Siames",
            sexo="hembra",
            fecha_nacimiento="2022-04-10",
            peso="4.80",
        )
        self.mascota_ajena = Mascota.objects.create(
            usuario=self.otro_usuario,
            nombre="Rocky",
            especie="perro",
            sexo="macho",
        )

    def get_valid_payload(self, **overrides):
        payload = {
            "nombre": "Mora",
            "especie": "perro",
            "raza": "Beagle",
            "fecha_nacimiento": "2021-08-15",
            "sexo": "hembra",
            "peso": "8.3",
        }
        payload.update(overrides)
        return payload

    def test_formulario_editar_mascota_esta_disponible_para_dueno(self):
        response = self.client.get(reverse("editar_mascota", args=[self.mascota.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Editar Mascota")
        self.assertContains(response, 'name="nombre"', html=False)
        self.assertContains(response, "Luna")

    def test_edicion_mascota_actualiza_datos_y_redirige_a_detalle(self):
        response = self.client.post(
            reverse("editar_mascota", args=[self.mascota.id]),
            self.get_valid_payload(),
            follow=True,
        )

        self.assertRedirects(response, reverse("detalle_mascota", args=[self.mascota.id]))
        self.mascota.refresh_from_db()
        self.assertEqual(self.mascota.nombre, "Mora")
        self.assertEqual(self.mascota.especie, "perro")
        self.assertEqual(self.mascota.raza, "Beagle")
        self.assertEqual(str(self.mascota.peso), "8.30")
        self.assertContains(response, "Mora")
        self.assertContains(response, "Beagle")
        mensajes = list(response.context["messages"])
        self.assertTrue(
            any("se actualizaron correctamente" in str(m) for m in mensajes)
        )

    def test_edicion_invalida_no_guarda_cambios_y_muestra_error(self):
        response = self.client.post(
            reverse("editar_mascota", args=[self.mascota.id]),
            self.get_valid_payload(nombre=""),
        )

        self.assertEqual(response.status_code, 200)
        self.mascota.refresh_from_db()
        self.assertEqual(self.mascota.nombre, "Luna")
        self.assertIn("nombre", response.context["form"].errors)
        self.assertContains(
            response,
            "Revisa los datos del formulario antes de guardar.",
        )

    def test_usuario_no_puede_editar_mascota_ajena(self):
        response = self.client.get(reverse("editar_mascota", args=[self.mascota_ajena.id]))

        self.assertEqual(response.status_code, 404)


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

    def test_post_invalido_no_guarda_registro_de_dieta_y_muestra_errores(self):
        response = self.client.post(
            reverse("dieta"),
            {
                "mascota": "",
                "tipo_alimento": "Alimento seco",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Alimentacion.objects.count(), 0)
        self.assertIn("mascota", response.context["form"].errors)

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

    def test_historial_dieta_muestra_datos_basicos_del_registro(self):
        Alimentacion.objects.create(
            mascota=self.mascota,
            tipo_alimento="Alimento seco",
            cantidad="120 g",
            frecuencia="2 veces al dia",
            horario="08:00 y 20:00",
        )

        response = self.client.get(reverse("dieta"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["registros_dieta"]), 1)
        self.assertContains(response, "Alimento seco")
        self.assertContains(response, "120 g")
        self.assertContains(response, "08:00 y 20:00")

    def test_historial_dieta_vacio_entrega_contexto_sin_registros(self):
        response = self.client.get(reverse("dieta"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["registros_dieta"], [])
        self.assertIsNone(response.context["dieta_actual"])

    def test_usuario_puede_consultar_detalle_de_registro_alimentacion(self):
        registro = Alimentacion.objects.create(
            mascota=self.mascota,
            tipo_alimento="Alimento seco",
            cantidad="120 g",
            frecuencia="2 veces al dia",
            horario="08:00 y 20:00",
            observaciones="Siempre con agua fresca.",
        )

        response = self.client.get(reverse("detalle_alimentacion", args=[registro.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["registro"], registro)
        self.assertContains(response, "Alimento seco")
        self.assertContains(response, "Siempre con agua fresca.")

    def test_usuario_no_puede_ver_detalle_de_alimentacion_ajena(self):
        otro_usuario = Usuario.objects.create_user(
            username="otro-detalle",
            password="testpass123",
        )
        mascota_ajena = Mascota.objects.create(
            usuario=otro_usuario,
            nombre="Rocky",
            especie="perro",
            sexo="macho",
        )
        registro_ajeno = Alimentacion.objects.create(
            mascota=mascota_ajena,
            tipo_alimento="Alimento humedo",
        )

        response = self.client.get(
            reverse("detalle_alimentacion", args=[registro_ajeno.id])
        )

        self.assertEqual(response.status_code, 404)


class PanelControlViewTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="panel",
            password="testpass123",
            first_name="Kathy",
        )
        self.client.force_login(self.usuario)
        self.mascota = Mascota.objects.create(
            usuario=self.usuario,
            nombre="Luna",
            especie="gato",
            sexo="hembra",
            peso="4.80",
        )
        Alimentacion.objects.create(
            mascota=self.mascota,
            tipo_alimento="Alimento seco",
            frecuencia="2 veces al dia",
        )
        Cita.objects.create(
            mascota=self.mascota,
            fecha_cita=timezone.now() + timedelta(days=2),
            motivo="Control general",
        )

    def test_panel_control_muestra_resumen_del_usuario(self):
        response = self.client.get(reverse("panel_control"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Luna")
        self.assertContains(response, "Control general")
        self.assertEqual(response.context["total_mascotas"], 1)
