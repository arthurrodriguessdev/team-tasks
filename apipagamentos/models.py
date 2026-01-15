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

# https://www.mercadopago.com.br/subscriptions/checkout/congrats?collection_id=141502200659&collection_status=approved&preference_id=3136805720-22c97105-18f7-4ab6-be88-0ea10d975268&payment_type=credit_card&payment_id=141502200659&external_reference=5ad811fe16b042738a7a1c676d8c6f6d&site_id=MLB&status=approved&
