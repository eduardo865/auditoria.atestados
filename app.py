import streamlit as st
from google.cloud import storage
from google.oauth2 import service_account
import base64
import json

# Configuração da página
st.set_page_config(page_title="Auditoria de Atestados", page_icon="📄")

@st.cache_resource
def get_storage_client():
    try:
        # Lê o código Base64 dos Secrets
        if "gcp_json_base64" in st.secrets:
            encoded_json = st.secrets["gcp_json_base64"]
            # Decodifica para o formato JSON original
            decoded_json = base64.b64decode(encoded_json).decode("utf-8")
            info = json.loads(decoded_json)
            
            credentials = service_account.Credentials.from_service_account_info(info)
            return storage.Client(credentials=credentials, project=info['project_id'])
        else:
            st.error("Secret 'gcp_json_base64' não encontrado!")
            st.stop()
    except Exception as e:
        st.error(f"Erro na autenticação: {e}")
        st.stop()

# Inicializa o cliente do Google Cloud
storage_client = get_storage_client()
BUCKET_NAME = "atestados-saida-final" 

st.title("📄 Sistema de Upload - Auditoria")
st.write("Envie seus atestados para processamento automático.")

uploaded_files = st.file_uploader("Selecione os arquivos", type=["pdf", "jpg", "png"], accept_multiple_files=True)

if uploaded_files:
    bucket = storage_client.bucket(BUCKET_NAME)
    for uploaded_file in uploaded_files:
        with st.spinner(f"Enviando {uploaded_file.name}..."):
            blob = bucket.blob(uploaded_file.name)
            blob.upload_from_string(uploaded_file.read(), content_type=uploaded_file.type)
            st.success(f"✅ {uploaded_file.name} enviado!")
