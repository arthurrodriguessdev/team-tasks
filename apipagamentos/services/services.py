def ativar_plano_essencial(organizacao):
    if organizacao:
        organizacao.plano = 'pago'
        organizacao.save()

        return True
    
    return False

def desativar_plano_essencial(organizacao):
    if organizacao:
        organizacao.plano = 'gratuito'
        organizacao.save()

        return True
    
    return False