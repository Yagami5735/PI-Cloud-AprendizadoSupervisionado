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