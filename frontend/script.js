// frontend/script.js

// URL do backend - ajuste automático para produção
const BACKEND_URL = window.location.origin;

async function enviarArquivo(url, fileInputId, campoInputId, graficoId, mensagemId, proximaEtapaId) {
  const fileInput = document.getElementById(fileInputId);
  const campo = campoInputId ? document.getElementById(campoInputId).value : null;
  const mensagem = document.getElementById(mensagemId);
  const graficoImg = document.getElementById(graficoId);

  if (!fileInput.files.length) { 
    mensagem.textContent = "Selecione um arquivo!"; 
    mensagem.style.color = "red";
    return; 
  }
  if (campoInputId && !campo.trim()) { 
    mensagem.textContent = "Informe o campo alvo (y)!"; 
    mensagem.style.color = "red";
    return; 
  }

  mensagem.textContent = "Processando...";
  mensagem.style.color = "blue";
  graficoImg.style.display = "none";

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  if (campoInputId) formData.append("campo", campo);

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 120000);

    const res = await fetch(url, { 
      method: "POST", 
      body: formData, 
      signal: controller.signal 
    });
    clearTimeout(timeoutId);

    let data;
    try {
      data = await res.json();
    } catch (e) {
      mensagem.textContent = "Resposta inválida do servidor.";
      mensagem.style.color = "red";
      console.error("Invalid JSON response", e);
      return;
    }

    if (!res.ok) {
      let erros = [];
      if (data.mensagens) erros = data.mensagens;
      else if (data.detail?.mensagens) erros = data.detail.mensagens;
      else if (data.error) erros = [data.error];
      else erros = [data.message || "Erro desconhecido"];
      mensagem.textContent = "Erro: " + erros.join(", ");
      mensagem.style.color = "red";
      return;
    }

    if (data.grafico_url) {
      graficoImg.src = data.grafico_url;
      graficoImg.style.display = "block";
    }

    mensagem.textContent = data.message || "Sucesso!";
    mensagem.style.color = "green";
    
    if (proximaEtapaId) {
      document.getElementById(proximaEtapaId).style.display = "block";
    }

  } catch (err) {
    console.error(err);
    mensagem.style.color = "red";
    if (err.name === "AbortError") {
      mensagem.textContent = "Tempo de processamento excedido (2 minutos). Tente novamente.";
    } else {
      mensagem.textContent = "Erro ao enviar ou processar o arquivo: " + (err.message || err);
    }
  }
}

function gerarModelo() {
  enviarArquivo(`${BACKEND_URL}/upload/`, "file_treino", "campo_treino", "grafico_treino", "mensagem_treino", "etapa2");
}

function avaliarModelo() {
  enviarArquivo(`${BACKEND_URL}/avaliar/`, "file_avaliacao", "campo_avaliacao", "grafico_avaliacao", "mensagem_avaliacao", "etapa3");
}

function preverNovosDados() {
  enviarArquivo(`${BACKEND_URL}/prever/`, "file_previsao", null, "grafico_previsao", "mensagem_previsao", null);
  buscarDadosPrevisao();
}

// ✅ ADICIONE APENAS ESTAS FUNÇÕES AO FINAL DO script.js

// Variável global para armazenar os dados de previsão
let dadosPrevisao = null;

// ✅ FUNÇÃO PARA BUSCAR DADOS CSV DA PREVISÃO
async function buscarDadosPrevisao() {
  try {
    const response = await fetch(`${BACKEND_URL}/prever/csv/`);
    if (response.ok) {
      const csvText = await response.text();
      dadosPrevisao = csvText;
      adicionarBotaoDownload();
    }
  } catch (error) {
    console.error('Erro ao buscar CSV:', error);
  }
}

// ✅ FUNÇÃO PARA MOSTRAR BOTÃO DE DOWNLOAD
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

// ✅ FUNÇÃO PARA BAIXAR O CSV
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

// ✅ FUNÇÃO PARA RESETAR A PÁGINA
function resetarPagina() {
  // Esconde todas as etapas exceto a primeira
  document.getElementById('etapa1').style.display = 'block';
  document.getElementById('etapa2').style.display = 'none';
  document.getElementById('etapa3').style.display = 'none';
  
  // Limpa todas as mensagens
  document.getElementById('mensagem_treino').textContent = '';
  document.getElementById('mensagem_avaliacao').textContent = '';
  document.getElementById('mensagem_previsao').textContent = '';
  
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
  
  // Remove o container de download se existir
  const downloadContainer = document.getElementById('download-container');
  if (downloadContainer) {
    downloadContainer.remove();
  }
  
  // Limpa os dados de previsão
  dadosPrevisao = null;
  
  alert('Página resetada com sucesso! Pronto para começar novamente.');
}

// Verificar se o backend está online ao carregar a página
document.addEventListener('DOMContentLoaded', function() {
  fetch(`${BACKEND_URL}/health`)
    .then(response => response.json())
    .then(data => {
      console.log('Backend status:', data.status);
    })
    .catch(error => {
      console.error('Erro ao conectar com o backend:', error);
    });
});