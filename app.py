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
            # Pega o texto dos Secrets
            raw_str = st.secrets["gcp_json_base64"]
            
            # LIMPEZA RADICAL: Remove TUDO que não for caractere de Base64 (A-Z, 0-9, +, /, =)
            # Isso elimina aspas curvas, espaços invisíveis e caracteres utf-8 parasitas
            b64_str = re.sub(r'[^a-zA-Z0-9+/=]', '', raw_str)
            
            # Corrige preenchimento (padding) se necessário
            missing_padding = len(b64_str) % 4
            if missing_padding:
                b64_str += '=' * (4 - missing_padding)
            
            # Decodifica
            decoded_bytes = base64.b64decode(b64_str)
            info = json.loads(decoded_bytes.decode("utf-8"))
            
            credentials = service_account.Credentials.from_service_account_info(info)
            return storage.Client(credentials=credentials, project=info['project_id'])
        else:
            st.error("Secret 'gcp_json_base64' ausente.")
            st.stop()
    except Exception as e:
        st.error(f"Erro Crítico de Autenticação: {e}")
        st.stop()

storage_client = get_storage_client()
BUCKET_NAME = "atestados-saida-final"

st.title("📄 Sistema de Auditoria")
st.success("Conexão com Google Cloud estabelecida!")

uploaded_files = st.file_uploader("Arraste seus atestados aqui", type=["pdf", "jpg", "png"], accept_multiple_files=True)

if uploaded_files:
    bucket = storage_client.bucket(BUCKET_NAME)
    for uploaded_file in uploaded_files:
        with st.spinner(f"Enviando {uploaded_file.name}..."):
            blob = bucket.blob(uploaded_file.name)
            blob.upload_from_string(uploaded_file.read(), content_type=uploaded_file.type)
            st.success(f"✅ {uploaded_file.name} enviado!")
