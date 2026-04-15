
from django.contrib import admin
from django.urls import path

from mascotas.views import home, agregar_mascota

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('agregar-mascota/', agregar_mascota, name='agregar_mascota')
    
]
