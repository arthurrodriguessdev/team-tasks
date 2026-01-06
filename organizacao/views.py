from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from organizacao.forms import OrganizacaoForm
from organizacao.models import MembroOrganizacao, Organizacao

# TO DO: Verificar regra se um usuário pode criar mais de uma organização
@login_required
def criar_organizacao(request):
    if request.method == 'POST':
        form = OrganizacaoForm(request.POST)

        if form.is_valid():
            organizacao = form.save()
            MembroOrganizacao.objects.create(
                organizacao=organizacao,
                membro=request.user,
                papel='proprietario'
            )
            
            messages.success(request, 'Organização criada com sucesso.')
            return redirect('exibir_dashboard')
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

@login_required
def visualizar_organizacao(request):
    organizacao = MembroOrganizacao.get_organizacao_do_proprietario(request.user)

    if organizacao is None:
        messages.error(request, 'Organização não encontrada')
        return redirect('exibir_dashboard')
    
    # TO DO: Template separado para participantes
    
    # lista_membros = []
    # membros = MembroOrganizacao.get_membros_organizacao(organizacao)

    # for membro in membros:
    #     lista_membros.append(f'{membro.membro.nome} ({membro.membro.username})')

    # membros = ', '.join(lista_membros)
    dados = {
        'Nome da Organização': organizacao.nome,
        'Plano da Organização': organizacao.plano.capitalize(),
        'Proprietário': request.user.get_nome,
        'Criada em': organizacao.criada_em,
        'Quantidade de Membros': MembroOrganizacao.get_quantidade_membros(organizacao),
    }

    contexto = {
        'titulo': f'Detalhes da Organização:',
        'titulo_visualizar': 'Dados da Organização',
        'dados': dados,
        'organizacao': organizacao,
        'botoes': [
            {
                'nome': 'Voltar',
                'classe': 'visualizar-editar-botao',
                'url': 'exibir_dashboard'
            },
            {
                'nome': 'Convidar Participantes',
                'classe': 'adicionar-botao',
                'url': 'exibir_dashboard'
            }
        ]
    }
    return render(request, 'visualizar_organizacao.html', contexto)