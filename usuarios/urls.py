from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView, home, registro, api_veterinarias

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('registro/', registro, name='registro'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('api/veterinarias/', api_veterinarias, name='api_veterinarias'),
    path('', home, name='home'),
]