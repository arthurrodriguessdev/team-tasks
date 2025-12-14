from django.core.exceptions import ValidationError
from django import forms
from comum.models import Usuario

class UsuarioCadastroForm(forms.ModelForm):
    password_confirmacao = forms.CharField(
        max_length=128,
        required=True,
        label='Confirme sua senha:'
    )

    class Meta:
        model = Usuario
        fields = ('nome', 'email', 'password', 'username', 'password_confirmacao')

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_confirmacao = cleaned_data.get('password_confirmacao')
        username = cleaned_data.get('username')

        usuarios_existentes = Usuario.objects.filter(username=username)

        if usuarios_existentes.exists():
            return self.add_error('username', 'Este nome de usuário já existe.')
        
        if password and ' ' in password:
            self.add_error('password', 'A senha não deve conter espaço em branco.')

        if password and len(password) < 8:
            return self.add_error('password', 'A senha deve ter, no mínimo, 8 caracteres.')
        
        if password and password_confirmacao and password != password_confirmacao:
            return self.add_error('password_confirmacao', 'As senhas não coincidem.')
        
        return cleaned_data
    
    def save(self, commit=True):
        usuario = super().save(commit=False)

        usuario.nome = usuario.nome.title()
        usuario.username = usuario.username.strip()

        if usuario:
            usuario.full_clean()
            usuario.save()

        return usuario
    
    
class UsuarioLoginForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('email', 'password')