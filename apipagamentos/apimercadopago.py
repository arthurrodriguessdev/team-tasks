import requests

LINK_SEM_PLANO = 'https://api.mercadopago.com/preapproval'

def criar_plano_pagar(email_pagador):
    headers = {
        'Authorization': '',
        'Content-Type': 'application/json'
    }

    parametros_api = {
        "reason": "Stasker - Plano Essencial",
        "payer_email": email_pagador,
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