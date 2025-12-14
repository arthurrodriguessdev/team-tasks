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

    def clean_username(self):
        username = self.cleaned_data.get('username')
        usuarios_existente = Usuario.objects.filter(username=username)

        if usuarios_existente.exists():
            raise forms.ValidationError('Este nome de usuário já existe.')
        
        return username
          
    def clean_email(self):
        email = self.cleaned_data.get('email')
        email_existente = Usuario.objects.filter(email=email)

        if email_existente.exists():
            raise forms.ValidationError('O e-mail informado já existe.')
        
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if password and ' ' in password:
            raise forms.ValidationError('A senha não deve conter espaço em branco.')

        if password and len(password) < 8:
            raise forms.ValidationError('A senha deve ter, no mínimo, 8 caracteres.')
        
        return password
    
    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_confirmacao = cleaned_data.get('password_confirmacao')
        
        if password and password_confirmacao and password != password_confirmacao:
            self.add_error('password_confirmacao', 'As senhas não coincidem.')
            return cleaned_data
        
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
        fields = ('username', 'password')