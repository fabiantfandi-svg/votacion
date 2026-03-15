from django.urls import path
from .views_auth import RegistroAPIView, LoginApiView
from .views_perfil import PerfilImagenAPIView
from .views import VotacionAPIView 

urlpatterns = [
    path('auth/registro/', RegistroAPIView.as_view(), name="api_registro"),
    path('auth/login/', LoginApiView.as_view(), name="api_login"),
    path('votos/', VotacionAPIView.as_view(), name="api_votos"),
    path('perfil/foto/', PerfilImagenAPIView.as_view(), name="api_perfil_foto"),
]