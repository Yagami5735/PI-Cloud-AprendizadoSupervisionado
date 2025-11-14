async function enviarArquivo(url, fileInputId, campoInputId, graficoId, mensagemId, proximaEtapaId) {
  const fileInput = document.getElementById(fileInputId);
  const campo = campoInputId ? document.getElementById(campoInputId).value : null;
  const mensagem = document.getElementById(mensagemId);
  const graficoImg = document.getElementById(graficoId);

  if (!fileInput.files.length) { mensagem.textContent = "Selecione um arquivo!"; return; }
  if (campoInputId && !campo.trim()) { mensagem.textContent = "Informe o campo alvo (y)!"; return; }

  mensagem.textContent = "Processando...";
  graficoImg.style.display = "none";

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  if (campoInputId) formData.append("campo", campo);

  try {
    const res = await fetch(url, { method: "POST", body: formData });
    const data = await res.json();

    if (!res.ok) {
      let erros = [];
      if (data.mensagens) erros = data.mensagens;
      else if (data.detail?.mensagens) erros = data.detail.mensagens;
      else erros = [data.error || "Erro desconhecido"];
      mensagem.textContent = "Erro: " + erros.join(", ");
      return;
    }

    if (data.grafico_url) {
      graficoImg.src = data.grafico_url;  // diretamente a URL retornada
      graficoImg.style.display = "block";
    }

    mensagem.textContent = data.message || "Sucesso!";

    // Mostrar próxima etapa
    if (proximaEtapaId) document.getElementById(proximaEtapaId).style.display = "block";

  } catch (err) {
    console.error(err);
    mensagem.textContent = "Erro ao enviar ou processar o arquivo: " + err.message;
  }
}

// Funções específicas para cada etapa
function gerarModelo() {
  enviarArquivo("http://127.0.0.1:8000/upload/", "file_treino", "campo_treino", "grafico_treino", "mensagem_treino", "etapa2");
}

function avaliarModelo() {
  enviarArquivo("http://127.0.0.1:8000/avaliar/", "file_avaliacao", "campo_avaliacao", "grafico_avaliacao", "mensagem_avaliacao", "etapa3");
}

function preverNovosDados() {
  enviarArquivo("http://127.0.0.1:8000/prever/", "file_previsao", null, "grafico_previsao", "mensagem_previsao", null);
}
