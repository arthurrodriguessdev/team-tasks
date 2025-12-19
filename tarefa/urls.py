from django.urls import path
from tarefa.views import criar_tarefa, listar_tarefas


urlpatterns = [
    path('minhas_tarefas/', listar_tarefas, name='listagem_tarefas'),
    path('adicionar_tarefa/', criar_tarefa, name='adicionar_tarefa')
]