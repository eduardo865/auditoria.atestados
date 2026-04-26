import streamlit as st
from google.cloud import storage
from google.oauth2 import service_account
import base64
import json

st.set_page_config(page_title="Auditoria de Atestados", page_icon="📄")

@st.cache_resource
def get_storage_client():
    try:
        if "gcp_json_base64" in st.secrets:
            # Pega a string e remove qualquer espaço ou quebra de linha acidental
            b64_str = st.secrets["gcp_json_base64"].strip()
            
            # Remove caracteres que não pertencem ao Base64 (limpeza de segurança)
            # Isso evita o erro de 'utf-8' se houver lixo na string
            try:
                decoded_bytes = base64.b64decode(b64_str)
                decoded_json = decoded_bytes.decode("utf-8")
                info = json.loads(decoded_json)
            except Exception:
                # Se falhar, tenta uma segunda limpeza de padding
                missing_padding = len(b64_str) % 4
                if missing_padding:
                    b64_str += '=' * (4 - missing_padding)
                decoded_json = base64.b64decode(b64_str).decode("utf-8")
                info = json.loads(decoded_json)
            
            credentials = service_account.Credentials.from_service_account_info(info)
            return storage.Client(credentials=credentials, project=info['project_id'])
        else:
            st.error("A chave 'gcp_json_base64' não foi encontrada nos Secrets.")
            st.stop()
    except Exception as e:
        st.error(f"Erro Crítico de Autenticação: {e}")
        st.stop()

# Inicialização
storage_client = get_storage_client()
BUCKET_NAME = "atestados-saida-final"

st.title("📄 Sistema de Auditoria")
st.write("Conexão com Google Cloud estabelecida com sucesso!")

uploaded_files = st.file_uploader("Arraste seus atestados aqui", type=["pdf", "jpg", "png"], accept_multiple_files=True)

if uploaded_files:
    bucket = storage_client.bucket(BUCKET_NAME)
    for uploaded_file in uploaded_files:
        with st.spinner(f"Fazendo upload de {uploaded_file.name}..."):
            blob = bucket.blob(uploaded_file.name)
            blob.upload_from_string(uploaded_file.read(), content_type=uploaded_file.type)
            st.success(f"✅ {uploaded_file.name} enviado!")
