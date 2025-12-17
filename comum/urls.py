from django.urls import path
from comum.views import login_usuario, cadastrar_usuario, logout_usuario


urlpatterns = [
    path('', login_usuario, name='login_usuario'),
    path('cadastro/', cadastrar_usuario, name='cadastro_usuario'),
    path('logout/', logout_usuario, name='logout_usuario')
]