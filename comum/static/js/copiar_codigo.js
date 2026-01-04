function chamar_copiar_codigo(){
    const botao = document.getElementById('botao_copiar');
    
    if(!botao){
        return;
    }

    botao.addEventListener("click", function(){
        copyToClipboard('codigo_usuario', botao);
    })
}

function copyToClipboard(elementId, botao_copiar){
    const texto_copiado = window.document.getElementById(elementId).innerText;
    navigator.clipboard.writeText(texto_copiado)
    .then(function(){
        botao_copiar.innerText = 'Copiado';
        botao_copiar.classList.remove('visualizar-editar-botao');
        botao_copiar.classList.add('codigo-copiado-botao');
    })
}

chamar_copiar_codigo();