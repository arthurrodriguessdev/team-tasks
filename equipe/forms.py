from django import forms
from django_select2.forms import Select2Widget, Select2MultipleWidget
from django.db.models import Q
from equipe.models import Equipe
from comum.models import MembroEquipe, Usuario
from organizacao.models import MembroOrganizacao, Organizacao


class EquipeForm(forms.ModelForm):
    responsavel = forms.ModelChoiceField(
        required=True,
        queryset=None,
        label='Responsável pela equipe',
        widget=Select2Widget(attrs={
            'class': 'select2-widget'
        })
    )

    organizacao = forms.ModelChoiceField(
        required=True, 
        queryset=None,
        widget=Select2Widget(attrs={
            'class': 'select2-widget'
        })
    )

    class Meta:
        model = Equipe
        fields = ('nome', 'descricao', 'responsavel', 'organizacao')

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

        organizacoes = MembroOrganizacao.objects.filter(
            Q(membro=self.usuario, papel='proprietario') 
            # Q(membro=self.usuario, papel='administrador')
        ).values_list('organizacao', flat=True).distinct()

        if not self.instance.pk:
            self.fields.pop('responsavel')
            self.fields['organizacao'].queryset = Organizacao.objects.filter(id__in=organizacoes)
        
        else:
            self.fields['responsavel'].queryset = MembroEquipe.get_usuarios_membros_equipe(self.instance.pk)
            self.fields.pop('organizacao')

class AdicionarParticipanteForm(forms.Form):
    membro = forms.ModelMultipleChoiceField(
        label='Membros da organização que não são da equipe',
        queryset=Usuario.objects.none(),
        required=True,
        widget=Select2MultipleWidget(attrs={
            'class': 'select2-widget'
        })
    )

    class Meta:
        model = MembroEquipe
        fields = ('membro',)
    
    def __init__(self, *args, **kwargs):
        self.organizacao = kwargs.pop('organizacao', None)
        self.equipe = kwargs.pop('equipe', None)
        super().__init__(*args, **kwargs)
        
        if self.organizacao:
            usuarios_organizacao = MembroOrganizacao.objects.filter(
                organizacao=self.organizacao
            ).values_list('membro', flat=True)

            if self.equipe:
                usuarios_organizacao = usuarios_organizacao.exclude(
                    membro__in=MembroEquipe.objects.filter(equipe=self.equipe).values_list('membro', flat=True)
                )

            self.fields['membro'].queryset = Usuario.objects.filter(id__in=usuarios_organizacao)