from django.shortcuts import render, redirect
from organizacao.forms import OrganizacaoForm

# TO DO: Verificar regra se um usuário pode criar mais de uma organização
def criar_organizacao(request):
    if request.method == 'POST':
        form = OrganizacaoForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('listagem_tarefas')
    
    contexto = {
        'form': OrganizacaoForm(),
        'titulo_formulario': 'Dados da Organização',
        'titulo_botao_form': 'Cadastrar',
        'titulo': 'Cadastrar Organização',
        'url_view': 'criar_organizacao'
    }

    return render(request, 'criar_organizacao.html', contexto)