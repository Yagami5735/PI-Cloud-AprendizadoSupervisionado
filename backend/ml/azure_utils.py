import os
import logging
from azure.storage.blob import BlobServiceClient

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

def download_arquivo(container_name, blob_name, local_file_name):
    """Faz download de um arquivo do Azure Blob Storage"""
    if not AZURE_STORAGE_CONNECTION_STRING:
        raise RuntimeError("Azure env vars missing - cannot download file")
    
    try:
        blob_service_client = get_blob_service_client()
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        with open(local_file_name, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        
        logger.info(f"File downloaded: {blob_name} -> {local_file_name}")
        return True
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise

def upload_arquivo(container_name, local_file_name, blob_name=None):
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
        return True
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise

# Funções auxiliares
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

def upload_bytes(data: bytes, blob_name: str, container_name: str):
    """Faz upload de bytes diretamente para o Azure Blob Storage"""
    if not AZURE_STORAGE_CONNECTION_STRING:
        raise RuntimeError("Azure env vars missing - cannot upload bytes")
    
    try:
        blob_service_client = get_blob_service_client()
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        blob_client.upload_blob(data, overwrite=True)
        
        logger.info(f"Bytes uploaded: {blob_name} ({len(data)} bytes)")
        return True
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