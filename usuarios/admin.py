from django.contrib import admin
from .models import Rol, Usuario, Veterinaria


admin.site.unregister(Rol) if admin.site.is_registered(Rol) else None
admin.site.unregister(Usuario) if admin.site.is_registered(Usuario) else None
admin.site.unregister(Veterinaria) if admin.site.is_registered(Veterinaria) else None

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'rol')

@admin.register(Veterinaria)
class VeterinariaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ciudad', 'direccion')