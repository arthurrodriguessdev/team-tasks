from django.urls import path
from organizacao.views import criar_organizacao, visualizar_organizacao, convidar_participantes, visualizar_convite, aceitar_convite, recusar_convite, adicionar_administradores, listar_participantes


urlpatterns = [
    path('criar_organizacao/', criar_organizacao, name='criar_organizacao'),
    path('visualizar_organizacao', visualizar_organizacao, name='visualizar_organizacao'),
    path('convidar_participantes/<int:pk>', convidar_participantes, name='convidar_participantes'),
    path('visualizar_convite/<int:pk>', visualizar_convite, name='visualizar_convite'),
    path('convite_aceito/<int:pk>', aceitar_convite, name='aceitar_convite'),
    path('convite_recusado/<int:pk>', recusar_convite, name='recusar_convite'),
    path('lista_participantes/<int:pk>', listar_participantes, name='listagem_participantes'),

    path('adicionar_administradores/<int:pk>', adicionar_administradores, name='adicionar_administradores')
]