from django.urls import path
from equipe import views

urlpatterns = [
    path('adicionar_equipe/', views.CriarEquipe.as_view(), name='adicionar_equipe'),
    path('minhas_equipes/', views.ListarEquipes.as_view(), name='listagem_equipes'),
    path('visualizar_equipe/<int:pk>', views.VisualizarEquipe.as_view(), name='visualizar_equipe'),
    path('excluir_equipe/<int:pk>', views.ExcluirEquipe.as_view(), name='excluir_equipe'),
]