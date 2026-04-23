from django.test import TestCase
from django.urls import reverse

from .models import Usuario


class RegistroUsuarioTests(TestCase):
    def get_valid_payload(self, **overrides):
        payload = {
            "first_name": "Kathy",
            "last_name": "Gonzalez",
            "username": "kathy.petlover",
            "email": "kathy@example.com",
            "telefono": "+56 9 1234 5678",
            "password1": "ClaveSegura123!",
            "password2": "ClaveSegura123!",
        }
        payload.update(overrides)
        return payload

    def test_formulario_registro_esta_disponible(self):
        response = self.client.get(reverse("registro"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Crear cuenta")
        self.assertContains(response, 'type="email"', html=False)
        self.assertContains(response, 'id="togglePasswords"', html=False)

    def test_registro_exitoso_crea_usuario_y_redirige_al_login(self):
        response = self.client.post(
            reverse("registro"),
            self.get_valid_payload(),
            follow=True,
        )

        self.assertRedirects(response, reverse("login"))
        self.assertEqual(Usuario.objects.count(), 1)

        mensajes = list(response.context["messages"])
        self.assertTrue(any("Cuenta creada correctamente" in str(m) for m in mensajes))

        usuario = Usuario.objects.get(username="kathy.petlover")
        self.assertEqual(usuario.first_name, "Kathy")
        self.assertEqual(usuario.last_name, "Gonzalez")
        self.assertEqual(usuario.email, "kathy@example.com")
        self.assertEqual(usuario.telefono, "+56 9 1234 5678")

    def test_registro_rechaza_correo_con_formato_invalido(self):
        response = self.client.post(
            reverse("registro"),
            self.get_valid_payload(email="correo-invalido"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Usuario.objects.count(), 0)
        self.assertIn("email", response.context["form"].errors)

    def test_registro_no_permite_username_duplicado(self):
        Usuario.objects.create_user(
            username="kathy.petlover",
            email="ya-existe@example.com",
            password="ClaveSegura123!",
        )

        response = self.client.post(reverse("registro"), self.get_valid_payload())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Usuario.objects.count(), 1)
        self.assertIn("username", response.context["form"].errors)

    def test_registro_no_permite_correo_duplicado(self):
        Usuario.objects.create_user(
            username="usuario-existente",
            email="kathy@example.com",
            password="ClaveSegura123!",
        )

        response = self.client.post(reverse("registro"), self.get_valid_payload())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Usuario.objects.count(), 1)
        self.assertIn("email", response.context["form"].errors)


class InicioSesionTests(TestCase):
    def setUp(self):
        self.password = "ClaveSegura123!"
        self.usuario = Usuario.objects.create_user(
            username="kathy.petlover",
            email="kathy@example.com",
            password=self.password,
            first_name="Kathy",
        )

    def test_formulario_login_esta_disponible(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Accede a tu cuenta")
        self.assertContains(response, 'name="username"', html=False)
        self.assertContains(response, 'type="submit"', html=False)

    def test_login_con_credenciales_validas_redirige_a_mis_mascotas(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": self.usuario.username,
                "password": self.password,
            },
        )

        self.assertRedirects(response, reverse("mis_mascotas"))

    def test_login_con_credenciales_validas_autentica_al_usuario(self):
        self.client.post(
            reverse("login"),
            {
                "username": self.usuario.username,
                "password": self.password,
            },
        )

        response = self.client.get(reverse("mis_mascotas"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.usuario.id)

    def test_login_con_credenciales_invalidas_muestra_error(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": self.usuario.username,
                "password": "ClaveIncorrecta123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].non_field_errors())


class PerfilUsuarioTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="kathy.petlover",
            email="kathy@example.com",
            password="ClaveSegura123!",
            first_name="Kathy",
            last_name="Gonzalez",
            telefono="+56 9 1234 5678",
        )

    def test_perfil_requiere_autenticacion(self):
        response = self.client.get(reverse("perfil"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_perfil_muestra_datos_del_usuario_autenticado(self):
        otro_usuario = Usuario.objects.create_user(
            username="otro.usuario",
            email="otro@example.com",
            password="ClaveSegura123!",
            first_name="Otro",
            last_name="Usuario",
        )
        self.client.force_login(self.usuario)

        response = self.client.get(reverse("perfil"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kathy")
        self.assertContains(response, "Gonzalez")
        self.assertContains(response, "kathy@example.com")
        self.assertContains(response, "+56 9 1234 5678")
        self.assertContains(response, "kathy.petlover")
        self.assertNotContains(response, otro_usuario.email)

    def test_menu_incluye_acceso_al_perfil(self):
        self.client.force_login(self.usuario)

        response = self.client.get(reverse("perfil"))

        self.assertContains(response, 'href="/perfil/"', html=False)
        self.assertContains(response, "Perfil")


class CerrarSesionTests(TestCase):
    def setUp(self):
        self.password = "ClaveSegura123!"
        self.usuario = Usuario.objects.create_user(
            username="logout.user",
            email="logout@example.com",
            password=self.password,
            first_name="Kathy",
        )
        self.client.force_login(self.usuario)

    def test_opcion_cerrar_sesion_es_visible_para_usuario_autenticado(self):
        response = self.client.get(reverse("panel_control"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'action="/logout/"', html=False)

    def test_logout_cierra_la_sesion_del_usuario(self):
        response = self.client.post(reverse("logout"))

        self.assertRedirects(response, reverse("home"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_redirige_al_inicio(self):
        response = self.client.post(reverse("logout"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))