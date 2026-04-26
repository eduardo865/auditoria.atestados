import streamlit as st
from google.cloud import storage
from google.oauth2 import service_account
import json

st.set_page_config(page_title="Auditoria de Atestados", page_icon="📄")

@st.cache_resource
def get_storage_client():
    try:
        # Puxa as credenciais dos Secrets do Streamlit
        if "gcp_service_account" in st.secrets:
            info = dict(st.secrets["gcp_service_account"])
            # Remove escapes de quebra de linha se houver
            if "private_key" in info:
                info["private_key"] = info["private_key"].replace("\\n", "\n")
            
            credentials = service_account.Credentials.from_service_account_info(info)
            return storage.Client(credentials=credentials, project=info['project_id'])
        else:
            st.error("Secrets 'gcp_service_account' não encontrado.")
            st.stop()
    except Exception as e:
        st.error(f"Erro na autenticação: {e}")
        st.stop()

storage_client = get_storage_client()
BUCKET_NAME = "atestados-saida-final" 

st.title("📄 Auditoria Automática de Atestados")
st.markdown("Arraste seus arquivos abaixo para processamento imediato.")

uploaded_files = st.file_uploader(
    "Arraste PDF, JPG ou PNG", 
    type=["pdf", "jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files:
    bucket = storage_client.bucket(BUCKET_NAME)
    for uploaded_file in uploaded_files:
        with st.spinner(f"Enviando: {uploaded_file.name}"):
            try:
                blob = bucket.blob(uploaded_file.name)
                blob.upload_from_string(
                    uploaded_file.read(),
                    content_type=uploaded_file.type
                )
                st.success(f"✅ {uploaded_file.name} enviado!")
            except Exception as e:
                st.error(f"❌ Erro no envio: {e}")
st.divider()
st.caption("Desenvolvido para Auditoria de Saúde - Projeto able-inn-404618")
