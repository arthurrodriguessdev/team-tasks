from django.shortcuts import render, redirect
from django.contrib import messages
from tarefa.models import Tarefa
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from tarefa.forms import TarefaForm
from comum.utils import pesquisar_objetos


@login_required
def criar_tarefa(request):
    if request.method == 'POST':
        form = TarefaForm(request.POST, request=request)

        if form.is_valid():
            form.full_clean()
            form.save()

            messages.success(request, 'Tarefa criada com sucesso.')
            return redirect('listagem_tarefas')

    form = TarefaForm(request=request)
    contexto = {
        'titulo': 'Cadastrar Tarefa',
        'botoes': [
            {'url': 'listagem_tarefas',
             'classe': 'visualizar-editar-botao',
             'nome': 'Voltar'
            },
        ],
        
        'url_view': 'adicionar_tarefa',
        'form': form,
        'titulo_formulario': 'Dados da Tarefa',
        'titulo_botao_form': 'Cadastrar'
    }

    return render(request, 'adicionar_tarefa.html', contexto)

@login_required
def listar_tarefas(request):
    tarefas = Tarefa.objects.filter(Q(criada_por=request.user.pk)) #TO DO: Adicionar filtros do request.user como PARTICIPANTE também

    tarefas = pesquisar_objetos(request.GET.get('q'), tarefas, ['titulo', 'descricao'])

    cabecalhos_tabela = ['Título', 'Equipe', 'Prazo', 'Status']
    contexto = {
        'titulo': 'Minhas Tarefas',
        'tarefas': tarefas,
        'cabecalhos': cabecalhos_tabela,
        'url_pesquisa': 'listagem_tarefas',
        'botoes': [
            {'url': 'adicionar_tarefa',
             'classe': 'adicionar-botao',
             'nome': 'Adicionar Tarefa'
            },
        ]
    }

    return render(request, 'listagem_tarefas.html', contexto)