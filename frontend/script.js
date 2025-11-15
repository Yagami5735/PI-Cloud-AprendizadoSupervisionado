// Variável global para armazenar os dados de previsão
let dadosPrevisao = null;

async function gerarModelo() {
    const fileInput = document.getElementById('file_treino');
    const campoInput = document.getElementById('campo_treino');
    const file = fileInput.files[0];
    const campo = campoInput.value;
    const mensagemDiv = document.getElementById('mensagem_treino');
    
    if (!file || !campo) {
        mensagemDiv.innerHTML = '<span class="erro">Por favor, selecione um arquivo e informe o campo alvo.</span>';
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('campo', campo);
    
    try {
        mensagemDiv.innerHTML = '<span class="processando">Treinando modelo...</span>';
        
        const response = await fetch('/upload/', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Mostra o gráfico
            const grafico = document.getElementById('grafico_treino');
            grafico.src = result.grafico_url + '?t=' + new Date().getTime();
            grafico.style.display = 'block';
            grafico.alt = 'Gráfico de Treinamento';
            
            mensagemDiv.innerHTML = '<span class="sucesso">' + result.message + '</span>';
            
            // Mostra a próxima etapa
            document.getElementById('etapa2').style.display = 'block';
            
        } else {
            mensagemDiv.innerHTML = '<span class="erro">Erro: ' + result.error + '</span>';
        }
    } catch (error) {
        console.error('Erro:', error);
        mensagemDiv.innerHTML = '<span class="erro">Erro ao treinar modelo</span>';
    }
}

async function avaliarModelo() {
    const fileInput = document.getElementById('file_avaliacao');
    const campoInput = document.getElementById('campo_avaliacao');
    const file = fileInput.files[0];
    const campo = campoInput.value;
    const mensagemDiv = document.getElementById('mensagem_avaliacao');
    
    if (!file || !campo) {
        mensagemDiv.innerHTML = '<span class="erro">Por favor, selecione um arquivo e informe o campo alvo.</span>';
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('campo', campo);
    
    try {
        mensagemDiv.innerHTML = '<span class="processando">Avaliando modelo...</span>';
        
        const response = await fetch('/avaliar/', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Mostra o gráfico
            const grafico = document.getElementById('grafico_avaliacao');
            grafico.src = result.grafico_url + '?t=' + new Date().getTime();
            grafico.style.display = 'block';
            grafico.alt = 'Gráfico de Avaliação';
            
            mensagemDiv.innerHTML = '<span class="sucesso">' + result.message + '</span>';
            
            // Mostra a próxima etapa
            document.getElementById('etapa3').style.display = 'block';
            
        } else {
            mensagemDiv.innerHTML = '<span class="erro">Erro: ' + result.error + '</span>';
        }
    } catch (error) {
        console.error('Erro:', error);
        mensagemDiv.innerHTML = '<span class="erro">Erro ao avaliar modelo</span>';
    }
}

async function preverNovosDados() {
    const fileInput = document.getElementById('file_previsao');
    const file = fileInput.files[0];
    const mensagemDiv = document.getElementById('mensagem_previsao');
    
    if (!file) {
        mensagemDiv.innerHTML = '<span class="erro">Por favor, selecione um arquivo CSV para previsão.</span>';
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        mensagemDiv.innerHTML = '<span class="processando">Processando previsão...</span>';
        
        const response = await fetch('/prever/', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Mostra o gráfico
            const grafico = document.getElementById('grafico_previsao');
            grafico.src = result.grafico_url + '?t=' + new Date().getTime();
            grafico.style.display = 'block';
            grafico.alt = 'Gráfico de Previsão';
            
            mensagemDiv.innerHTML = '<span class="sucesso">' + result.message + '</span>';
            
            // Busca os dados CSV da previsão
            await buscarDadosPrevisao();
            
        } else {
            mensagemDiv.innerHTML = '<span class="erro">Erro: ' + result.error + '</span>';
        }
    } catch (error) {
        console.error('Erro:', error);
        mensagemDiv.innerHTML = '<span class="erro">Erro ao fazer previsão</span>';
    }
}

// Função para buscar os dados CSV da previsão
async function buscarDadosPrevisao() {
    try {
        const response = await fetch('/prever/csv/');
        if (response.ok) {
            const csvText = await response.text();
            dadosPrevisao = csvText;
            adicionarBotaoDownload();
        }
    } catch (error) {
        console.error('Erro ao buscar CSV:', error);
    }
}

// Função para mostrar o botão de download
function adicionarBotaoDownload() {
    // Remove o container anterior se existir
    const containerAnterior = document.getElementById('download-container');
    if (containerAnterior) {
        containerAnterior.remove();
    }
    
    // Cria novo container de download
    const downloadContainer = document.createElement('div');
    downloadContainer.id = 'download-container';
    downloadContainer.innerHTML = `
        <h3>📊 Download das Previsões</h3>
        <button onclick="baixarCSV()" class="btn-download">Baixar CSV com Previsões</button>
    `;
    
    // Adiciona após a etapa 3
    const etapa3 = document.getElementById('etapa3');
    etapa3.appendChild(downloadContainer);
}

// Função para baixar o CSV
function baixarCSV() {
    if (!dadosPrevisao) {
        alert('Nenhum dado de previsão disponível para download.');
        return;
    }
    
    // Cria um blob com os dados CSV
    const blob = new Blob([dadosPrevisao], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    
    // Configura o download
    link.href = url;
    link.setAttribute('download', 'previsoes.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    alert('CSV baixado com sucesso!');
}

// Função para resetar a página
function resetarPagina() {
    // Esconde todas as etapas exceto a primeira
    document.getElementById('etapa1').style.display = 'block';
    document.getElementById('etapa2').style.display = 'none';
    document.getElementById('etapa3').style.display = 'none';
    
    // Limpa todas as mensagens
    document.getElementById('mensagem_treino').innerHTML = '';
    document.getElementById('mensagem_avaliacao').innerHTML = '';
    document.getElementById('mensagem_previsao').innerHTML = '';
    
    // Esconde todos os gráficos
    document.getElementById('grafico_treino').style.display = 'none';
    document.getElementById('grafico_avaliacao').style.display = 'none';
    document.getElementById('grafico_previsao').style.display = 'none';
    
    // Limpa os campos de arquivo
    document.getElementById('file_treino').value = '';
    document.getElementById('file_avaliacao').value = '';
    document.getElementById('file_previsao').value = '';
    
    // Limpa os campos de texto
    document.getElementById('campo_treino').value = '';
    document.getElementById('campo_avaliacao').value = '';
    
    // Esconde o container de download se existir
    const downloadContainer = document.getElementById('download-container');
    if (downloadContainer) {
        downloadContainer.style.display = 'none';
    }
    
    // Limpa os dados de previsão
    dadosPrevisao = null;
    
    alert('Página resetada com sucesso! Pronto para começar novamente.');
}