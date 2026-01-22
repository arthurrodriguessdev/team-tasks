# Funções utilitárias e genéricas

from django.db.models import Q
import random
import string
from comum.models import Usuario, CodigoEmail

def pesquisar_objetos(termo, queryset, campos):
    if not termo:
        return queryset
    
    buscar = Q()
    for campo in campos:
        buscar |= Q(**{
            f"{campo}__icontains": termo
            }
        )

    return queryset.filter(buscar)

def criar_codigo_usuario(usuario):
    if not usuario.codigo is None:
        return

    while True:
        codigo_usuario = ''.join(random.choices(string.digits, k=6))

        if Usuario.objects.filter(codigo=codigo_usuario).exists():
            continue
        
        usuario.codigo = codigo_usuario
        usuario.save()
        return
    
def criar_codigo_verificacao_email():
    while True:
        codigo_verificacao = ''.join(random.choices(string.digits, k=6))

        if CodigoEmail.objects.filter(codigo_verificacao=codigo_verificacao).exists():
            continue

        return codigo_verificacao