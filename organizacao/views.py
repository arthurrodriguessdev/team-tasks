from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from organizacao.forms import OrganizacaoForm
from organizacao.models import MembroOrganizacao, Organizacao
from comum.models import Usuario

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
                'url': 'convidar_participantes',
                'id_item': organizacao.pk
            }
        ]
    }
    return render(request, 'visualizar_organizacao.html', contexto)

def convidar_participantes(request, pk):
    organizacao = get_object_or_404(Organizacao, pk=pk)

    contexto = {
        'url_view': 'convidar_participantes',
        'id_url': organizacao.pk,
        'titulo_formulario': 'Convidar Participantes',
        'url_pesquisa': 'convidar_participantes',
        'id_url_pesquisa': organizacao.pk,
        'usuario': None,
        'placeholder': 'Insira o código do usuário',
        'pesquisou': 0,
        'enviou_convite': 0
    }

    if request.method == 'POST':
        acao = request.POST.get('acao')
        codigo = request.POST.get('q') or request.POST.get('codigo_usuario')

        usuario = Usuario.objects.filter(codigo=codigo).exclude(id=request.user.id).first()

        if acao == 'buscar':
            contexto['usuario'] = usuario
            contexto['pesquisou'] = 1

        if acao == 'convidar' and usuario:
            # MembroEquipe.objects.create(
            #     equipe=equipe,
            #     membro=usuario
            # )

            contexto['usuario'] = usuario
            contexto['enviou_convite'] = 1

    return render(request, 'convidar_participantes.html', contexto)