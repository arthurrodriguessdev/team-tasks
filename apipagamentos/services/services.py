def ativar_plano_essencial(organizacao):
    if organizacao:
        organizacao.plano = 'pago'
        organizacao.save()

        return True
    
    return False