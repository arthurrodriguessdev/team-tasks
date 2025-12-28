from django import forms
from equipe.models import Equipe


class EquipeForm(forms.ModelForm):
    class Meta:
        model = Equipe
        fields = ('nome', 'descricao')