from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
import uvicorn
import os
import pandas as pd
from ml.app2 import treinar_modelo, avaliar_modelo, prever_novos_dados, carregar_modelo, normalizar_minmax, baixar_binario_do_blob
from ml.azure_utils import upload_bytes
from io import BytesIO
from pathlib import Path

BASE_DIR = Path(__file__).parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="Projeto Integrador ML", version="1.0.0")

port = int(os.getenv("PORT", 8000))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos do frontend
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_index():
    # Lendo o HTML
    index_path = FRONTEND_DIR / "index.html"
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(html_content)

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API está funcionando"}

# Função que criptografa os dados
def criptografar_df(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    dados = buffer.getvalue()
    criptografado = bytes([(b + 1) % 256 for b in dados])
    return criptografado

# Função da parte 1 - Mostrar confiança
@app.post("/upload/")
async def upload_csv(file: UploadFile, campo: str = Form(...)):
    try:
        # Recebendo o arquivo
        file_content = await file.read()
        df = pd.read_csv(BytesIO(file_content))

        # Checando se o usuário passou um campo válido
        if campo not in df.columns:
            return JSONResponse({"error": f"Campo '{campo}' não encontrado no CSV."}, status_code=400)

        # Separando em X e y
        y = df[[campo]]
        X = df.drop(columns=[campo])

        # Aplicando a criptografia
        X_bin = criptografar_df(X)
        y_bin = criptografar_df(y)

        # Jogando pro Blob
        upload_bytes(X_bin, "X.bin", "uploads")
        upload_bytes(y_bin, "y.bin", "uploads")

        # Treinando e pegando o URL do gráfico
        grafico_url = treinar_modelo("X.bin", "y.bin")

        # Retornando um Feedback
        return JSONResponse({
            "message": "Modelo treinado com sucesso!",
            "grafico_url": grafico_url
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# Função da parte 2 - Avaliar com dados novos
@app.post("/avaliar/")
async def avaliar_csv(file: UploadFile, campo: str = Form(...)):
    try:
        # Recebe e abre o novo arquivo
        file_content = await file.read()
        df = pd.read_csv(BytesIO(file_content))

        # Checa se o campo que o usuário passou é válido
        if campo not in df.columns:
            return JSONResponse({"error": f"Campo '{campo}' não existe no CSV."}, status_code=400)

        # Separa em X e y
        y = df[[campo]]
        X = df.drop(columns=[campo])

        # Criptografa
        X_bin = criptografar_df(X)
        y_bin = criptografar_df(y)

        # Faz upload
        upload_bytes(X_bin, "X_avaliacao.bin", "uploads")
        upload_bytes(y_bin, "y_avaliacao.bin", "uploads")

        # Aplica o modelo nos dados e salva o URL do gráfico gerado
        grafico_url = avaliar_modelo("X_avaliacao.bin", "y_avaliacao.bin")

        # Retorna um feedback
        return JSONResponse({
            "message": "Avaliação realizada com sucesso!",
            "grafico_url": grafico_url
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# Função da parte 3 - Prever com dados
@app.post("/prever/")
async def prever_csv(file: UploadFile):
    try:
        # Recebendo e lendo o arquivo
        file_content = await file.read()
        df = pd.read_csv(BytesIO(file_content))

        # Criptografando
        X_bin = criptografar_df(df)
        # Dando upload no Blob
        upload_bytes(X_bin, "X_previsao.bin", "uploads")

        # Aplicando dados no modelo e salvando o URL do gráfico
        grafico_url = prever_novos_dados("X_previsao.bin")

        # Mostrando um feedback
        return JSONResponse({
            "message": "Previsão concluída!",
            "grafico_url": grafico_url
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# Função pra disponibilizar o CSV com as previsões para dowload no front
@app.get("/prever/csv/")
async def download_previsao_csv():
    try:
        '''from ml.app2 import carregar_modelo, normalizar_minmax, baixar_binario_do_blob
        import pandas as pd'''
        
        # Pegando os arquivos
        X_previsao = baixar_binario_do_blob("X_previsao.bin")
        modelo = carregar_modelo("modelo_final.pkl")
        
        # Fazendo a previsão
        X_norm = normalizar_minmax(X_previsao)
        previsoes = modelo.predict(X_norm)
        
        # Juntando os valores preditos com os dados vindos do cliente para dowload
        df_completo = X_previsao.copy()
        df_completo['previsao'] = previsoes
        
        # Converte para CSV
        csv_content = df_completo.to_csv(index=False)
        
        # Retorna o CSV para download
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=previsoes.csv"}
        )
        
    except Exception as e:
        return JSONResponse({"error": f"Erro ao gerar CSV: {str(e)}"}, status_code=500)

# Função para resetar tudo
@app.post("/reset/")
async def resetar_modelo():
    return JSONResponse({
        "status": "ok", 
        "mensagem": "Interface resetada."
    })
