import streamlit as st
from google.cloud import storage
from google.oauth2 import service_account
import base64
import json
import re

st.set_page_config(page_title="Auditoria de Atestados", page_icon="📄")

@st.cache_resource
def get_storage_client():
    try:
        if "gcp_json_base64" in st.secrets:
            # 1. Limpa a string de qualquer resquício de caractere invisível
            b64_str = re.sub(r'[^a-zA-Z0-9+/=]', '', st.secrets["gcp_json_base64"])
            
            # 2. Decodifica
            decoded_bytes = base64.b64decode(b64_str)
            decoded_str = decoded_bytes.decode("utf-8")
            
            # 3. Transforma em dicionário
            info = json.loads(decoded_str)
            
            credentials = service_account.Credentials.from_service_account_info(info)
            return storage.Client(credentials=credentials, project=info['project_id'])
        else:
            st.error("Secret não encontrado.")
            st.stop()
    except Exception as e:
        st.error(f"Erro Crítico: {e}")
        st.stop()

# --- Restante do código (Título e Upload) ---
storage_client = get_storage_client()
st.title("📄 Auditoria Pronta")
st.success("Conectado com sucesso!")

u_files = st.file_uploader("Selecione os arquivos", accept_multiple_files=True)
if u_files:
    bucket = storage_client.bucket("atestados-saida-final")
    for f in u_files:
        blob = bucket.blob(f.name)
        blob.upload_from_string(f.read(), content_type=f.type)
        st.success(f"Enviado: {f.name}")
