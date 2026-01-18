from apipagamentos.views import adquirir_plano_essencial, cancelar_plano_essencial
from apipagamentos.apimercadopago import notificacoes_pagamentos, api_cancelar_plano, validar_pagamento
from django.urls import path

urlpatterns = [
    path('plano_essencial', adquirir_plano_essencial, name='adquirir_plano_essencial'),
    path('notificacoes_pagamentos/', notificacoes_pagamentos, name='notificacoes_pagamentos'),
    path('validar_pagamento/', validar_pagamento, name='validacao_pagamento'),
    path('cancelamento_plano/', cancelar_plano_essencial, name='cancelar_plano'),
    path('api_cancelar_plano/', api_cancelar_plano, name='cancelamento_plano_api')
]