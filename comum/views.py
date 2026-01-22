from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from comum.forms import UsuarioCadastroForm, UsuarioLoginForm, VincularResponsaveisForm
from comum.models import Usuario, MembroEquipe, CodigoEmail
from tarefa.models import Tarefa
from comum.utils import criar_codigo_usuario, criar_codigo_verificacao_email
from organizacao.models import Organizacao, MembroOrganizacao, ConviteOrganizacao
from equipe.models import Equipe


def cadastrar_usuario(request):
    if request.method == 'POST':
        form = UsuarioCadastroForm(request.POST)

        if form.is_valid():
            form.save()

            username = request.POST.get('username')
            password = request.POST.get('password')

            if username and password:
                usuario = authenticate(request, username=username, password=password)

                try:
                    login(request, usuario)
                    
                except Exception as error:
                    return HttpResponse(f'Erro: {error}')

            CodigoEmail.objects.create(
                usuario=request.user,
                codigo_verificacao=criar_codigo_verificacao_email()
            )

            messages.success(request, 'Usuário criado com sucesso. Verifique seu e-mail.')
            return enviar_email_codigo(request)
        
    else:
        form = UsuarioCadastroForm()

    contexto = {
        'titulo_pagina': 'Team Task | Entrar',
        'form': form,
        'url_view': 'cadastro_usuario',
        'titulo': 'Team Tasks',
        'paragrafo': 'Um software feito para facilitar a realização de projetos e entregas de empresas!',
        'titulo_form': 'Cadastro',
    }

    return render(request, 'cadastro_usuario.html', contexto)

def login_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        usuario = authenticate(request, username=username, password=password)
        
        if usuario is not None:
            if not request.user.email_verificado:
                return redirect('enviar_email_codigo')
            
            login(request, usuario)
            criar_codigo_usuario(usuario)
            
            if not request.user.tem_organizacao:
                return redirect('onboarding')

            return redirect('exibir_dashboard')
        
        else:
            messages.error(request, 'Email ou senha inválidos. Verifique os dados e tente novamente.')
            return redirect('login_usuario')

    else:
        form = UsuarioLoginForm()

    contexto = {
        'titulo_pagina': 'Team Task | Entrar',
        'form': form,
        'url_view': 'login_usuario',
        'titulo': 'Bem-vindo novamente!',
        'paragrafo': 'Caso seja sua primeira vez por aqui, clique na opção de criar conta ao lado.',
        'titulo_form': 'Login',
        'url_link': 'login_usuario',
        'link_adicional': 'Esqueci minha senha',
        'texto_divisor': 'ou',
    }

    return render(request, 'login_usuario.html', contexto)

def logout_usuario(request):
    logout(request)
    return redirect('login_usuario')

def vincular_responsaveis(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk)

    if request.method == 'POST':
        form = VincularResponsaveisForm(request.POST, tarefa=tarefa, instance=tarefa)

        if form.is_valid():
            form.save()

            messages.success(request, 'Vinculação de tarefa realizada com sucesso')
            return redirect('listagem_tarefas')

    form = VincularResponsaveisForm(tarefa=tarefa, instance=tarefa)
    contexto = {
        'form': form,
        'url_view': 'vincular_responsaveis_tarefa',
        'titulo_formulario': 'Vinculação de responsáveis',
        'titulo_botao_form': 'Salvar',
        'id_url': tarefa.id
    }

    return render(request, 'vincular_responsaveis.html', contexto)

def api_dashboard(request):
    usuario = request.user

    organizacoes = []
    membro_organizacoes = MembroOrganizacao.objects.filter(membro=usuario).select_related('organizacao')

    for membro in membro_organizacoes:
        organizacoes.append(f'{membro.organizacao.nome} ({membro.get_papel_display()})')

    return JsonResponse(
        {
            'qtd_tarefas_criadas_por_mim': Tarefa.total_tarefas_criadas_usuario(usuario),
            'qtd_tarefas_atribuidas_mim': Tarefa.total_tarefas_atribuidas_usuario(usuario),
            'minhas_equipes': list(MembroEquipe.get_equipe_usuario(usuario).values_list('nome', flat=True)),
            'minhas_organizacoes': list(organizacoes)
        })

def exibir_dashboard(request):
    contexto = {
        'titulo': 'Dashboard',
        'botoes':[
            {
                'nome': 'Atualizar',
                'classe': 'visualizar-editar-botao',
                'url': 'exibir_dashboard'
            }
        ]
    }
    
    return render(request, 'dashboard.html', contexto)

def exibir_onboarding(request):
    contexto = {
        'titulo': 'Bem vindo ao TaskTeam',
        'subtitulo': 'Organize equipes, tarefas e responsabilidades em um só lugar',
        'titulo_container': 'Vamos começar?',
        'subtitulo_container': 'Escolha uma das opções abaixo para começar.'
    }

    return render(request, 'onboarding.html', contexto)

def exibir_codigo_convite_onboarding(request):
    contexto = {
        'titulo': 'Quase lá...',
        'subtitulo': 'Preparado para utilizar o TaskTeam?',
        'titulo_container': '',
        'subtitulo_container': 'Copie o código de convite abaixo, envie ao responsável da sua organização e aguarde o convite.',
        'usuario': request.user,
    }

    return render(request, 'onboarding_aguardando_convite.html', contexto)

def convites_onboarding(request):
    convites = request.user.convites.all()
    contexto = {
        'titulo': 'Meus Convites',
        'subtitulo': 'Clique no convite para visualizar mais informações.',
        'titulo_container': 'Convites Ativos',
        'convites': convites,
    }

    return render(request, 'onboarding_visualizar_convites.html', contexto)

def api_organizacao_dashboard(request):
    organizacao = MembroOrganizacao.objects.filter(
        membro=request.user, 
        papel='proprietario').values_list('organizacao', flat=True).first()
    
    equipes_organizacao = Equipe.objects.filter(organizacao=organizacao)
    tarefas_organizacao = Tarefa.objects.filter(equipe__in=equipes_organizacao)

    return JsonResponse({
        'qtd_membros': MembroOrganizacao.get_quantidade_membros(organizacao),
        'qtd_equipes': equipes_organizacao.count(),
        'qtd_tarefas': tarefas_organizacao.count()
    })

def exibir_dashboard_organizacao(request):
    usuario = request.user
    organizacao_proprietario = usuario.organizacoes.filter(papel='proprietario').select_related('organizacao').first()

    contexto = {
        'titulo': f'Dashboard: {organizacao_proprietario.organizacao.nome}',
        'botoes':[
            {
                'nome': 'Detalhes',
                'classe': 'visualizar-editar-botao',
                'url': 'visualizar_organizacao'
            }
        ]
    }
    
    return render(request, 'dashboard_organizacao.html', contexto)

def meu_perfil(request):
    usuario = request.user

    dados = {
        'Nome': usuario.get_nome,
        'Usuário': usuario.username,
        'E-mail': usuario.email,
        'Conta criada em': usuario.date_joined,
        'Código de convite': usuario.codigo
    }

    contexto = {
        'titulo': 'Meu Perfil:',
        'titulo_visualizar': 'Dados Cadastrais',
        'titulo_visualizar_adicional': 'Dados de Organizações',
        'dados': dados,
        'botoes':[
            {   
                'url': 'exibir_dashboard',
                'nome': 'Voltar',
                'classe': 'visualizar-editar-botao'
            },
        ]
    }
    return render(request, 'meu_perfil.html', contexto)

def enviar_email_codigo(request):
    usuario = request.user

    try:
        codigo_email = CodigoEmail.objects.filter(usuario=request.user).first()

    except:
        codigo_email = criar_codigo_usuario(usuario)

    MENSAGEM_PADRAO = f'Olá {usuario.get_nome}, esse é seu código de verificação de 6 dígitos: {codigo_email.codigo_verificacao}'
    ASSUNTO = 'Verificação de e-mail no sistema Stasker.'

    if request.method == 'POST':
        codigo = str(request.POST.get('codigo_verificacao'))

        if codigo == str(codigo_email.codigo_verificacao):
            usuario.email_verificado = True
            usuario.save()

            messages.success(request, 'E-mail verificado com sucesso.')
            return redirect('login_usuario')

        else:
            messages.error(request, 'Erro na verificação. Tente novamente ou solicite o reenvio do código.')
            return redirect('enviar_email_codigo')
    
    try:
        send_mail(
            ASSUNTO,
            MENSAGEM_PADRAO,
            settings.DEFAULT_FROM_EMAIL,
            [usuario.email],
            fail_silently=False
        )

    except Exception as error:
        return HttpResponse(f'Erro: {error}')

    return render(request, 'inserir_codigo_verificacao.html')

# decorador responsável por verificar se o e-mail do usuário já está verificado
class EmailVerificationRequired(object):
    def __init__(self, function):
        self.function = function

    def __call__(self, request):
        if not request.user.tem_email_verificado:
            return redirect('enviar_email_codigo')
        
        response = self.function(request)
        return response