# Funções utilitárias e genéricas

from django.db.models import Q
import random

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
        return ''
    
    codigo_usuario = str(random.random())
    codigo_usuario = str(usuario.pk) + (codigo_usuario[14:])

    usuario.codigo = codigo_usuario
    usuario.save()