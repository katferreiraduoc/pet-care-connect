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

## Migraciones

```bash
python manage.py migrate
```

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

```
pet-care-connect/
│
├── petcare/
├── manage.py
├── venv/
└── README.md
```

---

## 💡 Notas

* Asegúrate de tener Python instalado
* Activar siempre el entorno virtual antes de trabajar
* No subir la carpeta `venv/` al repositorio (ya incluido en gitignore)

---

## 👩‍💻 Equipo

* Katherine Ferreira
* Gerko Berrios
* Julian Soberon
