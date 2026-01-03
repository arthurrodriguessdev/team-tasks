from django.db import models
from comum.models import Usuario

class Organizacao(models.Model):
    PLANO_CHOICES = [
        ('gratuito', 'Gratuito'),
        ('pago', 'Pago')
    ]

    nome = models.CharField(max_length=50, blank=False, null=False)
    criada_em = models.DateTimeField(auto_now_add=True)
    plano = models.CharField(choices=PLANO_CHOICES, default='gratuito')
    # papel TO DO: Visualizar isso depois

    def __str__(self):
        return self.nome
    

class MembroOrganizacao(models.Model):
    organizacao = models.ForeignKey(Organizacao, on_delete=models.PROTECT, related_name='organizacao')
    membro = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='membro_organizacao')

    def __str__(self):
        return self.organizacao.nome
    
    @classmethod
    def eh_membro_equipe(cls, usuario):
        return cls.objects.filter(membro=usuario)