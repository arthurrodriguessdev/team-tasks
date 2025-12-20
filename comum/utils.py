# Funções utilitárias e genéricas

from django.db.models import Q

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
