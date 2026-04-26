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
            # Pega o texto e remove qualquer caractere que não seja Base64
            raw_b64 = st.secrets["gcp_json_base64"]
            clean_b64 = re.sub(r'[^a-zA-Z0-9+/=]', '', raw_b64)
            
            # Decodifica e carrega como JSON
            decoded_bytes = base64.b64decode(clean_b64)
            info = json.loads(decoded_bytes.decode("utf-8"))
            
            credentials = service_account.Credentials.from_service_account_info(info)
            return storage.Client(credentials=credentials, project=info['project_id'])
        else:
            st.error("Configuração 'gcp_json_base64' não encontrada nos Secrets.")
            st.stop()
    except Exception as e:
        st.error(f"Erro Crítico: {e}")
        st.stop()

# --- INTERFACE ---
storage_client = get_storage_client()
BUCKET_NAME = "atestados-saida-final"

st.title("📄 Sistema de Auditoria")
st.success("Conexão com Google Cloud Ativa!")

files = st.file_uploader("Selecione os arquivos", type=["pdf", "jpg", "png"], accept_multiple_files=True)

if files:
    bucket = storage_client.bucket(BUCKET_NAME)
    for f in files:
        with st.spinner(f"Enviando {f.name}..."):
            blob = bucket.blob(f.name)
            blob.upload_from_string(f.read(), content_type=f.type)
            st.success(f"✅ {f.name} enviado!")
