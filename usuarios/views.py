from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from .forms import CustomAuthenticationForm, RegistroUsuarioForm

def home(request):
    return render(request, 'home.html')

class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'usuarios/login.html'


def registro(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegistroUsuarioForm()

    return render(request, "usuarios/register.html", {"form": form})
