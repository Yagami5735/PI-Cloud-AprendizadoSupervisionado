# backend/ml/app2.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error
import os
from fastapi import HTTPException
from .azure_utils import download_arquivo, upload_arquivo
from io import BytesIO
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------- util: descriptografa bytes (sua "subtrair 1") ----------
def descriptografar_binario(bin_data: bytes) -> pd.DataFrame:
    dados = bytes([(b - 1) % 256 for b in bin_data])
    buffer = BytesIO(dados)
    df = pd.read_csv(buffer)
    return df

# ---------- util: baixa binário do Blob e retorna DataFrame ----------
def baixar_binario_do_blob(blob_name: str) -> pd.DataFrame:
    url = download_arquivo(blob_name)
    # download do conteúdo binário
    r = requests.get(url)
    r.raise_for_status()
    df = descriptografar_binario(r.content)
    return df

# ---------- validação ----------
def validar_dados(X, y):
    erros = []
    if len(X) < 20:
        erros.append(f"Poucos dados ({len(X)} linhas). Mínimo: 20.")
    tipos_invalidos = X.select_dtypes(exclude=[np.number]).columns.tolist()
    if tipos_invalidos:
        erros.append(f"Variáveis não numéricas: {tipos_invalidos}")
    if erros:
        raise HTTPException(status_code=400, detail={"status": "erro_validacao", "mensagens": erros})

# ---------- normalização MinMax (aplicada separadamente por dataset) ----------
def normalizar_minmax(X: pd.DataFrame) -> pd.DataFrame:
    X_norm = X.copy()
    for campo in X.columns:
        denom = X[campo].max() - X[campo].min()
        if denom == 0 or pd.isna(denom):
            X_norm[campo] = 0
        else:
            X_norm[campo] = (X[campo] - X[campo].min()) / denom
    return X_norm

# ===========================
# treinar_modelo (mantido)
# ===========================
def treinar_modelo(X_blob="X.bin", y_blob="y.bin"):
    X = baixar_binario_do_blob(X_blob)
    y = baixar_binario_do_blob(y_blob)
    if y.ndim > 1 and y.shape[1] > 1:
        y = y.iloc[:, 0]
    df = pd.concat([X, y], axis=1).dropna()
    X, y = df.iloc[:, :-1], df.iloc[:, -1]
    validar_dados(X, y)
    X = normalizar_minmax(X)

    tscv = TimeSeriesSplit(n_splits=5)
    fig, axes = plt.subplots(tscv.get_n_splits() + 1, 2, figsize=(15, 5 * (tscv.get_n_splits() + 1)))
    r2_test_lista, rmse_test_lista = [], []

    for i, (train_idx, test_idx) in enumerate(tscv.split(X)):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        modelo = LinearRegression().fit(X_train, y_train)
        y_pred_train = modelo.predict(X_train)
        y_pred_test = modelo.predict(X_test)

        r2_test = modelo.score(X_test, y_test)
        rmse_test = mean_squared_error(y_test, y_pred_test) ** 0.5
        r2_test_lista.append(r2_test)
        rmse_test_lista.append(rmse_test)

        ax1, ax2 = axes[i, 0], axes[i, 1]
        ax1.plot(y.values, label='Real', color='blue')
        ax1.plot(range(len(y_pred_train)), y_pred_train, color='red', label='Treino')
        ax1.plot(range(len(y_pred_train), len(y_pred_train)+len(y_pred_test)), y_pred_test, color='black', label='Teste')
        ax1.set_title(f'Fold {i+1} — Evolução temporal')
        ax1.legend(); ax1.grid(alpha=0.3)

        ax2.scatter(y_test, y_pred_test, color='blue')
        ax2.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
        ax2.set_title(f'Real vs Predito — Fold {i+1}')
        ax2.text(0.05, 0.95,
                 f'R²: {r2_test:.4f}\nRMSE: {rmse_test:.2f}',
                 transform=ax2.transAxes, fontsize=10,
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                 verticalalignment='top')

    mean_r2, mean_rmse = np.mean(r2_test_lista), np.mean(rmse_test_lista)
    ax_r2, ax_rmse = axes[-1, 0], axes[-1, 1]
    ax_r2.plot(range(1, len(r2_test_lista)+1), r2_test_lista, marker='o', label='R²')
    ax_r2.axhline(mean_r2, color='red', linestyle='--', label=f'Média={mean_r2:.4f}')
    ax_r2.legend(); ax_r2.grid(alpha=0.3)
    ax_rmse.plot(range(1, len(rmse_test_lista)+1), rmse_test_lista, marker='s', label='RMSE')
    ax_rmse.axhline(mean_rmse, color='red', linestyle='--', label=f'Média={mean_rmse:.2f}')
    ax_rmse.legend(); ax_rmse.grid(alpha=0.3)

    plt.tight_layout()
    img_path = os.path.join(BASE_DIR, "cv_plot2.png")
    plt.savefig(img_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

    upload_arquivo(img_path, "cv_plot2.png")
    blob_url = download_arquivo("cv_plot2.png")
    return blob_url

# ===========================
# avaliar_modelo (corrigido para retornar URL do gráfico)
# ===========================
def avaliar_modelo(X_blob="X.bin", y_blob="y.bin"):
    X = baixar_binario_do_blob(X_blob)
    y = baixar_binario_do_blob(y_blob)
    if y.ndim > 1 and y.shape[1] > 1:
        y = y.iloc[:, 0]

    df = pd.concat([X, y], axis=1).dropna()
    X, y = df.iloc[:, :-1], df.iloc[:, -1]
    validar_dados(X, y)

    X_norm = normalizar_minmax(X)
    modelo = LinearRegression().fit(X_norm, y)
    y_pred = modelo.predict(X_norm)
    rmse = mean_squared_error(y, y_pred) ** 0.5
    r2 = modelo.score(X_norm, y)

    # Gera gráfico avaliação (Real vs Predito + info)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    ax1.plot(X_norm.index, y, label='Real', color='blue', linewidth=2)
    ax1.plot(X_norm.index, y_pred, label='Predito', color='red', linewidth=2)
    ax1.set_title('Evolução Temporal', fontsize=13)
    ax1.set_xlabel('Índice'); ax1.set_ylabel('Var. Alvo (Y)')
    ax1.legend(); ax1.grid(True, alpha=0.3)

    ax2.scatter(y, y_pred, color='blue')
    y_min = min(y.min(), y_pred.min()); y_max = max(y.max(), y_pred.max())
    identidade_range = np.linspace(y_min, y_max, 100)
    ax2.plot(identidade_range, identidade_range, 'r--', linewidth=2)
    ax2.set_title('Real vs Predito', fontsize=13)
    ax2.set_xlabel('Valor Real (y)'); ax2.set_ylabel('Valor Predito (ŷ)')
    ax2.text(0.05, 0.95,
             f'RMSE: {rmse:.2f}\nR²: {r2:.4f}', transform=ax2.transAxes,
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
             verticalalignment='top', fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    img_path = os.path.join(BASE_DIR, "avaliacao_plot.png")
    plt.savefig(img_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

    upload_arquivo(img_path, "avaliacao_plot.png")
    blob_url = download_arquivo("avaliacao_plot.png")
    return blob_url

# ===========================
# prever_novos_dados (ajustado: treina modelo com dados de treino e aplica em X_blob)
# ===========================
def prever_novos_dados(X_blob="X_previsao.bin"):
    # 1) Baixa dados de treino originais (assumidos como X.bin e y.bin no container)
    try:
        X_train = baixar_binario_do_blob("X.bin")
        y_train = baixar_binario_do_blob("y.bin")
    except Exception as e:
        # Se não encontrar os arquivos de treino, devolve erro claro
        raise HTTPException(status_code=400, detail=f"Arquivos de treino (X.bin/y.bin) não encontrados no Blob: {e}")

    if y_train.ndim > 1 and y_train.shape[1] > 1:
        y_train = y_train.iloc[:, 0]

    # Preprocessa treino
    df_train = pd.concat([X_train, y_train], axis=1).dropna()
    X_train, y_train = df_train.iloc[:, :-1], df_train.iloc[:, -1]
    validar_dados(X_train, y_train)
    X_train_norm = normalizar_minmax(X_train)

    # Treina modelo final
    modelo = LinearRegression().fit(X_train_norm, y_train)

    # 2) Baixa os dados novos (X_blob) e faz predict
    X_novos = baixar_binario_do_blob(X_blob)
    # assume X_novos tem mesmas colunas; normaliza separadamente (como feito no restante do pipeline)
    X_novos_norm = normalizar_minmax(X_novos)

    # Prever
    y_pred = modelo.predict(X_novos_norm)

    # Gera gráfico de predição
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(X_novos_norm.index, y_pred, label='Predição', linewidth=2, color='red')
    ax.set_title('Predição', fontsize=13)
    ax.set_xlabel('Índice'); ax.set_ylabel('Var. Alvo (Y)')
    ax.legend(); ax.grid(True, alpha=0.3)
    plt.tight_layout()

    img_path = os.path.join(BASE_DIR, "prever_plot.png")
    plt.savefig(img_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

    upload_arquivo(img_path, "prever_plot.png")
    blob_url = download_arquivo("prever_plot.png")
    return blob_url
