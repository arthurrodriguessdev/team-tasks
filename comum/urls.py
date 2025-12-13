from django.urls import path
from comum.views import login_usuario, registrar_usuario


urlpatterns = [
    path('login', login_usuario, name='login_usuario'),
    path('cadastro', registrar_usuario, name='registrar_usuario')
]