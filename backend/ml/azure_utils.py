import os
import logging
from azure.storage.blob import BlobServiceClient
import pickle
from io import BytesIO

# Configurar logging
logger = logging.getLogger(__name__)

# Verifica se as variáveis existem, mas não quebra o app na importação
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
AZURE_STORAGE_ACCOUNT_NAME = os.getenv('AZURE_STORAGE_ACCOUNT_NAME') 
AZURE_STORAGE_ACCOUNT_KEY = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')

# Log para debug
logger.info(f"Azure Storage Account Name: {AZURE_STORAGE_ACCOUNT_NAME}")
logger.info(f"Azure Storage Connection String configured: {bool(AZURE_STORAGE_CONNECTION_STRING)}")

def get_blob_service_client():
    if not AZURE_STORAGE_CONNECTION_STRING:
        raise RuntimeError("Azure env vars missing - cannot create blob service client")
    try:
        return BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    except Exception as e:
        logger.error(f"Error creating blob service client: {e}")
        raise

# Função para baixar o arquivo
def download_arquivo(blob_name: str, container_name: str) -> str:
    if not AZURE_STORAGE_CONNECTION_STRING:
        raise RuntimeError("Azure env vars missing - cannot get file URL")
    
    try:
        from datetime import datetime, timedelta
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions
        
        blob_service_client = get_blob_service_client()
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        # Gera um token com acesso público temporário
        sas_token = generate_blob_sas(
            account_name=AZURE_STORAGE_ACCOUNT_NAME,
            container_name=container_name,
            blob_name=blob_name,
            account_key=AZURE_STORAGE_ACCOUNT_KEY,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=24)  # Válido por 24 horas
        )
        
        # Retorna a URL
        url = f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
        logger.info(f"Generated SAS URL for: {blob_name}")
        return url
        
    except Exception as e:
        logger.error(f"Error generating file URL: {e}")
        raise

# Função para fazer upload de arquivos no Blob
def upload_arquivo(local_file_name: str, blob_name: str = None, container_name: str = "uploads"):
    if not AZURE_STORAGE_CONNECTION_STRING:
        raise RuntimeError("Azure env vars missing - cannot upload file")
    
    try:
        if blob_name is None:
            blob_name = os.path.basename(local_file_name)
        
        blob_service_client = get_blob_service_client()
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        with open(local_file_name, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        
        logger.info(f"File uploaded: {local_file_name} -> {blob_name}")
        return blob_client.url
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise

# Função para fazer upload de bytes
def upload_bytes(data: bytes, blob_name: str, container_name: str):
    if not AZURE_STORAGE_CONNECTION_STRING:
        raise RuntimeError("Azure env vars missing - cannot upload bytes")
    
    try:
        blob_service_client = get_blob_service_client()
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        blob_client.upload_blob(data, overwrite=True)
        
        logger.info(f"Bytes uploaded: {blob_name} ({len(data)} bytes)")
        return blob_client.url
    except Exception as e:
        logger.error(f"Error uploading bytes: {e}")
        raise

# Função para baixar os bytes
def download_bytes(blob_name: str, container_name: str) -> bytes:
    if not AZURE_STORAGE_CONNECTION_STRING:
        raise RuntimeError("Azure env vars missing - cannot download bytes")
    
    try:
        blob_service_client = get_blob_service_client()
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        download_stream = blob_client.download_blob()
        data = download_stream.readall()
        
        logger.info(f"Bytes downloaded: {blob_name} ({len(data)} bytes)")
        return data
    except Exception as e:
        logger.error(f"Error downloading bytes: {e}")
        raise

# Função para salvar o modelo linear
def salvar_modelo(modelo, blob_name: str, container_name: str = "uploads"):
    """Salva um modelo treinado no Azure Blob Storage"""
    try:
        # Salve em bytes
        model_bytes = pickle.dumps(modelo)
        
        # Faz upload usando a função anterior
        upload_bytes(model_bytes, blob_name, container_name)
        
        logger.info(f"Model saved: {blob_name}")
    except Exception as e:
        logger.error(f"Error saving model: {e}")
        raise

# Função pra puxar o modelo do blob
def carregar_modelo(blob_name: str, container_name: str = "uploads"):
    """Carrega um modelo do Azure Blob Storage"""
    try:
        # Baixa os bytes
        model_bytes = download_bytes(blob_name, container_name)
        
        # Desserializa o modelo
        modelo = pickle.loads(model_bytes)
        
        logger.info(f"Model loaded: {blob_name}")
        return modelo
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise

# Função que checa se o conteiner existe pra segurança
def container_exists(container_name):
    if not AZURE_STORAGE_CONNECTION_STRING:
        return False
    
    try:
        blob_service_client = get_blob_service_client()
        container_client = blob_service_client.get_container_client(container_name)
        return container_client.exists()
    except Exception:
        return False

# Função pra lista os blobs 
def list_blobs(container_name):
    if not AZURE_STORAGE_CONNECTION_STRING:
        return []
    
    try:
        blob_service_client = get_blob_service_client()
        container_client = blob_service_client.get_container_client(container_name)
        return [blob.name for blob in container_client.list_blobs()]
    except Exception as e:
        logger.error(f"Error listing blobs: {e}")
        return []
