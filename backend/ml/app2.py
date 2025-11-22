import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error
from fastapi import HTTPException
from .azure_utils import download_bytes, upload_bytes, salvar_modelo, carregar_modelo, download_arquivo
from io import BytesIO

# Função para descriptografar os dados
def descriptografar_binario(bin_data: bytes) -> pd.DataFrame:
    dados = bytes([(b - 1) % 256 for b in bin_data])
    buffer = BytesIO(dados)
    df = pd.read_csv(buffer)
    return df

# Função que baixa o binário do Blob e descriptografa
def baixar_binario_do_blob(blob_name: str) -> pd.DataFrame:
    bin_data = download_bytes(blob_name, "uploads")
    df = descriptografar_binario(bin_data)
    return df

# Função que valida os dados
def validar_dados(X, y):
    erros = []
    # Checa se há mais que 20 dados
    if len(X) < 20:
        erros.append(f"Poucos dados ({len(X)} linhas). Mínimo: 20.")
    # Checa se há tipos inválidos
    tipos_invalidos = X.select_dtypes(exclude=[np.number]).columns.tolist()
    if tipos_invalidos:
        erros.append(f"Variáveis não numéricas: {tipos_invalidos}")
    if erros:
        raise HTTPException(status_code=400, detail={"status": "erro_validacao", "mensagens": erros})

# Função para aplicar nomalização Min-Max
def normalizar_minmax(X: pd.DataFrame) -> pd.DataFrame:
    X_norm = X.copy()
    # Pra cada campo, aplicar a min max
    for campo in X.columns:
        denom = X[campo].max() - X[campo].min()
        if denom == 0 or pd.isna(denom):
            X_norm[campo] = 0
        else:
            X_norm[campo] = (X[campo] - X[campo].min()) / denom
    return X_norm

# Converte os gráficos para bytes
def figura_para_bytes(fig) -> bytes:
    buffer = BytesIO()
    fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    return buffer.getvalue()

# Função Treinar Modelo
def treinar_modelo(X_blob="X.bin", y_blob="y.bin"):
    # Baixa do Blob os arquivos
    X = baixar_binario_do_blob(X_blob)
    y = baixar_binario_do_blob(y_blob)
    if y.ndim > 1 and y.shape[1] > 1:
        y = y.iloc[:, 0]
    df = pd.concat([X, y], axis=1)
    
    # Tapando os NA com a média do valor anterior e do próximo
    df = df.interpolate(method='linear')
    
    X, y = df.iloc[:, :-1], df.iloc[:, -1]
    # Valida os dados
    validar_dados(X, y)
    # Aplica normalização em X
    X = normalizar_minmax(X)

    # Fazendo o CV com 5 splits
    tscv = TimeSeriesSplit(n_splits=5)
    fig, axes = plt.subplots(tscv.get_n_splits() + 1, 2, figsize=(15, 5 * (tscv.get_n_splits() + 1)))
    r2_test_lista, rmse_test_lista = [], []

    for i, (train_idx, test_idx) in enumerate(tscv.split(X)):
        # Separando em x e y train e test
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        # Aplicando o modelo linear
        modelo = LinearRegression().fit(X_train, y_train)
        y_pred_train = modelo.predict(X_train)
        y_pred_test = modelo.predict(X_test)

        # Calculando as métricas
        r2_test = modelo.score(X_test, y_test)
        rmse_test = mean_squared_error(y_test, y_pred_test) ** 0.5
        r2_test_lista.append(r2_test)
        rmse_test_lista.append(rmse_test)

        # Plotando os gráficos com as métricas
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
    # Plotando gráfico final com a média do desempenho das folds
    mean_r2, mean_rmse = np.mean(r2_test_lista), np.mean(rmse_test_lista)
    ax_r2, ax_rmse = axes[-1, 0], axes[-1, 1]
    ax_r2.plot(range(1, len(r2_test_lista)+1), r2_test_lista, marker='o', label='R²')
    ax_r2.axhline(mean_r2, color='red', linestyle='--', label=f'Média={mean_r2:.4f}')
    ax_r2.legend(); ax_r2.grid(alpha=0.3)
    ax_rmse.plot(range(1, len(rmse_test_lista)+1), rmse_test_lista, marker='s', label='RMSE')
    ax_rmse.axhline(mean_rmse, color='red', linestyle='--', label=f'Média={mean_rmse:.2f}')
    ax_rmse.legend(); ax_rmse.grid(alpha=0.3)

    plt.tight_layout()
    
    # Convertendo a imagem para bytes
    img_bytes = figura_para_bytes(fig)
    # Salvndo ela no Blob
    upload_bytes(img_bytes, "cv_plot2.png", "uploads")
    plt.close(fig)
    
    # Salva o modelo final treinado
    modelo_final = LinearRegression().fit(X, y)
    salvar_modelo(modelo_final, "modelo_final.pkl")

    # Retornando o ULR da imagem
    blob_url = download_arquivo("cv_plot2.png", "uploads")
    return blob_url

# Função Avaliar o Modelo
def avaliar_modelo(X_blob="X_avaliacao.bin", y_blob="y_avaliacao.bin"):
    # Recebe os arquivos binários do Blob
    X = baixar_binario_do_blob(X_blob)
    y = baixar_binario_do_blob(y_blob)
    if y.ndim > 1 and y.shape[1] > 1:
        y = y.iloc[:, 0]

    df = pd.concat([X, y], axis=1)
    
    # Tapando os NA com a média do valor anterior e do próximo
    df = df.interpolate(method='linear')
    
    X, y = df.iloc[:, :-1], df.iloc[:, -1]
    
    # Valida os dados
    validar_dados(X, y)
    # Aplica Min Max nos novos dados
    X_norm = normalizar_minmax(X)
    
    # Abre o modelo treinado
    try:
        modelo = carregar_modelo("modelo_final.pkl")
    except:
        modelo = LinearRegression().fit(X_norm, y)
        salvar_modelo(modelo, "modelo_final.pkl")
    
    y_pred = modelo.predict(X_norm)
    rmse = mean_squared_error(y, y_pred) ** 0.5
    r2 = modelo.score(X_norm, y)

    # Fazendo o gráfico da avaliação com as métricas
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
    
    # Jogando o gráfico no Blob 
    img_bytes = figura_para_bytes(fig)
    upload_bytes(img_bytes, "avaliacao_plot.png", "uploads")
    plt.close(fig)

    # Recebendo o URL do gráfico do Blob e retornando ele
    blob_url = download_arquivo("avaliacao_plot.png", "uploads")
    return blob_url

# Função para prever novos dados
def prever_novos_dados(X_blob="X_previsao.bin"):
    # Carrega modelo treinado
    try:
        modelo = carregar_modelo("modelo_final.pkl")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Modelo não encontrado. Treine um modelo primeiro: {e}")

    # Reebe os novos dados
    X_novos = baixar_binario_do_blob(X_blob)
    # Tapando os NA com a média do valor anterior e do próximo
    X_novos = X_novos.interpolate(method='linear')
    # Normaliza eles
    X_novos_norm = normalizar_minmax(X_novos)
    # Faz o predict
    y_pred = modelo.predict(X_novos_norm)

    # Fazendo o gráfico de predição
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(X_novos_norm.index, y_pred, label='Predição', linewidth=2, color='red')
    ax.set_title('Predição', fontsize=13)
    ax.set_xlabel('Índice'); ax.set_ylabel('Var. Alvo (Y)')
    ax.legend(); ax.grid(True, alpha=0.3)
    plt.tight_layout()

    # Jogando o gráfico no Blob
    img_bytes = figura_para_bytes(fig)
    upload_bytes(img_bytes, "prever_plot.png", "uploads")
    plt.close(fig)

    # Puando a URL do gráfico do Blob e retornando
    blob_url = download_arquivo("prever_plot.png", "uploads")
    return blob_url
