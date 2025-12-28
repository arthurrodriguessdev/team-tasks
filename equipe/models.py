from django.db import models
from comum.models import Usuario


class Equipe(models.Model):
    criada_por = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='criador_equipe')
    responsavel = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='responsavel_equipe')
    nome = models.CharField(max_length=50, null=False, blank=False)
    descricao = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nome
