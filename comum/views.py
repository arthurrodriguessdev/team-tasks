from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.mail import send_mail
from django.utils import timezone
import datetime
from django.urls import reverse
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from comum.forms import UsuarioCadastroForm, UsuarioLoginForm, VincularResponsaveisForm, RecuperacaoSenhaForm
from comum.models import Usuario, MembroEquipe, CodigoEmail, TokenAlterarSenha
from tarefa.models import Tarefa
from comum.utils import criar_codigo_usuario, criar_codigo_verificacao_email, gerar_token_alterar_senha
from organizacao.models import Organizacao, MembroOrganizacao, ConviteOrganizacao
from equipe.models import Equipe

URL_ENVIAR_EMAIL = f'https://mail.zoho.com/api/accounts/{settings.ACCOUNT_ID_ZOHO}/messages'
URL_GERAR_TOKEN = f'https://accounts.zoho.com/oauth/v2/token'


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
            return redirect('enviar_email_codigo')
        
    else:
        form = UsuarioCadastroForm()

    contexto = {
        'titulo_pagina': 'Stasker | Criar conta',
        'form': form,
        'url_view': 'cadastro_usuario',
        'titulo': 'Stasker Gerenciamento',
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
            login(request, usuario)
            criar_codigo_usuario(usuario)

            if not request.user.email_verificado:
                return redirect('enviar_email_codigo')
            
            if not request.user.tem_organizacao:
                return redirect('onboarding')

            return redirect('exibir_dashboard')
        
        else:
            messages.error(request, 'Email ou senha inválidos. Verifique os dados e tente novamente.')
            return redirect('login_usuario')

    else:
        form = UsuarioLoginForm()

    contexto = {
        'titulo_pagina': 'Stasker | Entrar',
        'form': form,
        'url_view': 'login_usuario',
        'titulo': 'Bem-vindo novamente!',
        'paragrafo': 'Caso seja sua primeira vez por aqui, clique na opção de criar conta ao lado.',
        'titulo_form': 'Login',
        'url_link': 'alterar_senha',
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
        'titulo': 'Bem vindo ao Stasker',
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
    URL_API = 'https://api.brevo.com/v3/smtp/email'

    usuario = request.user
    codigo_email = CodigoEmail.objects.filter(usuario=usuario).first() or criar_codigo_usuario(usuario)

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

    MENSAGEM_PADRAO = f'Olá {usuario.get_nome}, esse é seu código de verificação de 6 dígitos: {codigo_email.codigo_verificacao}'
    ASSUNTO = 'Verificação de e-mail no sistema Stasker.'

    headers = {
        'accept': 'application/json',
        'api-key': settings.TOKEN_API_BREVO,
        'content-type': 'application/json'
    }

    parametros = {
        "sender":{
            "name":"Stasker Gerenciamento",
            "email":"staskergerenciamento@gmail.com"
        },
        "to":[{"email": f"{usuario.email}"}],
        "subject": f"{ASSUNTO}",
        "htmlContent":f"<html><head></head><body><p>{MENSAGEM_PADRAO}</p></body></html>"
    }

    try:
        response = requests.post(url=URL_API, headers=headers, json=parametros)

    except Exception as error:
        return HttpResponse(f'Erro ao enviar o código de verificação: {error}')
    
    return render(request, 'inserir_codigo_verificacao.html')

# decorador responsável por verificar se o e-mail do usuário já está verificado
class EmailVerificationRequired(object):
    def __init__(self, function):
        self.function = function

    def __call__(self, request, **kwargs):
        pk = None

        for chave, valor in kwargs.items():
            if 'pk' in chave:
                pk = kwargs['pk']

        if not request.user.tem_email_verificado:
            return redirect('enviar_email_codigo')
        
        if not pk is None:
            response = self.function(request, pk)
        else:
            response = self.function(request)

        return response

def suporte_usuario(request):
    usuario = request.user

    if usuario:
        email_solicitante = usuario.email
        username_solicitante = usuario.username

    if request.method == 'POST':
        erro = request.POST.get('erro_suporte')
        local_erro = request.POST.get('local_erro_suporte')
    
        if not erro or not local_erro:
            messages.error(request, 'Não foi possível enviar o chamado. Preencha a descrição do erro e o local onde ele ocorre.')
            return redirect('exibir_dashboard')

        try:
            SUBJECT = f'Ocorrência de erros ou dúvidas sobre o sistema.'

            HTML_CONTENT = ''
            HTML_CONTENT += f'<h2>- Erro / Dúvida:</h2>'
            HTML_CONTENT += f'<p>{erro}</p></br>'
            HTML_CONTENT += f'<p>- Local de ocorrência: <strong>{local_erro}</strong></p>'
            HTML_CONTENT += f'<p>- E-mail do usuário: <strong>{email_solicitante}</strong></p>'
            HTML_CONTENT += f'<p>- Username do usuário: <strong>{username_solicitante}</strong></p>'

            response = enviar_email(settings.EMAIL_SUPORTE_DEFAULT, SUBJECT, HTML_CONTENT)
            if response.status_code == 200:
                messages.success(request, 'Sua dúvida foi enviada com sucesso. Nossa equipe irá investigar sua solicitação.')
                return redirect('exibir_dashboard')

        except Exception as error:
            return HttpResponse(f'Ocorreu um erro: {error}')

    return render(request, 'pedir_suporte.html')

def gerar_token_zoho_email():
    parametros_api = {
        'refresh_token': settings.REFRESH_TOKEN_ZOHO,
        'client_id': settings.CLIENT_ID_ZOHO,
        'client_secret': settings.CLIENT_SECRET_ZOHO,
        'grant_type': 'refresh_token'
    }

    try:
        response = requests.post(url=URL_GERAR_TOKEN, data=parametros_api).json()

    except Exception as error:
        return HttpResponse(f'Ocorreu um erro de integração: {error}')

    if response and "access_token" in response:
        return response['access_token']
        
    return HttpResponse('Ocorreu um erro inesperado.', status=response.status_code)

def alterar_senha(request):
    if request.method == 'POST':
        email = request.POST.get('email_trocar_senha')

        if email:
            usuario = Usuario.objects.filter(email=email).first()

            if usuario is None:
                messages.error(request, 'Não encontramos nenhuma conta com esse e-mail.')
                return redirect('alterar_senha')
            
            token_alterar_senha = gerar_token_alterar_senha()

            if token_alterar_senha is None:
                messages.error(request, 'Ocorreu algum erro. Tente novamente mais tarde.')
                return redirect('alterar_senha')
            
            # criando token (válido por 10 min)
            validade = timezone.now() + datetime.timedelta(minutes=10)
            TokenAlterarSenha.objects.create(
               token_codigo=token_alterar_senha,
               usuario=usuario,
               validade=validade
            )

            token = TokenAlterarSenha.objects.get(usuario=usuario)

            URL_ALTERAR_SENHA = request.build_absolute_uri(reverse('redefinicao_senha', args=[token.token_codigo, usuario.pk]))
            
            ASSUNTO = 'Recuperação de senha'
            HTML_CONTENT = ''
            HTML_CONTENT += f'<h2>- Bem-vindo de volta!</h2>'
            HTML_CONTENT += f'<p>Acesse o link abaixo e realize a recuperação de senha da sua conta</p><br>'
            HTML_CONTENT += f'<a href="{URL_ALTERAR_SENHA}">{URL_ALTERAR_SENHA}</a>'

            response = enviar_email(email, ASSUNTO, HTML_CONTENT)
            if response.status_code != 200:
                token.delete()
                messages.error(request, 'A requisição de e-mail não foi atendida. Tente novamente mais tarde.')
            
            messages.success(request, 'Foi enviado um link de recuperação de senha para seu e-mail. (válido por 10 minutos).')
            return redirect('login_usuario')
            
        else:
            messages.error(request, 'O e-mail informado não é válido.')
            return redirect('alterar_senha')

    return render(request, 'verificacao_alterar_senha.html')

def cadastrar_nova_senha(request, *args, **kwargs):
    try:
        token = kwargs['token']
        id_user = kwargs['id_usuario']
        
        usuario = Usuario.objects.get(pk=id_user)
        registro_token = TokenAlterarSenha.objects.get(token_codigo=token, usuario=usuario)
        
        if registro_token is None or registro_token.validade < timezone.now():
            registro_token.delete()
            messages.error(request, 'A validade do token expirou, realize a solicitação novamente.')
            return redirect('alterar_senha')

    except Exception as error:
        print(f'Erro: {error}')
        registro_token.delete()
        return HttpResponse('Ocorreu um erro inesperado. Tente novamente mais tarde.')
    
    if request.method == 'POST':
        form = RecuperacaoSenhaForm(request.POST, instance=usuario)

        if form.is_valid():
            usuario.set_password(form.cleaned_data['password'])
            usuario.save()

            tokens = usuario.token.all()
            tokens.delete()
            messages.success(request, 'Senha recuperada com sucesso. Realize login novamente.')
            return redirect('login_usuario')
        
        messages.error(request, 'O formulário enviado está inválido.')
        return redirect('redefinicao_senha', token, id_user)
    
    form = RecuperacaoSenhaForm(instance=usuario)
    contexto = {
        'token': token,
        'form': form,
        'id_user': id_user
    }

    return render(request, 'formulario_alteracao_senha.html', contexto)

def enviar_email(to_email, assunto, conteudo_html):
    access_token = gerar_token_zoho_email()

    if access_token:
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Zoho-oauthtoken {access_token}'
        }

        parametros_api = {
            'fromAddress': settings.EMAIL_SUPORTE_DEFAULT,
            'toAddress': to_email,
            'subject': assunto,
            'content': conteudo_html,
            'askReceipt' : 'yes',
            'mailFormat': 'html'
        }

        try:
            response = requests.post(url=URL_ENVIAR_EMAIL, json=parametros_api, headers=headers)
            return response

        except Exception as error:
            return HttpResponse(f'Ocorreu um erro de requisição: {error}')
        
    return HttpResponse(f'Erro de identificação.')

# Páginas de erros personalizadas
def forbidden(request, exception):
    return render(request, 'erros/erro403.html', status=403)

def not_found(request, exception):
    return render(request, 'erros/erro404.html', status=404)

def server_error(request):
    return render(request, 'erros/erro500.html', status=500)