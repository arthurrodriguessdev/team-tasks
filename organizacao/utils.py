def apagar_objeto(objeto):
    if objeto:
        try:
            objeto.delete()
            return True
        
        except Exception as erro:
            print(f'Erro ao excluir objeto: {erro}')
            return False
        
    return False
