from django.urls import path
from organizacao.views import criar_organizacao, visualizar_organizacao, convidar_participantes


urlpatterns = [
    path('criar_organizacao/', criar_organizacao, name='criar_organizacao'),
    path('visualizar_organizacao', visualizar_organizacao, name='visualizar_organizacao'),
    path('convidar_participantes/<int:pk>', convidar_participantes, name='convidar_participantes')
]