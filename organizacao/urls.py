from django.urls import path
from organizacao.views import criar_organizacao, visualizar_organizacao


urlpatterns = [
    path('criar_organizacao/', criar_organizacao, name='criar_organizacao'),
    path('visualizar_organizacao', visualizar_organizacao, name='visualizar_organizacao')
]