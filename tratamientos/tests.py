from django.test import TestCase
from django.urls import reverse

from citas.models import AtencionMedica
from mascotas.models import Mascota
from usuarios.models import Usuario

from .models import Tratamiento


class TratamientosFlowTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="tratamientos-user",
            password="testpass123",
        )
        self.otro_usuario = Usuario.objects.create_user(
            username="otro-tratamiento",
            password="testpass123",
        )
        self.client.force_login(self.usuario)
        self.mascota = Mascota.objects.create(
            usuario=self.usuario,
            nombre="Luna",
            especie="gato",
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
            "fecha_atencion": "2026-05-05",
            "tipo_atencion": "Consulta general",
            "diagnostico": "Dermatitis leve",
            "tratamiento_indicado": "Aplicar medicamento por 10 dias.",
            "examenes_ordenados": "Hemograma",
            "veterinario": "Dra. Soto",
            "clinica": "Clinica Central",
            "observaciones": "Control en dos semanas.",
            "peso_actual": "4.2",
            "vacuna_nombre": "",
            "vacuna_proxima": "",
            "tratamiento_nombre": "Apoquel",
            "medicamento": "Apoquel 16 mg",
            "dosis": "1 comprimido",
            "frecuencia": "Cada 24 horas",
            "fecha_fin_tratamiento": "2026-05-15",
        }
        payload.update(overrides)
        return payload

    def test_usuario_puede_registrar_tratamiento_para_mascota_propia(self):
        response = self.client.post(
            reverse("registros_medicos"),
            self.get_valid_payload(),
            follow=True,
        )

        self.assertEqual(Tratamiento.objects.count(), 1)
        tratamiento = Tratamiento.objects.get()
        self.assertEqual(tratamiento.nombre_tratamiento, "Apoquel")
        self.assertEqual(tratamiento.atencion_medica.mascota, self.mascota)

        mensajes = list(response.context["messages"])
        self.assertTrue(any("Registro médico guardado para" in str(m) for m in mensajes))

    def test_post_invalido_no_guarda_registro_medico_ni_tratamiento(self):
        response = self.client.post(
            reverse("registros_medicos"),
            self.get_valid_payload(fecha_atencion="", tipo_atencion=""),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(AtencionMedica.objects.count(), 0)
        self.assertEqual(Tratamiento.objects.count(), 0)
        self.assertIn("fecha_atencion", response.context["form"].errors)
        self.assertIn("tipo_atencion", response.context["form"].errors)

    def test_listado_tratamientos_muestra_informacion_basica(self):
        atencion = AtencionMedica.objects.create(
            mascota=self.mascota,
            fecha_atencion="2026-05-05",
            tipo_atencion="Consulta general",
            tratamiento_indicado="Aplicar medicamento por 10 dias.",
        )
        Tratamiento.objects.create(
            nombre_tratamiento="Apoquel",
            descripcion="Aplicar medicamento por 10 dias.",
            medicamento="Apoquel 16 mg",
            frecuencia="Cada 24 horas",
            fecha_inicio="2026-05-05",
            atencion_medica=atencion,
        )

        response = self.client.get(f"{reverse('registros_medicos')}?pet={self.mascota.id}")

        self.assertEqual(response.status_code, 200)
        tratamientos = response.context["tratamientos_activos"]
        self.assertEqual(len(tratamientos), 1)
        self.assertEqual(tratamientos[0].nombre_tratamiento, "Apoquel")
        self.assertEqual(tratamientos[0].medicamento, "Apoquel 16 mg")
        self.assertEqual(tratamientos[0].frecuencia, "Cada 24 horas")

    def test_listado_tratamientos_vacio_entrega_contexto_sin_registros(self):
        response = self.client.get(f"{reverse('registros_medicos')}?pet={self.mascota.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["tratamientos_activos"], [])
        self.assertEqual(response.context["timeline"], [])

    def test_usuario_puede_ver_detalle_de_tratamiento_propio(self):
        atencion = AtencionMedica.objects.create(
            mascota=self.mascota,
            fecha_atencion="2026-05-05",
            tipo_atencion="Consulta general",
            tratamiento_indicado="Aplicar medicamento por 10 dias.",
        )
        tratamiento = Tratamiento.objects.create(
            nombre_tratamiento="Apoquel",
            descripcion="Aplicar medicamento por 10 dias.",
            medicamento="Apoquel 16 mg",
            frecuencia="Cada 24 horas",
            fecha_inicio="2026-05-05",
            atencion_medica=atencion,
        )

        response = self.client.get(reverse("detalle_tratamiento", args=[tratamiento.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["tratamiento"], tratamiento)
        self.assertContains(response, "Apoquel")

    def test_usuario_no_puede_ver_tratamiento_ajeno(self):
        atencion_ajena = AtencionMedica.objects.create(
            mascota=self.mascota_ajena,
            fecha_atencion="2026-05-05",
            tipo_atencion="Consulta general",
        )
        tratamiento_ajeno = Tratamiento.objects.create(
            nombre_tratamiento="Otico",
            fecha_inicio="2026-05-05",
            atencion_medica=atencion_ajena,
        )

        response = self.client.get(
            reverse("detalle_tratamiento", args=[tratamiento_ajeno.id])
        )

        self.assertEqual(response.status_code, 404)
