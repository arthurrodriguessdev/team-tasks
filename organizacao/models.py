from django.db import models
from comum.models import Usuario

class Organizacao(models.Model):
    PLANO_CHOICES = [
        ('gratuito', 'Gratuito'),
        ('pago', 'Pago')
    ]

    nome = models.CharField(max_length=50, blank=False, null=False)
    criada_em = models.DateTimeField(auto_now_add=True)
    plano = models.CharField(choices=PLANO_CHOICES, default='gratuito', max_length=10)
    # TO DO: Verificar a possibilidade de um campo FK criado_por (fk com Usuario)

    def __str__(self):
        return self.nome
    

class MembroOrganizacao(models.Model):
    PAPEL_CHOICES = [
        ('proprietario', 'Proprietário'),
        ('administrador', 'Administrador'),
        ('membro', 'Membro')
    ]

    organizacao = models.ForeignKey(Organizacao, on_delete=models.PROTECT, related_name='membros')
    membro = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='organizacoes')
    papel = models.CharField(choices=PAPEL_CHOICES, default='membro', max_length=20)

    def __str__(self):
        return f'{self.membro} - {self.organizacao}'

    @classmethod
    def get_organizacao_do_proprietario(cls, usuario):
        proprietario = cls.objects.select_related('organizacao').filter(
            membro=usuario,
            papel='proprietario'
        ).first()

        if proprietario:
            return proprietario.organizacao
        return None
    
    @classmethod
    def get_quantidade_membros(cls, organizacao):
        return cls.objects.filter(organizacao=organizacao).count()

    @classmethod
    def get_membros_organizacao(cls, organizacao):
        return cls.objects.filter(organizacao=organizacao)
    
    # @classmethod
    # def eh_membro_organizacao(cls, usuario):
    #     return cls.objects.filter(membro=usuario)


class ConviteOrganizacao(models.Model):
    usuario_convidado = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='convites')
    organizacao = models.ForeignKey(Organizacao, on_delete=models.CASCADE, related_name='convites_enviados')
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usuario_convidado} - {self.organizacao}'