from django.shortcuts import render
from tarefa.models import Tarefa
from django.db.models import Q

def criar_tarefa(request):
    if request.method == 'POST':
        ...

    return render(request, 'criar_tarefa.html')

def listar_tarefas(request):
    tarefas = Tarefa.objects.filter(
        Q(criada_por=request.user.pk)
    )

    contexto = {
        'tarefas': tarefas
    }

    return render(request, 'listagem_tarefas.html', contexto)