import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

LINK_SEM_PLANO = 'https://api.mercadopago.com/preapproval'

def criar_plano_pagar():
    headers = {
        'Authorization': 'Bearer APP_USR-1615086174935673-011514-ddd5cc9de23bda595f3a3ff1383e03ec-3136805720',
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
        "status": "pending"
    }

    response = requests.post(LINK_SEM_PLANO, json=parametros_api, headers=headers)
    return response.json()

@csrf_exempt
def notificacoes_webhooks(request):
    return JsonResponse({'foi': 'chegou'})