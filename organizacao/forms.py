from django import forms
from django_select2.forms import Select2MultipleWidget
from organizacao.models import Organizacao, MembroOrganizacao
from comum.models import Usuario


class OrganizacaoForm(forms.ModelForm):
    class Meta:
        model = Organizacao
        fields = ('nome',)


class AdministradoresForm(forms.Form):
    membro = forms.ModelMultipleChoiceField(
        label='Estes membros serão administradores da organização',
        required=True,
        queryset=MembroOrganizacao.objects.none(),
        widget=Select2MultipleWidget(attrs={
            'class': 'select2-widget'
        })
    )

    class Meta:
        model = MembroOrganizacao
        fields = ('membro',)
    
    def __init__(self, *args, **kwargs):
        self.organizacao = kwargs.pop('organizacao')
        super().__init__(*args, **kwargs)

        if self.organizacao:
            membros_opcoes = self.organizacao.membros.filter(
                papel='membro'
            ).values_list('membro')

            self.fields['membro'].queryset = Usuario.objects.filter(id__in=membros_opcoes)