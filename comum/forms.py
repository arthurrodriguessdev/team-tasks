from django import forms
from comum.models import Usuario

class UsuarioCadastroForm(forms.ModelForm):
    password_confirmacao = forms.CharField(
        max_length=128,
        required=True
    )

    class Meta:
        model = Usuario
        fields = ('nome', 'email', 'password', 'username', 'password_confirmacao')

    def save(self, commit=False):
        password = self.cleaned_data.get('password')
        password_confirmacao = self.cleaned_data.get('password_confirmacao')

        if password != password_confirmacao:
            return self.add_error('As senhas devem ser iguais.')

        if commit == True:
            self.save()

        return self.cleaned_data
    
    
class UsuarioLoginForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('email', 'password')