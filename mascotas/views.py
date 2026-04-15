from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def agregar_mascota(request):
    return render(request, 'mascota_add.html')