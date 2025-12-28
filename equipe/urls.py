from django.urls import path
from equipe import views

urlpatterns = [
    path('adicionar_equipe/', views.CriarEquipe.as_view(), name='adicionar_equipe'),
    path('minhas_equipes/', views.ListarEquipes.as_view(), name='listagem_equipes')
]