
function consumir_api_dashboard(){
    const resultado_api = fetch('api_dashboard')
    .then(response => response.json())
    .then(data =>{
        return data;
    });

    return resultado_api;
}

function insertAfter(item_novo, item_existente){
    item_existente.parentNode.insertBefore(item_novo, item_existente.nextSibling);
}

// Essa função retira 'ul' de lista e adiciona uma mensagem informativa ao usuário
function mensagemInformativaSemItens(lista_remover, novo_texto, titulo_card){
    if(lista_remover){
        lista_remover.remove();
    }
    
    const text = document.createElement('p');
    text.classList.add('sem-itens-dashboard');
    text.style.fontSize = "14px";
    text.style.fontWeight = "400";

    text.textContent = novo_texto;
    insertAfter(text, titulo_card);
}

document.addEventListener("DOMContentLoaded", async function (){
    const tarefas_criadas_por_mim = window.document.getElementById('tarefas_criadas_por_mim');
    const tarefas_atribuidas_mim = window.document.getElementById('tarefas_atribuidas_mim');
    const lista_equipes = window.document.getElementById('lista_equipes');
    const lista_organizacoes = window.document.getElementById('lista_organizacoes');
    const titulo_minhas_equipes = window.document.getElementById('minhas_equipes_titulo');
    const minhas_organizacoes_titulo = window.document.getElementById('minhas_organizacoes_titulo');

    const result = await consumir_api_dashboard();

    tarefas_criadas_por_mim.textContent = `${result.qtd_tarefas_criadas_por_mim}`;
    tarefas_atribuidas_mim.textContent = `${result.qtd_tarefas_atribuidas_mim}`;

    if(result.minhas_organizacoes.length <= 0){
        mensagemInformativaSemItens(lista_organizacoes, 'Você ainda não faz parte de nenhuma organização.', minhas_organizacoes_titulo);

    } else{
        for(let i = 0; i < result.minhas_organizacoes.length; i++){
            const linha_organizacao = document.createElement('li');

            linha_organizacao.textContent = result.minhas_organizacoes[i];
            linha_organizacao.classList.add('item-listagem-dashboard');
            lista_organizacoes.appendChild(linha_organizacao);
        }
    }

    if(result.minhas_equipes.length <= 0){
        mensagemInformativaSemItens(lista_equipes, 'Você ainda não faz parte de nenhuma equipe.', titulo_minhas_equipes);

    } else{
        for(let i = 0; i < result.minhas_equipes.length; i++){
            const linha_equipe = document.createElement('li');

            linha_equipe.textContent = result.minhas_equipes[i];
            linha_equipe.classList.add('item-listagem-dashboard')
            lista_equipes.appendChild(linha_equipe);
        }
    }
})