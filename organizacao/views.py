from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from organizacao.forms import OrganizacaoForm, AdministradoresForm
from organizacao.models import MembroOrganizacao, Organizacao, ConviteOrganizacao
from organizacao.utils import apagar_objeto
from comum.utils import pesquisar_objetos
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
                'url': 'exibir_dashboard_organizacao'
            },
        ]
    }

    if request.user.eh_proprietario_organizacao:
        contexto['botoes'].extend([
            {
                'nome': 'Membros',
                'classe': 'visualizar-editar-botao',
                'url': 'listagem_participantes',
                'id_item': organizacao.pk
            },

            {
                'nome': 'Convidar Participantes',
                'classe': 'adicionar-botao',
                'url': 'convidar_participantes',
                'id_item': organizacao.pk
            },

            {
                'nome': 'Gerenciar Administradores',
                'classe': 'adicionar-botao',
                'url': 'adicionar_administradores',
                'id_item': organizacao.pk
            }
        ])

    return render(request, 'visualizar_organizacao.html', contexto)

def convidar_participantes(request, pk):
    organizacao = get_object_or_404(Organizacao, pk=pk)
    tem_modal = request.session.pop('modal', None)

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

    if tem_modal:
        contexto.update({
            'titulo_modal': tem_modal['titulo'],
            'paragrafo_modal': tem_modal['paragrafo'],
            'mostrar_modal': True
        })

    if request.method == 'POST':
        acao = request.POST.get('acao')
        codigo = request.POST.get('q') or request.POST.get('codigo_usuario')

        usuario = Usuario.objects.filter(codigo=codigo).exclude(id=request.user.id).first()

        if acao == 'buscar':
            contexto['usuario'] = usuario
            contexto['pesquisou'] = 1

        if acao == 'convidar' and usuario:
            if pode_convidar_participantes(organizacao):
                ConviteOrganizacao.objects.create(
                    usuario_convidado=usuario,
                    organizacao=organizacao,
                    enviado_por=request.user
                )
                
                contexto['usuario'] = usuario
                contexto['enviou_convite'] = 1
            else:
                request.session['modal'] = {
                    'titulo': 'Limite do plano atingido.',
                    'paragrafo': 'Seu plano atual não permite convidar mais participantes. Para continuar, faça upgrade do seu plano.'
                }
                
                return redirect('convidar_participantes', pk=organizacao.pk)

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

def adicionar_administradores(request, pk):
    organizacao = get_object_or_404(Organizacao, pk=pk)

    if request.method == 'POST':
        form = AdministradoresForm(request.POST, organizacao=organizacao)

        if form.is_valid():
            membros_selecionados = form.cleaned_data.get('membro')
            MembroOrganizacao.objects.filter(
                organizacao=organizacao,
                membro__in=membros_selecionados
            ).update(papel='administrador')
            
            messages.success(request, 'Administradores atribuídos com sucesso.')
            return redirect('visualizar_organizacao')

    else:
        form = AdministradoresForm(organizacao=organizacao)
    
    contexto = {
        'form': form,
        'url_view': 'adicionar_administradores',
        'id_url': organizacao.pk,
        'titulo_formulario': 'Definir Administradores da Organização',
        'titulo_botao_form': 'Salvar'
    }

    return render(request, 'adicionar_administradores.html', contexto)

def listar_participantes(request, pk):
    organizacao = get_object_or_404(Organizacao, pk=pk)

    membros_organizacao = MembroOrganizacao.objects.filter(
        organizacao=organizacao
    ).values_list('membro', flat=True)

    participantes = Usuario.objects.filter(id__in=membros_organizacao)
    participantes = pesquisar_objetos(request.GET.get('q'), participantes, ['nome', 'username'])
    
    contexto = {
        'titulo': 'Membros da Organização',
        'cabecalhos': ['Nome', 'Usuário', 'E-mail', 'Cadastro no sistema'],
        'url_pesquisa': f'listagem_participantes',
        'id_url': organizacao.pk,
        'participantes': participantes,
        'botoes':[
            {
                'nome': 'Voltar',
                'classe': 'visualizar-editar-botao',
                'url': 'visualizar_organizacao'
            }
        ]
    }

    return render(request, 'participantes.html', contexto)

# Função bloqueadora que bloqueia o plano gratuito (máximo de 10 membros na organzação)
def pode_convidar_participantes(organizacao):
    if MembroOrganizacao.get_quantidade_membros(organizacao) >= 10:
        return False

    return True