# Pet Care Connect

Proyecto web desarrollado con Django para la gestión de mascotas, registros médicos, citas, tratamientos, alimentación y búsqueda de veterinarias cercanas.

## Tecnologías utilizadas

- Python 3
- Django 6
- MySQL
- HTML, CSS y JavaScript
- Leaflet
- xhtml2pdf

## Funcionalidades principales

- Registro e inicio de sesión con usuario personalizado
- Gestión de mascotas
- Registro de atenciones médicas, vacunas y tratamientos
- Agenda de citas veterinarias
- Registro de dieta y alimentación
- Descarga de ficha médica en PDF
- Vista de veterinarias cercanas en mapa

## Estructura del proyecto

El proyecto está organizado en las siguientes apps:

- `usuarios`: `Rol`, `Usuario`, `Veterinaria`
- `mascotas`: `Mascota`, `Alimentacion`, `Vacuna`, `Recordatorio`
- `citas`: `Cita`, `AtencionMedica`
- `tratamientos`: `Tratamiento`

Los roles iniciales (`Admin`, `Veterinario`, `Cliente`) se cargan automáticamente mediante migraciones.

## Requisitos

- Python 3.x
- MySQL instalado y en ejecución
- Un entorno virtual recomendado

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU-USUARIO/pet-care-connect.git
cd pet-care-connect
```

### 2. Cambiar a la rama de trabajo

Este proyecto utiliza `develop` como rama principal de trabajo.

```bash
git fetch origin
git checkout develop
```

Si no tienes la rama local:

```bash
git checkout -b develop origin/develop
```

### 3. Crear y activar entorno virtual

```bash
python -m venv venv
```

Windows PowerShell:

```bash
venv\Scripts\Activate.ps1
```

Windows CMD:

```bash
venv\Scripts\activate.bat
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

## Configuración de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
DB_NAME=pet_care_connect
DB_USER=petcare_app
DB_PASSWORD=tu_password
```

Este archivo es local y no debe subirse al repositorio.

## Configuración de base de datos

### 1. Crear base de datos y usuario en MySQL

Ejecuta en MySQL:

```sql
CREATE DATABASE pet_care_connect CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'petcare_app'@'localhost' IDENTIFIED BY 'TuPasswordSegura123!';
GRANT ALL PRIVILEGES ON pet_care_connect.* TO 'petcare_app'@'localhost';
FLUSH PRIVILEGES;
```

El usuario y la contraseña deben coincidir con los valores definidos en `.env`.

### 2. Aplicar migraciones

Una vez configurado MySQL y creado el archivo `.env`, ejecuta:

```bash
python manage.py migrate
```

Este paso crea toda la estructura de tablas del proyecto.

### 3. Crear superusuario opcional

```bash
python manage.py createsuperuser
```

## Levantar el servidor

```bash
python manage.py runserver
```

Luego abre:

```text
http://127.0.0.1:8000/
```

## Rutas y módulos destacados

- `/` : portada pública
- `/panel-control/` : panel principal del usuario autenticado
- `/mis_mascotas/` : listado de mascotas del usuario
- `/registros-medicos/` : historial médico
- `/mascota/<id>/pdf/` : descarga de ficha médica en PDF
- `/dieta/` : seguimiento de alimentación
- `/veterinarias-cercanas/` : mapa de veterinarias para usuarios logueados
- `/api/veterinarias/` : endpoint JSON con veterinarias registradas

## Documentación de base de datos

En `docs/db/` se conservan archivos referenciales del diseño original:

- `create-bd.sql`
- `db-diagram.png`

Sirven como apoyo documental, pero la estructura vigente del proyecto se gestiona mediante modelos y migraciones de Django.

## Buenas prácticas del equipo

- No trabajar en `main`
- Trabajar siempre en `develop`
- Crear ramas desde `develop` para nuevas funcionalidades
- Hacer commits frecuentes y descriptivos

Ejemplo:

```bash
git checkout -b feature/registro-usuario
```

## Notas

- Activa siempre el entorno virtual antes de trabajar.
- No subas `venv/` ni `.env` al repositorio.
- Si agregas nuevas librerías, actualiza `requirements.txt`.
- Si aparece un error como `Table '...usuarios_veterinaria' doesn't exist`, probablemente faltan migraciones por aplicar.

## Equipo

- Katherine Ferreira
- Gerko Berrios
- Julian Soberon