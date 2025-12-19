from django import forms
from tarefa.models import Tarefa


class TarefaForm(forms.ModelForm):
    prazo = forms.DateField(
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