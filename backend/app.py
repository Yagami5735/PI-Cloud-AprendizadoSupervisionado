from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import pandas as pd
from io import BytesIO

from ml.app2 import treinar_modelo, avaliar_modelo, prever_novos_dados
from ml.azure_utils import upload_arquivo

# ==========================
# CONFIGURAÇÕES DE DIRETÓRIO
# ==========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

# CORS liberado
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Arquivos estáticos
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# ==========================
# FRONTEND
# ==========================

@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

# ==========================
# FUNÇÃO DE CRIPTOGRAFIA SIMPLES
# ==========================
def criptografar_df(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    dados = buffer.getvalue()
    criptografado = bytes([(b + 1) % 256 for b in dados])
    return criptografado

# ==========================
# 1️⃣ ENDPOINT TREINAR MODELO
# ==========================
@app.post("/upload/")
async def upload_csv(file: UploadFile, campo: str = Form(...)):
    try:
        temp_path = os.path.join(UPLOAD_DIR, "original.csv")
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        df = pd.read_csv(temp_path)

        if campo not in df.columns:
            return JSONResponse({"error": f"Campo '{campo}' não encontrado no CSV."}, status_code=400)

        y = df[[campo]]
        X = df.drop(columns=[campo])

        X_bin = criptografar_df(X)
        y_bin = criptografar_df(y)

        X_path = os.path.join(UPLOAD_DIR, "X.bin")
        y_path = os.path.join(UPLOAD_DIR, "y.bin")
        with open(X_path, "wb") as f: f.write(X_bin)
        with open(y_path, "wb") as f: f.write(y_bin)

        upload_arquivo(X_path, "X.bin")
        upload_arquivo(y_path, "y.bin")

        grafico_url = treinar_modelo("X.bin", "y.bin")

        return JSONResponse({
            "message": "Modelo treinado com sucesso!",
            "grafico_url": grafico_url
        })

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ==========================
# 2️⃣ ENDPOINT AVALIAR MODELO
# ==========================
@app.post("/avaliar/")
async def avaliar_csv(file: UploadFile, campo: str = Form(...)):
    try:
        temp_path = os.path.join(UPLOAD_DIR, "avaliacao.csv")
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        df = pd.read_csv(temp_path)

        if campo not in df.columns:
            return JSONResponse({"error": f"Campo '{campo}' não existe no CSV."}, status_code=400)

        y = df[[campo]]
        X = df.drop(columns=[campo])

        X_bin = criptografar_df(X)
        y_bin = criptografar_df(y)

        X_path = os.path.join(UPLOAD_DIR, "X_avaliacao.bin")
        y_path = os.path.join(UPLOAD_DIR, "y_avaliacao.bin")
        with open(X_path, "wb") as f: f.write(X_bin)
        with open(y_path, "wb") as f: f.write(y_bin)

        upload_arquivo(X_path, "X_avaliacao.bin")
        upload_arquivo(y_path, "y_avaliacao.bin")

        grafico_url = avaliar_modelo("X_avaliacao.bin", "y_avaliacao.bin")

        return JSONResponse({
            "message": "Avaliação realizada com sucesso!",
            "grafico_url": grafico_url
        })

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ==========================
# 3️⃣ ENDPOINT PREVER
# ==========================
@app.post("/prever/")
async def prever_csv(file: UploadFile):
    try:
        temp_path = os.path.join(UPLOAD_DIR, "previsao.csv")
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        df = pd.read_csv(temp_path)

        X_bin = criptografar_df(df)

        X_path = os.path.join(UPLOAD_DIR, "X_previsao.bin")
        with open(X_path, "wb") as f: f.write(X_bin)

        upload_arquivo(X_path, "X_previsao.bin")

        grafico_url = prever_novos_dados("X_previsao.bin")

        return JSONResponse({
            "message": "Previsão concluída!",
            "grafico_url": grafico_url
        })

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ==========================
# RESET (opcional)
# ==========================
@app.post("/reset/")
async def resetar_modelo():
    return JSONResponse({
        "status": "ok",
        "mensagem": "Interface resetada."
    })
