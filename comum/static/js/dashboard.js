
function consumir_api_dashboard(){
    const resultado_api = fetch('api_dashboard')
    .then(response => response.json())
    .then(data =>{
        console.log(data)
        return data;
    });

    return resultado_api;
}

document.addEventListener("DOMContentLoaded", async function (){
    const tarefas_criadas_por_mim = window.document.getElementById('tarefas_criadas_por_mim');
    const tarefas_atribuidas_mim = window.document.getElementById('tarefas_atribuidas_mim');
    const lista_equipes = window.document.getElementById('lista_equipes');
    const lista_organizacoes = window.document.getElementById('lista_organizacoes');

    const result = await consumir_api_dashboard();

    tarefas_criadas_por_mim.textContent = `${result.qtd_tarefas_criadas_por_mim}`;
    tarefas_atribuidas_mim.textContent = `${result.qtd_tarefas_atribuidas_mim}`;

    for(let i = 0; i < result.minhas_equipes.length; i++){
        const linha_equipe = document.createElement('li');

        linha_equipe.textContent = result.minhas_equipes[i];
        linha_equipe.classList.add('item-listagem-dashboard')
        lista_equipes.appendChild(linha_equipe);
    }

    for(let i = 0; i < result.minhas_organizacoes.length; i++){
        const linha_organizacao = document.createElement('li');

        linha_organizacao.textContent = result.minhas_organizacoes[i];
        linha_organizacao.classList.add('item-listagem-dashboard');
        lista_organizacoes.appendChild(linha_organizacao);
    }
})