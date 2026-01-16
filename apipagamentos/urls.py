from apipagamentos.views import adquirir_plano_essencial
from apipagamentos.apimercadopago import notificacoes_pagamentos
from django.urls import path

urlpatterns = [
    path('plano_essencial', adquirir_plano_essencial, name='adquirir_plano_essencial'),
    path('notificacoes_pagamentos/', notificacoes_pagamentos, name='notificacoes_pagamentos')
]