from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def agregar_mascota(request):
    return render(request, 'mascota_add.html')

def mis_mascotas(request):
    return render(request, 'mis_mascotas.html')

def citas(request):
    return render(request, 'citas.html')

def registros_medicos(request):
    return render(request, 'registros_medicos.html')

def dieta(request):
    return render(request, 'dieta.html')

def panel_control(request):
    return render(request, 'panel_control.html')