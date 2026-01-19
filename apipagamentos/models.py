from django.db import models
from organizacao.models import Organizacao

class Assinatura(models.Model):

    STATUS_PAGAMENTO = [
        ('authorized', 'Ativa'),
        ('pending', 'Pendente'),
        ('cancelled', 'Cancelada'),
    ]

    organizacao = models.ForeignKey(Organizacao, on_delete=models.CASCADE, related_name='assinaturas')
    preapproval_id = models.CharField(max_length=100, unique=True) # ID retornado pelo Mercado Pago (preapproval_id)
    plano = models.CharField(max_length=50)
    status = models.CharField(max_length=20,choices=STATUS_PAGAMENTO,default='pending')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_cancelamento = models.DateTimeField(null=True, blank=True)
    ativa = models.BooleanField(default=False)
    criada_em = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f'{self.organizacao} - {self.plano} ({self.status})'