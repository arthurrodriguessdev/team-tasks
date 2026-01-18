from django.shortcuts import render, redirect, HttpResponse
import logging
from django.conf import settings
from apipagamentos.apimercadopago import criar_plano_pagar, api_cancelar_plano
from apipagamentos.models import Assinatura
from organizacao.models import MembroOrganizacao, Organizacao

logger = logging.getLogger(__name__)

def adquirir_plano_essencial(request):
    if not settings.PAGAMENTO_ATIVO:
        return HttpResponse('Pagamento e planos indisponíveis temporariamente')
    
    organizacao = MembroOrganizacao.get_organizacao_do_proprietario(request.user)

    if Assinatura.objects.filter(organizacao=organizacao, status__in=['pending, authorized']).exists():
        return HttpResponse('Já existe uma assinatura em andamento.', status=400)
    
    plano = criar_plano_pagar()
    print(plano['init_point'])

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

def cancelar_plano_essencial(request):
    organizacao = MembroOrganizacao.get_organizacao_do_proprietario(request.user)

    if not organizacao or organizacao.plano != 'pago':
        return HttpResponse('A organização não foi encontrada ou não possui o plano essencial ativo.')
    
    try:
        assinatura = Assinatura.objects.get(organizacao=organizacao, status='authorized')
        api_cancelar_plano(assinatura.preapproval_id)

    except Exception as error:
        logger.error(f'Erro ao buscar assinatura: ', exc_info=error)
    
    return HttpResponse('Teste')