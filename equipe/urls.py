from django.urls import path
from equipe import views

urlpatterns = [
    path('adicionar_equipe/', views.CriarEquipe.as_view(), name='adicionar_equipe'),
    path('minhas_equipes/', views.ListarEquipes.as_view(), name='listagem_equipes'),
    path('visualizar_equipe/<int:pk>', views.VisualizarEquipe.as_view(), name='visualizar_equipe'),
    path('excluir_equipe/<int:pk>', views.ExcluirEquipe.as_view(), name='excluir_equipe'),
    path('editar_equipe/<int:pk>', views.EditarEquipe.as_view(), name='editar_equipe'),

    path('excluir_membros/<int:pk>', views.remover_todos_membros, name='remover_todos_membros'),
    path('excluir_tarefas/<int:pk>', views.remover_todas_tarefas_equipe, name='remover_todas_tarefas_equipe'),
    path('adicionar_participantes/<int:pk>', views.adicionar_participantes, name='adicionar_participantes')
]