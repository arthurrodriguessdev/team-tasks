from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from comum.forms import UsuarioForm
from comum.models import Usuario

def registrar_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)

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
        form = UsuarioForm()

    return render(request, ..., {'form': form})

def login_usuario(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        usuario = authenticate(request, email=email, password=password)

        if usuario is None:
            login(request, usuario)
    
