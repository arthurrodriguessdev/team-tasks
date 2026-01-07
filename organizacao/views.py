from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from organizacao.forms import OrganizacaoForm
from organizacao.models import MembroOrganizacao, Organizacao, ConviteOrganizacao
from organizacao.utils import apagar_objeto
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
            ConviteOrganizacao.objects.create(
                usuario_convidado=usuario,
                organizacao=organizacao,
                enviado_por=request.user
            )
            
            contexto['usuario'] = usuario
            contexto['enviou_convite'] = 1

    return render(request, 'convidar_participantes.html', contexto)

def aceitar_convite(request, pk):
    convite = get_object_or_404(ConviteOrganizacao, pk=pk)
    MembroOrganizacao.objects.create(
        organizacao=convite.organizacao,
        membro=request.user,
        papel='membro'
    )

    apagar_objeto(convite)
    return redirect('exibir_dashboard')

def recusar_convite(request, pk):
    convite = get_object_or_404(ConviteOrganizacao, pk=pk)
    apagar_objeto(convite)

    return redirect('onboarding')

def visualizar_convite(request, pk):
    convite = get_object_or_404(ConviteOrganizacao, pk=pk)
    
    dados = {
        'Nome': convite.organizacao,
        'Convidado por': convite.enviado_por,
        'Data de convite': convite.criado_em
    }

    contexto = {
        'titulo': f'Detalhes da Organização:',
        'titulo_visualizar': 'Dados da Organização',
        'dados': dados,
        'botoes_inferiores':[
            {
                'nome': 'Recusar Convite',
                'classe': 'excluir-botao',
                'url': 'recusar_convite',
                'id_nome': 'botao_recusar',
                'id_item': convite.pk
            },

            {
                'nome': 'Aceitar Convite',
                'classe': 'adicionar-botao',
                'url': 'aceitar_convite',
                'id_nome': 'botao_aceitar',
                'id_item': convite.pk
            }
        ],

        'botoes': [
            {
                'nome': 'Voltar',
                'classe': 'visualizar-editar-botao',
                'url': 'meus_convites'
            },
        ]
    }
    return render(request, 'visualizar_convite.html', contexto)