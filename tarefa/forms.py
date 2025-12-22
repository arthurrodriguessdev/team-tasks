from django import forms
from django_select2.forms import Select2Widget
from comum.models import Equipe, MembroEquipe
from tarefa.models import Tarefa


class TarefaForm(forms.ModelForm):
    prazo = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type':'date',
            }
        )
    )

    em_equipe = forms.BooleanField(
        required=False,
        help_text='Essa opção só deve ser marcada caso a tarefa que esteja sendo cadastrada seja pertencente à uma equipe. OBS: O usuário deve estar em uma equipe.'
    )

    equipe = forms.ModelChoiceField(
        queryset=Equipe.objects.all(),
        required=False,
        widget=Select2Widget(attrs={
            'class': 'select2-widget'
        },
    ))

    class Meta:
        model = Tarefa
        fields = ('titulo', 'descricao', 'prazo', 'em_equipe', 'equipe')

    # TO DO: Revisar esse método inteiro (lembrar que cada equipe pode ter VÁRIOS membros)
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

        equipes_user = MembroEquipe.objects.filter(membro=self.request.user.pk).values_list('equipe', flat=True)
        equipes = Equipe.objects.filter(id__in=equipes_user)

        self.fields['equipe'].queryset = equipes
        
    def save(self, commit = True):
        tarefa = super().save(commit=False)

        tarefa.criada_por = self.request.user

        if commit:
            tarefa.save()
        return tarefa