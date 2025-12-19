from django.shortcuts import render
from tarefa.models import Tarefa
from django.db.models import Q
from tarefa.forms import TarefaForm

def criar_tarefa(request):
    if request.method == 'POST':
        form = TarefaForm(request.POST, request=request)

        if form.is_valid():
            form.full_clean()
            form.save()

    form = TarefaForm(request=request)
    contexto = {
        'form': form
    }

    return render(request, 'criar_tarefa.html', contexto)

def listar_tarefas(request):
    tarefas = Tarefa.objects.filter(
        Q(criada_por=request.user.pk)
    )

    cabecalhos_tabela = ['Título', 'Descrição', 'Prazo', 'Status']
    contexto = {
        'titulo': 'Minhas Tarefas',
        'tarefas': tarefas,
        'cabecalhos': cabecalhos_tabela,
    }

    return render(request, 'listagem_tarefas.html', contexto)