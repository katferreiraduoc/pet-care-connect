from django.contrib.auth.views import LoginView
from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'home.html')

class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'
