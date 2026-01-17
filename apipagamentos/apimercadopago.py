import requests
from django.http import JsonResponse
from django.conf import settings
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from apipagamentos.models import Assinatura
from organizacao import views

settings.TOKEN_API_MERCADOPAGO

LINK_SEM_PLANO = 'https://api.mercadopago.com/preapproval'

def criar_plano_pagar():
    headers = {
        'Authorization': settings.TOKEN_API_MERCADOPAGO,
        'Content-Type': 'application/json'
    }

    parametros_api = {
        "reason": "Stasker - Plano Essencial",
        "payer_email": "test_user_1900638117602591183@testuser.com",
        "auto_recurring": {
            "frequency": 1,
            "frequency_type": "months",
            "transaction_amount": 19.90,
            "currency_id": "BRL"
        },

        "back_url": "http://127.0.0.1:8000/dashboard",
        "status": "pending",
        "notification_url": "https://joey-tinnier-cristopher.ngrok-free.dev/planos/notificacoes_pagamentos/?source_news=webhooks"
    }

    response = requests.post(LINK_SEM_PLANO, json=parametros_api, headers=headers)
    return response.json()

@require_POST
@csrf_exempt
def notificacoes_pagamentos(request):
    try:
        dados_recebidos_webhook = json.loads(request.body)
        id_assinatura = dados_recebidos_webhook['data']['id']

        validar_pagamento(id_assinatura)

        return JsonResponse({"foi": "ok"}, status=200)
    
    except Exception as error:
        return JsonResponse({'error': str(error)}, status=400)

def validar_pagamento(id_assinatura):
    URL_GET_ASSINATURA = f'https://api.mercadopago.com/preapproval/{id_assinatura}'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': settings.TOKEN_API_MERCADOPAGO
    }

    response = requests.get(URL_GET_ASSINATURA, headers=headers).json()

    if response:
        assinatura = Assinatura.objects.filter(
            preapproval_id=response['id']
        ).select_related('organizacao').first()

        status_assinatura = response['status']
    
        if status_assinatura == 'authorized':
            views.alterar_status_assinatura()