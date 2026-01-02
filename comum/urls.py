from django.urls import path
from comum.views import login_usuario, cadastrar_usuario, logout_usuario, vincular_responsaveis, api_dashboard, exibir_dashboard


urlpatterns = [
    path('', login_usuario, name='login_usuario'),
    path('cadastro/', cadastrar_usuario, name='cadastro_usuario'),
    path('logout/', logout_usuario, name='logout_usuario'),

    path('vincular_responsaveis_tarefa/<int:pk>', vincular_responsaveis, name='vincular_responsaveis_tarefa'),
    path('api_dashboard', api_dashboard, name='dashboard'),
    path('dashboard', exibir_dashboard, name='exibir_dashboard')
]