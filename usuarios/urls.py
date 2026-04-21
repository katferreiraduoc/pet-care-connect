from django.urls import path
from django.contrib.auth.views import LogoutView
<<<<<<< HEAD
from .views import CustomLoginView, home, registro, api_veterinarias
=======
from .views import CustomLoginView, registro
>>>>>>> 4bec2ef7f45a15bfdaada642edbd5d4db3eaf35c

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('registro/', registro, name='registro'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
<<<<<<< HEAD
    path('api/veterinarias/', api_veterinarias, name='api_veterinarias'),
    path('', home, name='home'),
]
=======
]
>>>>>>> 4bec2ef7f45a15bfdaada642edbd5d4db3eaf35c
