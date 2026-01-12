from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Case, When
from django.contrib import messages
from tarefa.models import Tarefa
from django.db import router
from django.db.models import Q
from django.db.models.deletion import Collector
from django.contrib.auth.decorators import login_required
from tarefa.forms import TarefaForm
from comum.utils import pesquisar_objetos
from comum.models import Usuario, MembroEquipe
from equipe.models import Equipe

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
    equipes_usuario = MembroEquipe.get_equipe_usuario(request.user)

    tarefas = Tarefa.objects.filter(equipe__in=equipes_usuario).distinct()
    tarefas = pesquisar_objetos(request.GET.get('q'), tarefas, ['titulo', 'descricao'])

    tarefas_responsavel = Tarefa.objects.filter(responsaveis=request.user)
    tarefas = tarefas.annotate(
        atribuida_a_mim=Case(
            When(id__in=tarefas_responsavel, then=True),
            default=False
        )
    )

    cabecalhos_tabela = ['Título', 'Equipe', 'Prazo', 'Status', 'Relação']
    contexto = {
        'titulo': 'Tarefas das Equipes',
        'tarefas': tarefas,
        'cabecalhos': cabecalhos_tabela,
        'url_pesquisa': 'listagem_tarefas',
        'botoes': []
    }

    if Equipe.eh_responsavel_equipe(request.user):
        contexto['botoes'].append({
            'url': 'adicionar_tarefa',
            'classe': 'adicionar-botao',
            'nome': 'Adicionar Tarefa'
        })

    return render(request, 'listagem_tarefas.html', contexto)

@login_required
def listar_minhas_tarefas(request):
    tarefas = Tarefa.objects.filter(Q(responsaveis=request.user.pk)).distinct()
    tarefas = pesquisar_objetos(request.GET.get('q'), tarefas, ['titulo', 'descricao'])

    cabecalhos_tabela = ['Título', 'Equipe', 'Prazo', 'Status', 'Relação']
    contexto = {
        'titulo': 'Minhas Tarefas',
        'tarefas': tarefas,
        'cabecalhos': cabecalhos_tabela,
        'url_pesquisa': 'listagem_tarefas',
        'botoes': []
    }

    return render(request, 'listagem_minhas_tarefas.html', contexto)

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
                'url': 'listagem_tarefas',
                'nome': 'Voltar',
                'classe': 'visualizar-editar-botao'
            },
        ]
    }

    if tarefa:
        dados.update(
            {
                'Tarefa da Equipe': tarefa.equipe, 
                'Responsáveis pela Tarefa': 'Não há responsáveis atribuídos para essa tarefa'
            }
        )

        if tarefa.equipe:
            if tarefa.responsaveis.exists():
                responsaveis = tarefa.responsaveis.values_list('username', flat=True)
                dados['Responsáveis pela Tarefa'] = ', '.join(responsaveis)

            # Responsável pela equipe pode vincular responsáveis (atribuir tarefa)
            if tarefa.equipe.responsavel == request.user:
                contexto['botoes'].insert(0,{
                    'url': 'vincular_responsaveis_tarefa',
                    'id_item': tarefa.id,
                    'nome': 'Vincular Responsáveis',
                    'classe': 'adicionar-botao'
                })

                contexto['botoes'].extend([
                    {
                        'url': 'editar_tarefa',
                        'nome': 'Editar',
                        'id_item': tarefa.pk,
                        'classe': 'visualizar-editar-botao'
                    },

                    {   
                        'url': 'excluir_tarefa',
                        'id_item': tarefa.id,
                        'nome': 'Excluir Tarefa',
                        'classe': 'excluir-botao'
                    },
                ])

    return render(request, 'visualizar_tarefas.html', contexto)

@login_required
def excluir_tarefa(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk)

    if request.method == 'POST':
        tarefa.delete()
        messages.success(request, 'A tarefa foi excluída com sucesso.')
        return redirect('listagem_tarefas')
    
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

        if tarefa.responsaveis.exists():
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

        'url': 'excluir_tarefa',
        'id_item': tarefa.pk,
        'dados_afetados': objetos_relacionados,
        'titulo_exibicao_dados': 'Confira os dados da tarefa antes de confirmar a exclusão:',
        'titulo_confirmacao': 'Serão apagados também, os seguintes itens:',
        'titulo_botao_form': 'Confirmar',
        'dados': dados,
        'pode_ter_dados_afetados': 1,
    }

    return render(request, 'excluir_tarefa.html', contexto)

@login_required
def editar_tarefa(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk)

    if request.method == 'POST':
        form = TarefaForm(request.POST, instance=tarefa, request=request)

        if form.is_valid():
            form.full_clean()
            form.save()

            messages.success(request, 'Tarefa atualizada com sucesso.')
            return redirect('listagem_tarefas')
    else:
        form = TarefaForm(instance=tarefa, request=request)

    contexto = {
        'tarefa': tarefa,
        'form': form,

        'titulo': 'Atualizar Tarefa',
        'botoes': [
            {
                'url': 'listagem_tarefas',
                'classe': 'visualizar-editar-botao',
                'nome': 'Voltar'
            },
        ],
        
        'url_view': 'editar_tarefa',
        'id_url': tarefa.pk,
        'titulo_formulario': 'Dados da Tarefa',
        'titulo_botao_form': 'Salvar'
    }

    return render(request, 'editar_tarefa.html', contexto)
