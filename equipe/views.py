from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db.models.deletion import Collector, ProtectedError
from django.db import router
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
    

class ListarEquipes(generic.ListView):
    model = Equipe
    template_name = 'listagem_equipes.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)

        equipes_participante = MembroEquipe.objects.filter(membro=self.request.user).values_list('equipe', flat=True)
        equipes_usuario = Equipe.objects.filter(id__in=equipes_participante)

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

        id_participantes = MembroEquipe.objects.filter(equipe=equipe).values_list('membro', flat=True)
        participantes = Usuario.objects.filter(id__in=id_participantes).values_list('username', flat=True)

        dados = {
            'Nome': equipe.nome,
            'Descrição': equipe.descricao,
            'Criador da Equipe': equipe.criada_por,
            'Responsável pela Equipe': equipe.responsavel,
        }

        dados['Participantes da Equipe'] = ', '.join(participantes)

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
                    'url': 'listagem_equipes',
                    'nome': 'Adicionar Participantes',
                    'classe': 'adicionar-botao'
                },
                {
                    'url': 'excluir_equipe',
                    'nome': 'Excluir Equipe',
                    'classe': 'excluir-botao',
                    'id_item': equipe.pk
                },
                {
                    'url': 'listagem_equipes',
                    'nome': 'Editar',
                    'classe': 'visualizar-editar-botao'
                }
            ]
        })

        return contexto
    
class ExcluirEquipe(generic.DeleteView):
    model = Equipe
    template_name = 'excluir_equipe.html'
    success_url = 'listagem_equipes'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        equipe = self.get_object()
        
        id_participantes = MembroEquipe.objects.filter(equipe=equipe).values_list('membro', flat=True)

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
            'Participantes da Equipe': ', '.join(Usuario.objects.filter(id__in=id_participantes).values_list('username', flat=True))
        }

        contexto.update({
            'titulo': f'Confirmação de Exclusão da Equipe: {equipe.pk}',
            'titulo_confirmacao': 'Serão apagados também, os seguintes itens:',
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

            'botoes': [
                {
                    'url': 'visualizar_equipe',
                    'id_item': equipe.pk,
                    'classe': 'visualizar-editar-botao',
                    'nome': 'Voltar'
                },
                {
                    'url': 'listagem_equipes',
                    'classe': 'adicionar-botao',
                    'nome': 'Remover todos os membros'
                }
            ]
        })

        return contexto
    
    def post(self, request, *args, **kwargs):
        equipe = self.get_object()

        try:
            return super().post(request, *args, **kwargs)
        
        except ProtectedError:
            messages.error(request, 'Não é possível excluir esta equipe porque ainda existem membros ou tarefas vinculadas.')
            return redirect('visualizar_equipe', equipe.pk)