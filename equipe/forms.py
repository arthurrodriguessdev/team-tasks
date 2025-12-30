from django import forms
from django_select2.forms import Select2Widget
from equipe.models import Equipe
from comum.models import MembroEquipe


class EquipeForm(forms.ModelForm):
    responsavel = forms.ModelChoiceField(
        required=True,
        queryset=None,
        label='Responsável pela equipe',
        widget=Select2Widget(attrs={
            'class': 'select2-widget'
        })
    )

    class Meta:
        model = Equipe
        fields = ('nome', 'descricao', 'responsavel')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.fields.pop('responsavel')
        
        else:
            self.fields['responsavel'].queryset = MembroEquipe.get_usuarios_membros_equipe(self.instance.pk)