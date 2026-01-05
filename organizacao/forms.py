from django import forms
from organizacao.models import Organizacao


class OrganizacaoForm(forms.ModelForm):
    class Meta:
        model = Organizacao
        fields = ('nome',)