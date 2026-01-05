from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from organizacao.forms import OrganizacaoForm
from organizacao.models import MembroOrganizacao

# TO DO: Verificar regra se um usuário pode criar mais de uma organização
@login_required
def criar_organizacao(request):
    if request.method == 'POST':
        form = OrganizacaoForm(request.POST)

        if form.is_valid():
            organizacao = form.save()
            MembroOrganizacao.objects.create(
                organizacao=organizacao,
                membro=request.user
            )
            
            messages.success(request, 'Organização criada com sucesso.')
            return redirect('listagem_tarefas')
    else:
        form = OrganizacaoForm()
    
    contexto = {
        'form': form,
        'titulo_formulario': 'Dados da Organização',
        'titulo_botao_form': 'Cadastrar',
        'titulo': 'Cadastrar Organização',
        'url_view': 'criar_organizacao',
        'botoes': [
            {
                'nome': 'Voltar',
                'url': 'onboarding',
                'classe': 'visualizar-editar-botao'
            }
        ]
    }

    return render(request, 'criar_organizacao.html', contexto)