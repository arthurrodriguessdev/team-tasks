from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from comum.forms import UsuarioCadastroForm, UsuarioLoginForm, VincularResponsaveisForm
from comum.models import Usuario, MembroEquipe
from tarefa.models import Tarefa
from comum.utils import criar_codigo_usuario
from organizacao.models import Organizacao, MembroOrganizacao


def cadastrar_usuario(request):
    if request.method == 'POST':
        form = UsuarioCadastroForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário criado com sucesso.')

            return redirect('login_usuario')
        
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

        # arthurx18 == 18011801
        usuario = authenticate(request, username=username, password=password)

        if usuario is not None:
            login(request, usuario)
            criar_codigo_usuario(usuario)
            
            if not MembroOrganizacao.eh_membro_equipe(usuario):
                return redirect('onboarding')

            return redirect('listagem_tarefas')
        
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

    return JsonResponse(
        {
            'qtd_tarefas_criadas_por_mim': Tarefa.total_tarefas_criadas_usuario(usuario),
            'qtd_tarefas_atribuidas_mim': Tarefa.total_tarefas_atribuidas_usuario(usuario),
            'minhas_equipes': list(MembroEquipe.get_equipe_usuario(usuario).values_list('nome', flat=True))
        })

def exibir_dashboard(request):
    contexto = {
        'titulo': 'Dashboard',
        'botoes':[
            {
                'nome': 'Teste',
                'classe': 'visualizar-editar-botao',
                'url': 'listagem_tarefas'
            }
        ]
    }
    
    return render(request, 'dashboard.html', contexto)

def exibir_onboarding(request):
    return render(request, 'onboarding.html')