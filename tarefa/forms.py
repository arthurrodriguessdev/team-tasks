from django import forms
from django_select2.forms import Select2Widget, Select2MultipleWidget
import datetime
from comum.models import MembroEquipe, Usuario
from equipe.models import Equipe
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

    equipe = forms.ModelChoiceField(
        queryset=Equipe.objects.all(),
        required=True,
        widget=Select2Widget(attrs={
            'class': 'select2-widget'
        },
    ))

    class Meta:
        model = Tarefa
        fields = ('titulo', 'descricao', 'prazo', 'equipe')

    # TO DO: Revisar esse método inteiro (lembrar que cada equipe pode ter VÁRIOS membros)
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields.pop('equipe')
            
        else:
            equipes_user = MembroEquipe.objects.filter(membro=self.request.user.pk).values_list('equipe', flat=True)
            equipes = Equipe.objects.filter(responsavel=self.request.user)

            self.fields['equipe'].queryset = equipes
    
    def clean_prazo(self):
        data_atual = datetime.datetime.now().date()
        prazo = self.cleaned_data.get('prazo')

        if prazo:
            diferenca_dias = (prazo - data_atual).days

            if diferenca_dias < 0:
                raise forms.ValidationError('Data de prazo inválida.')

        return prazo
        
    def save(self, commit = True):
        tarefa = super().save(commit=False)

        if not tarefa.pk:
            tarefa.criada_por = self.request.user

        if commit:
            tarefa.save()
        return tarefa