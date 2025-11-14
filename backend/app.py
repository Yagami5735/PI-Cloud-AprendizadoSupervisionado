# backend/app.py
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import pandas as pd
from ml.app2 import treinar_modelo, avaliar_modelo, prever_novos_dados
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
    # Lê o arquivo index.html da pasta frontend
    index_path = FRONTEND_DIR / "index.html"
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(html_content)

# ... (o resto do código permanece igual)
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API está funcionando"}

def criptografar_df(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    dados = buffer.getvalue()
    criptografado = bytes([(b + 1) % 256 for b in dados])
    return criptografado

@app.post("/upload/")
async def upload_csv(file: UploadFile, campo: str = Form(...)):
    try:
        file_content = await file.read()
        df = pd.read_csv(BytesIO(file_content))

        if campo not in df.columns:
            return JSONResponse({"error": f"Campo '{campo}' não encontrado no CSV."}, status_code=400)

        y = df[[campo]]
        X = df.drop(columns=[campo])

        X_bin = criptografar_df(X)
        y_bin = criptografar_df(y)

        upload_bytes(X_bin, "X.bin", "data")
        upload_bytes(y_bin, "y.bin", "data")

        grafico_url = treinar_modelo("X.bin", "y.bin")

        return JSONResponse({
            "message": "Modelo treinado com sucesso!",
            "grafico_url": grafico_url
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/avaliar/")
async def avaliar_csv(file: UploadFile, campo: str = Form(...)):
    try:
        file_content = await file.read()
        df = pd.read_csv(BytesIO(file_content))

        if campo not in df.columns:
            return JSONResponse({"error": f"Campo '{campo}' não existe no CSV."}, status_code=400)

        y = df[[campo]]
        X = df.drop(columns=[campo])

        X_bin = criptografar_df(X)
        y_bin = criptografar_df(y)

        upload_bytes(X_bin, "X_avaliacao.bin", "data")
        upload_bytes(y_bin, "y_avaliacao.bin", "data")

        grafico_url = avaliar_modelo("X_avaliacao.bin", "y_avaliacao.bin")

        return JSONResponse({
            "message": "Avaliação realizada com sucesso!",
            "grafico_url": grafico_url
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/prever/")
async def prever_csv(file: UploadFile):
    try:
        file_content = await file.read()
        df = pd.read_csv(BytesIO(file_content))

        X_bin = criptografar_df(df)
        upload_bytes(X_bin, "X_previsao.bin", "data")

        grafico_url = prever_novos_dados("X_previsao.bin")

        return JSONResponse({
            "message": "Previsão concluída!",
            "grafico_url": grafico_url
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)