from django.urls import path
from organizacao.views import criar_organizacao


urlpatterns = [
    path('criar_organizacao/', criar_organizacao, name='criar_organizacao')
]