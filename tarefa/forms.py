from django import forms
from django_select2.forms import Select2Widget
from comum.models import Equipe, MembroEquipe
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

    em_equipe = forms.BooleanField(
        required=False,
        help_text='Essa opção só deve ser marcada caso a tarefa que esteja sendo cadastrada seja pertencente à uma equipe. OBS: O usuário deve estar em uma equipe.'
    )

    equipe = forms.ModelChoiceField(
        queryset=Equipe.objects.all(),
        widget=Select2Widget,
        required=False
    )

    class Meta:
        model = Tarefa
        fields = ('titulo', 'descricao', 'prazo', 'em_equipe', 'equipe', 'responsaveis')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

        equipe_usuario = MembroEquipe.objects.filter(membro=self.request.user.pk).values_list('equipe', flat=True).first()

        if equipe_usuario is None:
            self.fields['equipe'].disabled = True
            # self.fields['responsaveis'].disabled = True DESCOMENTAR
        
    def save(self, commit = True):
        tarefa = super().save(commit=False)

        tarefa.criada_por = self.request.user

        if commit:
            tarefa.save()
        return tarefa