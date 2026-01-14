from django.shortcuts import render, redirect
from apipagamentos.apimercadopago import criar_plano_pagar
from django.shortcuts import HttpResponse

def adquirir_plano_essencial(request):
    plano = criar_plano_pagar(request.user.email)
    pagina_pagamento = plano['init_point']

    return redirect(pagina_pagamento)