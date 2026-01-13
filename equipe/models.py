from django.db import models
from comum.models import Usuario
from organizacao.models import Organizacao


class Equipe(models.Model):
    criada_por = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='criador_equipe')
    responsavel = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='responsavel_equipe')
    nome = models.CharField(max_length=50, null=False, blank=False)
    descricao = models.TextField(null=True, blank=True, verbose_name='Descrição')
    organizacao = models.ForeignKey(
        Organizacao, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        verbose_name='Organização', 
        help_text='Organização à qual a equipe pertence'
    )

    def __str__(self):
        return self.nome
    
    @classmethod
    def eh_responsavel_equipe(self, usuario):
        return self.objects.filter(responsavel=usuario)
    
    @classmethod
    def get_qtd_equipes(cls, organizacao):
        return cls.objects.filter(organizacao=organizacao).count()
