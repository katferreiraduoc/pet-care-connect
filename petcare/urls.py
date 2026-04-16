
from django.contrib import admin
from django.urls import path

from mascotas.views import dieta, home, agregar_mascota, mis_mascotas, citas, panel_control, registros_medicos

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('agregar-mascota/', agregar_mascota, name='agregar_mascota'),
    path('mis_mascotas/', mis_mascotas, name='mis_mascotas'),
    path('citas/', citas, name='citas'),
    path('registros-medicos/', registros_medicos, name='registros_medicos'),
    path('dieta/', dieta, name='dieta'),
    path('panel-control/', panel_control, name='panel_control'),        
]


