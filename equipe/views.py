from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy, reverse
from django.db.models.deletion import Collector, ProtectedError
from django.db import router
from django.db.models import Q
from django.contrib import messages
from django.views import generic
from equipe.models import Equipe
from equipe.forms import EquipeForm
from comum.models import MembroEquipe, Usuario
from comum.utils import pesquisar_objetos


class CriarEquipe(generic.CreateView):
    model = Equipe
    template_name = 'adicionar_equipe.html'
    form_class = EquipeForm
    success_url = reverse_lazy('listagem_equipes')

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto.update(
            {
                'url_view': 'adicionar_equipe',
                'titulo': 'Cadastrar Equipe',
                'botoes':[
                    {
                        'url': 'listagem_tarefas',
                        'classe': 'visualizar-editar-botao',
                        'nome': 'Voltar'
                    }
                ],
                'titulo_formulario': 'Dados da Equipe',
                'titulo_botao_form': 'Cadastrar'
            }
        )

        return contexto
    
    def form_valid(self, form):
        equipe = form.save(commit=False)

        equipe.criada_por = self.request.user
        equipe.responsavel = self.request.user
        equipe.save()

        MembroEquipe.objects.create(
            equipe=equipe,
            membro=self.request.user
        )

        self.object = Equipe
        return super().form_valid(form)
    
    def post(self, request, *args, **kwargs):
        post = super().post(request, *args, **kwargs)
        messages.success(request, 'Equipe criada com sucesso.')
        return post
    

class ListarEquipes(generic.ListView):
    model = Equipe
    template_name = 'listagem_equipes.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)

        equipes_participante = MembroEquipe.objects.filter(membro=self.request.user).values_list('equipe', flat=True)
        equipes_usuario = Equipe.objects.filter(
            Q(id__in=equipes_participante) | Q(responsavel=self.request.user)
        )

        contexto.update({
            'cabecalhos': ['Nome da Equipe', 'Criador da Equipe'],
            'equipes': pesquisar_objetos(self.request.GET.get('q'), equipes_usuario, ['nome']),
            'titulo': 'Minhas Equipes',
            'botoes':[
                {
                    'url': 'adicionar_equipe',
                    'nome': 'Adicionar Equipe',
                    'classe': 'adicionar-botao'
                }
            ],
            'url_pesquisa': 'listagem_equipes'
        })
        
        return contexto
    

class VisualizarEquipe(generic.DetailView):
    model = Equipe
    template_name = 'visualizar_equipe.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        equipe = self.get_object()

        participantes = MembroEquipe.get_usuarios_membros_equipe(equipe).values_list('username', flat=True)

        dados = {
            'Nome': equipe.nome,
            'Descrição': equipe.descricao,
            'Criador da Equipe': equipe.criada_por,
            'Responsável pela Equipe': equipe.responsavel,
        }

        if participantes:
            dados['Participantes da Equipe'] = ', '.join(participantes)
        else:
            dados['Participantes da Equipe'] = 'A equipe não possui participantes.'

        contexto.update({
            'titulo': 'Detalhes da Equipe',
            'titulo_visualizar': 'Dados da Equipe',
            'dados': dados,
            'botoes':[
                {
                    'url': 'listagem_equipes',
                    'nome': 'Voltar',
                    'classe': 'visualizar-editar-botao'
                },
                {
                    'url': 'adicionar_participantes',
                    'nome': 'Adicionar Participantes',
                    'classe': 'adicionar-botao',
                    'id_item': equipe.pk
                },
                {
                    'url': 'excluir_equipe',
                    'nome': 'Excluir Equipe',
                    'classe': 'excluir-botao',
                    'id_item': equipe.pk
                },
                {
                    'url': 'editar_equipe',
                    'nome': 'Editar',
                    'id_item': equipe.pk,
                    'classe': 'visualizar-editar-botao'
                }
            ]
        })

        return contexto
    
class ExcluirEquipe(generic.DeleteView):
    model = Equipe
    template_name = 'excluir_equipe.html'
    success_url = reverse_lazy('listagem_equipes')

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        equipe = self.get_object()
        
        participantes = MembroEquipe.get_usuarios_membros_equipe(equipe).values_list('username', flat=True)

        membros = equipe.membros_equipe.all()
        tarefas = equipe.tarefa_equipe.filter(equipe__isnull=False)

        objetos_relacionados = []
        if membros.exists():
            objetos_relacionados.append({
                'titulo': 'Membros da equipe',
                'quantidade': membros.count(),
                'objetos': membros
            })

        if tarefas.exists():
            objetos_relacionados.append({
                'titulo': 'Tarefas da equipe',
                'quantidade': tarefas.count(),
                'objetos': tarefas
            })

        dados = {
            'Nome da Equipe': equipe.nome,
            'Responsável pela Equipe': equipe.responsavel,
            'Equipe criada por': equipe.criada_por,
        }

        if participantes:
            dados.update({
                'Participantes da Equipe': ', '.join(participantes)
            })

        else:
            dados.update({
                'Participantes da Equipe': 'A equipe não possui participantes.'
            })

        contexto.update({
            'titulo': f'Confirmação de Exclusão da Equipe: {equipe.pk}',
            'titulo_confirmacao': 'Para excluir a equipe, exclua primeiro os seguintes itens:',
            'dados': dados,
            'titulo_exibicao_dados': 'Confira os dados da equipe antes de confirmar a exclusão:',
            'titulo_botao_form': 'Confirmar',
            'dados_afetados': objetos_relacionados,
            'botoes_inferiores':[
                {   
                    'url': 'listagem_equipes',
                    'nome': 'Cancelar',
                    'classe': 'excluir-botao'
                },
            ],

            'url': 'excluir_equipe',
            'id_item': equipe.pk,
            'pode_ter_dados_afetados': 1,
            'botoes': []
        })

        if tarefas:
            contexto['botoes'].append({
                'url': 'remover_todas_tarefas_equipe',
                'id_item': equipe.id,
                'nome': 'Remover todas as tarefas',
                'classe': 'excluir-botao'
            })

        if membros:
            contexto['botoes'].append({
                'url': 'remover_todos_membros',
                'id_item': equipe.id,
                'nome': 'Remover todos membros',
                'classe': 'excluir-botao'
            })

        contexto['botoes'].append({ 
            'url': 'visualizar_equipe',
            'id_item': equipe.pk,
            'classe': 'visualizar-editar-botao',
            'nome': 'Voltar'     
        })

        return contexto
    
    def post(self, request, *args, **kwargs):
        equipe = self.get_object()

        try:
            post = super().post(request, *args, **kwargs)
            messages.success(request, 'Equipe excluída com sucesso.')
            return post
        
        except ProtectedError:
            messages.error(request, 'Não é possível excluir esta equipe porque ainda existem membros ou tarefas vinculadas.')
            return redirect('visualizar_equipe', equipe.pk)
        

class EditarEquipe(generic.UpdateView):
    model = Equipe
    template_name = 'editar_equipe.html'
    success_url = reverse_lazy('listagem_equipes')
    form_class = EquipeForm

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        equipe = self.get_object()

        contexto.update({
            'url_view': 'editar_equipe',
            'id_url': equipe.pk,

            'titulo': 'Atualizar Equipe',
            'botoes': [{
                'url': 'visualizar_equipe',
                'id_item': equipe.pk,
                'classe': 'visualizar-editar-botao',
                'nome': 'Voltar'
            }],

            'titulo_formulario': 'Dados da Equipe',
            'titulo_botao_form': 'Salvar'
        })
        
        return contexto

    def post(self, request, *args, **kwargs):
        post = super().post(request, *args, **kwargs)

        if post:
            messages.success(request, 'A equipe foi atualizada com sucesso.')
        return post
        
def remover_todos_membros(request, pk):
    equipe = get_object_or_404(Equipe, pk=pk)
    membros = equipe.membros_equipe.all()

    if request.method == 'POST':
        membros.delete()
        messages.success(request, 'Todos os membros da equipe foram excluídos.')

        return redirect('visualizar_equipe', equipe.pk)
    
    contexto = {
        'titulo': f'Confirmar exclusão de TODOS os membros da equipe: {equipe.pk}',
        'botoes':[
            {
                'url': 'excluir_equipe',
                'id_item': equipe.pk,
                'classe': 'visualizar-editar-botao',
                'nome': 'Voltar'
            }
        ],

        'url': 'remover_todos_membros',
        'id_item': equipe.pk,
        'titulo_botao_form': 'Confirmar',
        'titulo_exibicao_dados': 'ATENÇÃO:',
        'texto_informativo': f'Após a confirmação serão excluídos TODOS os {membros.count()} membros da equipe. Esta ação não pode ser desfeita.',
        'botoes_inferiores':[
            {
                'url': 'listagem_equipes',
                'classe': 'excluir-botao',
                'nome': 'Cancelar'
            }
        ]
    }
    return render(request, 'excluir_todos_membros.html', contexto)

def remover_todas_tarefas_equipe(request, pk):
    equipe = get_object_or_404(Equipe, pk=pk)
    tarefas_equipe = equipe.tarefa_equipe.all()

    if request.method == 'POST':
        tarefas_equipe.delete()
        messages.success(request, 'Todas as tarefas da equipe foram excluídas.')

        return redirect('visualizar_equipe', equipe.pk)

    contexto = {
        'titulo': f'Confirmar exclusão de TODAS as tarefas vinculadas à equipe: {equipe.pk}',
        'botoes':[
            {
                'url': 'excluir_equipe',
                'id_item': equipe.pk,
                'classe': 'visualizar-editar-botao',
                'nome': 'Voltar'
            }
        ],

        'url': 'remover_todas_tarefas_equipe',
        'id_item': equipe.pk,
        'titulo_botao_form': 'Confirmar',
        'titulo_exibicao_dados': 'ATENÇÃO:',
        'texto_informativo': f'Após a confirmação serão excluídos TODAS as {tarefas_equipe.count()} tarefas vinculadas à esta equipe. Esta ação não pode ser desfeita.',
        'botoes_inferiores':[
            {
                'url': 'listagem_equipes',
                'classe': 'excluir-botao',
                'nome': 'Cancelar'
            }
        ]
    }
    return render(request, 'excluir_todas_tarefas.html', contexto)

def adicionar_participantes(request, pk):
    equipe = get_object_or_404(Equipe, pk=pk)
    usuario = None
    pesquisou = 0

    if request.method == 'POST':
        usuario = Usuario.objects.filter(codigo=request.POST.get('q')).first()
        pesquisou = 1

    contexto = {
        'url_view': 'adicionar_participantes',
        'id_url': equipe.pk,
        'titulo_formulario': 'Adicionar Participantes',
        'url_pesquisa': 'adicionar_participantes',
        'id_url_pesquisa': equipe.pk,
        'usuario': usuario,
        'placeholder': 'Insira o código do usuário',
        'pesquisou': pesquisou
    }

    return render(request, 'adicionar_participantes.html', contexto)