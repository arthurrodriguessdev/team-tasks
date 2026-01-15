from django.shortcuts import render, redirect, HttpResponse
from apipagamentos.apimercadopago import criar_plano_pagar
from apipagamentos.models import Assinatura
from organizacao.models import MembroOrganizacao

def adquirir_plano_essencial(request):
    organizacao = MembroOrganizacao.get_organizacao_do_proprietario(request.user)

    if Assinatura.objects.filter(organizacao=organizacao, status__in=['pending, authorized']).exists():
        return HttpResponse('Já existe uma assinatura em andamento.', status=400)
    
    plano = criar_plano_pagar()

    if not 'init_point' in plano or not 'id' in plano:
        return HttpResponse('Erro ao criar assinatura.', status=400)
    
    Assinatura.objects.create(
        organizacao=organizacao,
        preapproval_id=plano['id'],
        plano='Essencial',
        valor=19.90,
        status='pending',
        ativa=False
    )

    pagina_pagamento = plano['init_point']
    return redirect(pagina_pagamento)