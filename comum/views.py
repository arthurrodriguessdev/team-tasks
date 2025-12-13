from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from comum.forms import UsuarioCadastroForm, UsuarioLoginForm
from comum.models import Usuario

def registrar_usuario(request):
    if request.method == 'POST':
        form = UsuarioCadastroForm(request.POST)

        if form.is_valid():
            Usuario.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                nome=form.cleaned_data['nome']
            ).save()

            messages.success(request, 'Usuário criado com sucesso.')
            return redirect(...)
        
    else:
        form = UsuarioCadastroForm()

    return render(request, ..., {'form': form})

def login_usuario(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        usuario = authenticate(request, email=email, password=password)

        if usuario is not None:
            login(request, usuario)
        
        else:
            form = UsuarioLoginForm()
            return render(request, 'login_usuario.html', {'form': form})

    else:
        form = UsuarioLoginForm()
        contexto = {
            'form': form,
            'url_view': 'login_usuario',
            'titulo': 'Bem-vindo novamente!',
            'paragrafo': 'Caso seja sua primeira vez por aqui, clique na opção de criar conta ao lado. '
        }

    return render(request, 'login_usuario.html', contexto)
    
