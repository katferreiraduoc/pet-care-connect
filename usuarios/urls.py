from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import CustomLoginView, api_veterinarias, registro

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("registro/", registro, name="registro"),
    path("logout/", LogoutView.as_view(next_page="home"), name="logout"),
    path("api/veterinarias/", api_veterinarias, name="api_veterinarias"),
]
