import requests
from django.http import JsonResponse
from django.conf import settings
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from apipagamentos.models import Assinatura
from apipagamentos.services.services import ativar_plano_essencial

logger = logging.getLogger(__name__)
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
        "notification_url": "https://joey-tinnier-cristopher.ngrok-free.dev/planos/notificacoes_pagamentos/"
    }

    response = requests.post(LINK_SEM_PLANO, json=parametros_api, headers=headers)
    return response.json()

@csrf_exempt
def notificacoes_pagamentos(request):
    try:
        dados_recebidos_webhook = json.loads(request.body)
        id_assinatura = dados_recebidos_webhook['data']['id']

        logger.info(f'Dados recebidos pelo webhook: {dados_recebidos_webhook}')

        validar_pagamento(id_assinatura)

        return JsonResponse({}, status=200)
    
    except Exception as error:
        return JsonResponse({'error': str(error)}, status=400)
    
def validar_pagamento(id_assinatura):
    URL_GET_ASSINATURA = f'https://api.mercadopago.com/preapproval/{id_assinatura}'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': settings.TOKEN_API_MERCADOPAGO
    }

    response = requests.get(URL_GET_ASSINATURA, headers=headers).json()

    if not response or 'status' not in response:
        return False

    assinatura = Assinatura.objects.filter(
        preapproval_id=response['id']
    ).select_related('organizacao').first()

    if not assinatura:
        return False

    if response['status'] == 'authorized' and assinatura.status != 'authorized':
        assinatura.status = 'authorized'
        assinatura.ativa = True
        assinatura.save()

        ativar_plano_essencial(assinatura.organizacao)
        return True
    
    return False

def api_cancelar_plano(id_assinatura):

    URL_API_CANCELAR_ASSINATURA = f'https://api.mercadopago.com/preapproval/{id_assinatura}'
    STATUS_CANCELADO = 'cancelled'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': settings.TOKEN_API_MERCADOPAGO
    }
    
    body = {
        'status': STATUS_CANCELADO
    }

    try:
        response = requests.put(URL_API_CANCELAR_ASSINATURA, headers=headers, json=body, timeout=10)

    except requests.exceptions.Timeout:
        logger.error(f'Timeout ao realizar requisição: {response.text}')
        return JsonResponse({'erro': 'Timeout com o Mercado Pago'}, status=504)
    
    except requests.exceptions.HTTPError:
        logger.error(f'Erro HTTP: {response.text}')
        return JsonResponse({'erro': 'Erro ao cancelar assinatura'}, status=response.status_code)

    return response