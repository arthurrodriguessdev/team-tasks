from django import forms
from django_select2.forms import Select2Widget
from comum.models import Equipe
from tarefa.models import Tarefa


class TarefaForm(forms.ModelForm):
    prazo = forms.DateField(
        required=False
    )
    
    # responsaveis = forms.ModelChoiceField(
    #     queryset=Equipe,
    #     widget=Select2Widget,
    #     required=False
    # )

    equipe = forms.ModelChoiceField(
        queryset=Equipe.objects.all(),
        widget=Select2Widget,
        required=False
    )

    class Meta:
        model = Tarefa
        fields = ('titulo', 'descricao', 'prazo', 'equipe', 'responsaveis')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)
        
    def save(self, commit = True):
        tarefa = super().save(commit=False)

        tarefa.criada_por = self.request.user

        if commit:
            tarefa.save()
        return tarefa