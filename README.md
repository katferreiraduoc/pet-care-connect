# 🐾 Pet Care Connect

Proyecto web desarrollado con Django para la gestión de mascotas, citas veterinarias, tratamientos y alimentación.

---

## Tecnologías utilizadas

* Python 3.x
* Django
* Git & GitHub
* MySQL

---

## Clonar el repositorio

```bash
git clone https://github.com/TU-USUARIO/pet-care-connect.git
cd pet-care-connect
```

---

## Trabajar en la rama develop (IMPORTANTE)

Este proyecto utiliza la rama **develop** como rama principal de trabajo.

```bash
git fetch origin
git checkout develop
```

Si no tienes la rama local:

```bash
git checkout -b develop origin/develop
```

---

## Crear entorno virtual

```bash
python -m venv venv
```

### Activar entorno virtual

**Windows (PowerShell):**

```bash
venv\Scripts\Activate.ps1
```

**Windows (CMD):**

```bash
venv\Scripts\activate.bat
```

---

## 📦 Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 🔐 Variables de entorno

Crear un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
DB_NAME=pet_care_connect
DB_USER=petcare_app
DB_PASSWORD=tu_password
```

Este archivo es local y no debe subirse al repositorio.

Asegúrate de que `.env` esté incluido en `.gitignore`.

---

## 🗄️ Configuración de base de datos (MySQL)

### 1. Crear usuario de base de datos

Ejecutar en MySQL:

```sql
CREATE USER 'petcare_app'@'localhost' IDENTIFIED BY 'TuPasswordSegura123!';
GRANT ALL PRIVILEGES ON pet_care_connect.* TO 'petcare_app'@'localhost';
FLUSH PRIVILEGES;
```

El usuario y la contraseña deben coincidir con los valores configurados en el archivo `.env`.

### 2. Configurar conexión en Django

Editar el archivo:

```text
petcare/settings.py
```

Y usar la configuración de base de datos con variables de entorno:

```python
from decouple import config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}
```

### 3. Crear estructura de base de datos con Django

Una vez configurada la conexión a MySQL y creado el archivo `.env`, ejecutar:

```bash
python manage.py migrate
```

Si todo está correcto, Django aplicará las migraciones y creará la estructura necesaria en la base de datos.

---

## 🧩 Modelo de datos actual

El proyecto está organizado en las siguientes apps:

* **usuarios**: Rol, Usuario
* **mascotas**: Mascota, Alimentacion, Vacuna, Recordatorio
* **citas**: Cita, AtencionMedica
* **tratamientos**: Tratamiento

Los roles iniciales (`Admin`, `Veterinario`, `Cliente`) se cargan automáticamente mediante migraciones.

---

## 📄 Documentación de base de datos

En la carpeta `docs/db/` se conservan archivos referenciales del diseño original:

* `create-bd.sql`
* `db-diagram.png`

Estos archivos sirven como apoyo documental del MER, pero la estructura actual del proyecto se gestiona mediante modelos y migraciones de Django.

---

## Levantar el servidor

```bash
python manage.py runserver
```

Abrir en navegador:

👉 http://127.0.0.1:8000/

---

## Buenas prácticas del equipo

* ❗ **NO trabajar en main**
* ✅ Trabajar siempre en `develop`
* 🔄 Crear ramas desde `develop` para nuevas funcionalidades
* 💾 Hacer commits frecuentes y descriptivos

Ejemplo:

```bash
git checkout -b feature/registro-usuario
```

---

## 📁 Estructura del proyecto

```text
pet-care-connect/
│
├── docs/
│   └── db/
│       ├── create-bd.sql
│       └── db-diagram.png
├── usuarios/
├── mascotas/
├── citas/
├── tratamientos/
├── petcare/
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 💡 Notas

* Asegúrate de tener Python y MySQL instalados
* Activar siempre el entorno virtual antes de trabajar
* No subir la carpeta `venv/` al repositorio
* No subir el archivo `.env` al repositorio
* Si agregas nuevas librerías, actualizar:

```bash
pip freeze > requirements.txt
```

---

## 👩‍💻 Equipo

* Katherine Ferreira
* Gerko Berrios
* Julian Soberon
