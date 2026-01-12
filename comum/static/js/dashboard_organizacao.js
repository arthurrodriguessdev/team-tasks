function consumir_api_dashboard_organizacao(){
    const dados_api = fetch('api_organizacao_dashboard')

    .then(response => response.json())
    .then((data) =>{
        return data
    });

    return dados_api
}

document.addEventListener("DOMContentLoaded", async function(){
    const result = await consumir_api_dashboard_organizacao();

    const qtd_total_membros = document.getElementById('qtd_total_membros');
    const qtd_equipes = document.getElementById('qtd_equipes');
    const qtd_tarefas = document.getElementById('qtd_tarefas');

    if(result){
        qtd_total_membros.textContent = `${result.qtd_membros}`;
        qtd_equipes.textContent = `${result.qtd_equipes}`;
        qtd_tarefas.textContent = `${result.qtd_tarefas}`
    }
})