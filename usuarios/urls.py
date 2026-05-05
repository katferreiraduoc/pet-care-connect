from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import CustomLoginView, api_veterinarias, perfil, registro,configuracion

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("registro/", registro, name="registro"),
    path("perfil/", perfil, name="perfil"),
    path("logout/", LogoutView.as_view(next_page="home"), name="logout"),
    path("api/veterinarias/", api_veterinarias, name="api_veterinarias"),
    path('configuracion/', configuracion, name='configuracion'),
    
]
