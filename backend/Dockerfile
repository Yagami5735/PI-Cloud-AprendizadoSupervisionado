FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libfreetype6-dev \
    libpng-dev \
    libjpeg-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar requirements primeiro para aproveitar cache
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY backend/ /app/
COPY frontend/ /app/frontend/

# Criar diretórios necessários
RUN mkdir -p /app/uploads /app/backend/ml

# Porta para Azure
ENV PORT=8000
EXPOSE 8000

# Comando para Azure App Service
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]