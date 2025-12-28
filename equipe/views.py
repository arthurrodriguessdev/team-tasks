from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from equipe.models import Equipe
from equipe.forms import EquipeForm
from comum.models import MembroEquipe


class CriarEquipe(generic.CreateView):
    model = Equipe
    template_name = 'adicionar_equipe.html'
    form_class = EquipeForm
    success_url = reverse_lazy('listagem_tarefas')


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
                'titulo_formulario': 'Dado da Equipe',
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
        equipes_usuario = MembroEquipe.objects.filter(membro=self.request.user).values_list('equipe', flat=True)

        contexto.update({
            'cabecalhos': ['Nome da Equipe'],
            'equipes': Equipe.objects.filter(id__in=equipes_usuario)
        })

        return contexto