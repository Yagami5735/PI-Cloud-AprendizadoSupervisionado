import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

load_dotenv()

CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")

if not CONNECTION_STRING or not CONTAINER_NAME:
    raise RuntimeError("Azure env vars missing")

# inicializa cliente (funciona com sua connection string SAS)
blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

def _extract_sas_from_conn_str(conn_str: str) -> str | None:
    """Retorna o valor do SharedAccessSignature se existir na connection string."""
    parts = dict(x.split("=", 1) for x in conn_str.split(";") if "=" in x)
    sas = parts.get("SharedAccessSignature") or parts.get("SharedAccessSignature".lower())
    if not sas:
        return None
    # sanitize: remove possíveis aspas e espaços e leading '?'
    sas = sas.strip().strip('"').strip("'")
    if sas.startswith("?"):
        sas = sas[1:]
    return sas

def upload_arquivo(local_path: str, blob_name: str) -> str:
    """Faz upload do arquivo e retorna uma URL utilizável (com SAS se disponível)."""
    # upload
    blob_client = container_client.get_blob_client(blob_name)
    with open(local_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

    # monta URL base sem SAS
    base_blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{CONTAINER_NAME}/{blob_name}"

    # tenta reaproveitar SAS embutido na connection string
    sas = _extract_sas_from_conn_str(CONNECTION_STRING)

    # debug: imprima o SAS e URL (remova em produção)
    print("DEBUG: SAS extracted (repr):", repr(sas))
    print("DEBUG: base_blob_url:", base_blob_url)

    if sas:
        url = f"{base_blob_url}?{sas}"  # apenas um "?"
    else:
        url = base_blob_url

    print("DEBUG: final blob url:", url)
    return url

def download_arquivo(nome_arquivo: str) -> str:
    """
    Gera a URL pública (com SAS) para um arquivo do container.
    Exemplo de retorno: https://<account>.blob.core.windows.net/<container>/<arquivo>?<sas>
    """
    if not CONNECTION_STRING:
        raise ValueError("Connection string não encontrada no .env")

    # Extrai o SAS da connection string
    sas = _extract_sas_from_conn_str(CONNECTION_STRING)
    if not sas:
        raise ValueError("SharedAccessSignature não encontrada na connection string")

    # Monta a URL final corretamente
    blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{CONTAINER_NAME}/{nome_arquivo}?{sas}"
    print("DEBUG: URL final correta:", blob_url)
    return blob_url
