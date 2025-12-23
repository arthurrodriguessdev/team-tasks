from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from tarefa.models import Tarefa
from django.db import router
from django.db.models import Q
from django.db.models.deletion import Collector
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

@login_required
def visualizar_tarefa(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk)

    dados = {
        'Título': tarefa.titulo,
        'Descrição': tarefa.descricao,
        'Prazo': tarefa.prazo,
    }

    contexto = {
        'titulo': f'Detalhes da Tarefa: {tarefa.pk}',
        'tarefa': tarefa,
        'titulo_visualizar': 'Dados da Tarefa',
        'dados': dados,

        'botoes':[
            {   
                'url': 'excluir_tarefa',
                'id_item': tarefa.id,
                'nome': 'Excluir Tarefa',
                'classe': 'excluir-botao'
            },

            {   
                'url': 'listagem_tarefas',
                'nome': 'Voltar',
                'classe': 'visualizar-editar-botao'
            }
        ]
    }

    if tarefa.em_equipe:
        dados.update(
            {'Tarefa da Equipe': tarefa.equipe, 
             'Responsáveis pela Tarefa': tarefa.responsaveis
            }
        )

        if tarefa.equipe:
            contexto['botoes'].insert(0,{
                'url': 'listagem_tarefas',
                'nome': 'Vincular Responsáveis',
                'classe': 'adicionar-botao'
            })

    return render(request, 'visualizar_tarefas.html', contexto)

def excluir_tarefa(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk)

    collector = Collector(using=router.db_for_write(Tarefa))
    collector.collect([tarefa])
    objetos_relacionados = []

    for model, objetos in collector.data.items():
        if model == Tarefa:
            continue

        if objetos:
            objetos_relacionados.append({
                'titulo': model._meta.verbose_name_plural.capitalize(),
                'quantidade': len(objetos),
                'objetos': list(objetos)
            })

    dados = {
        'Título': tarefa.titulo,
        'Descrição': tarefa.descricao,
        'Prazo': tarefa.prazo,
        'Criada por': tarefa.criada_por,
        'Criada em': tarefa.criada_em,
    }

    if tarefa.em_equipe:
        dados.update({'Equipe': tarefa.equipe})

        if tarefa.responsaveis:
            dados.update({'Responsáveis': tarefa.responsaveis})
    
    contexto = {
        'tarefa':tarefa,
        'titulo': f'Confirmação de Exclusão da Tarefa: {tarefa.pk}',
        'botoes':[
            {   
                'url': 'visualizar_tarefa',
                'nome': 'Voltar',
                'classe': 'visualizar-editar-botao',
                'id_item': tarefa.pk
            },
        ],

        'botoes_inferiores':[
            {   
                'url': 'listagem_tarefas',
                'nome': 'Cancelar',
                'classe': 'excluir-botao'
            },
        ],

        'dados_afetados': objetos_relacionados,
        'titulo_exibicao_dados': 'Confira os dados da tarefa antes de confirmar a exclusão:',
        'titulo_confirmacao': 'Serão apagados também, os seguintes itens:',
        'dados': dados
    }

    if request.method == 'GET':
        return render(request, 'excluir_tarefa.html', contexto)
    
    if request.method == 'POST':
        tarefa.delete()
        tarefa.save()

        messages.success(request, 'A tarefa foi excluída com sucesso.')
        return redirect('listagem_tarefas')