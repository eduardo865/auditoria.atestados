import streamlit as st
from google.cloud import storage
from google.oauth2 import service_account
import json

# --- CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="Auditoria de Atestados", page_icon="📄")

# --- AUTENTICAÇÃO SEGURA ---
@st.cache_resource
def get_storage_client():
    # Tenta ler as credenciais dos Secrets do Streamlit
    try:
        # O Streamlit converte o formato TOML dos Secrets em um dicionário Python
        info = dict(st.secrets["gcp_service_account"])
        credentials = service_account.Credentials.from_service_account_info(info)
        return storage.Client(credentials=credentials, project=info['project_id'])
    except Exception as e:
        st.error("Erro nas credenciais: Verifique os 'Secrets' no painel do Streamlit.")
        st.stop()

# Inicializa o cliente
storage_client = get_storage_client()
BUCKET_NAME = "atestados-saida-final" 

# --- INTERFACE ---
st.title("📄 Auditoria Automática de Atestados")
st.markdown("""
Esta interface envia seus arquivos para processamento via Inteligência Artificial.
Os resultados aparecerão na sua planilha do Google em instantes.
""")

uploaded_files = st.file_uploader(
    "Arraste ou selecione seus atestados (PDF, JPG, PNG)", 
    type=["pdf", "jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files:
    bucket = storage_client.bucket(BUCKET_NAME)
    
    for uploaded_file in uploaded_files:
        with st.spinner(f"Fazendo upload de: {uploaded_file.name}..."):
            try:
                blob = bucket.blob(uploaded_file.name)
                # Faz o upload do arquivo para o Google Cloud Storage
                blob.upload_from_string(
                    uploaded_file.read(),
                    content_type=uploaded_file.type
                )
                st.success(f"✅ {uploaded_file.name} enviado com sucesso!")
            except Exception as e:
                st.error(f"❌ Erro ao enviar {uploaded_file.name}: {e}")

st.divider()
st.caption("Desenvolvido para Auditoria de Saúde - Projeto able-inn-404618")
