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
    """Retorna o cliente do Blob Service se as credenciais existirem"""
    if not AZURE_STORAGE_CONNECTION_STRING:
        raise RuntimeError("Azure env vars missing - cannot create blob service client")
    
    try:
        return BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    except Exception as e:
        logger.error(f"Error creating blob service client: {e}")
        raise

def download_arquivo(blob_name: str, container_name: str) -> str:
    """Retorna a URL pública assinada do arquivo no Azure Blob Storage"""
    if not AZURE_STORAGE_CONNECTION_STRING:
        raise RuntimeError("Azure env vars missing - cannot get file URL")
    
    try:
        from datetime import datetime, timedelta
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions
        
        blob_service_client = get_blob_service_client()
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        # Gera SAS token para acesso público temporário
        sas_token = generate_blob_sas(
            account_name=AZURE_STORAGE_ACCOUNT_NAME,
            container_name=container_name,
            blob_name=blob_name,
            account_key=AZURE_STORAGE_ACCOUNT_KEY,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=24)  # Válido por 24 horas
        )
        
        # Retorna a URL com SAS token
        url = f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
        logger.info(f"Generated SAS URL for: {blob_name}")
        return url
        
    except Exception as e:
        logger.error(f"Error generating file URL: {e}")
        raise

def upload_arquivo(local_file_name: str, blob_name: str = None, container_name: str = "uploads"):
    """Faz upload de um arquivo para o Azure Blob Storage"""
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

def upload_bytes(data: bytes, blob_name: str, container_name: str):
    """Faz upload de bytes diretamente para o Azure Blob Storage"""
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

def download_bytes(blob_name: str, container_name: str) -> bytes:
    """Faz download de bytes do Azure Blob Storage"""
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

def salvar_modelo(modelo, blob_name: str, container_name: str = "uploads"):
    """Salva um modelo treinado no Azure Blob Storage"""
    try:
        # Serializa o modelo para bytes
        model_bytes = pickle.dumps(modelo)
        
        # Faz upload dos bytes
        upload_bytes(model_bytes, blob_name, container_name)
        
        logger.info(f"Model saved: {blob_name}")
    except Exception as e:
        logger.error(f"Error saving model: {e}")
        raise

def carregar_modelo(blob_name: str, container_name: str = "uploads"):
    """Carrega um modelo do Azure Blob Storage"""
    try:
        # Faz download dos bytes
        model_bytes = download_bytes(blob_name, container_name)
        
        # Desserializa o modelo
        modelo = pickle.loads(model_bytes)
        
        logger.info(f"Model loaded: {blob_name}")
        return modelo
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise

# Funções auxiliares (mantidas da sua versão original)
def container_exists(container_name):
    """Verifica se um container existe"""
    if not AZURE_STORAGE_CONNECTION_STRING:
        return False
    
    try:
        blob_service_client = get_blob_service_client()
        container_client = blob_service_client.get_container_client(container_name)
        return container_client.exists()
    except Exception:
        return False

def list_blobs(container_name):
    """Lista blobs em um container"""
    if not AZURE_STORAGE_CONNECTION_STRING:
        return []
    
    try:
        blob_service_client = get_blob_service_client()
        container_client = blob_service_client.get_container_client(container_name)
        return [blob.name for blob in container_client.list_blobs()]
    except Exception as e:
        logger.error(f"Error listing blobs: {e}")
        return []