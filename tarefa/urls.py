from django.urls import path
from tarefa.views import criar_tarefa, listar_tarefas, visualizar_tarefa, excluir_tarefa, editar_tarefa


urlpatterns = [
    path('minhas_tarefas/', listar_tarefas, name='listagem_tarefas'),
    path('adicionar_tarefa/', criar_tarefa, name='adicionar_tarefa'),
    path('visualizar_tarefa/<int:pk>', visualizar_tarefa, name='visualizar_tarefa'),
    path('excluir_tarefa/<int:pk>', excluir_tarefa, name='excluir_tarefa'),
    path('editar_tarefa/<int:pk>', editar_tarefa, name='editar_tarefa')
]