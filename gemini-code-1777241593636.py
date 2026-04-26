import streamlit as st
from google.cloud import storage
import os

# --- CONFIGURAÇÕES ---
# Certifique-se de ter o arquivo JSON da sua conta de serviço se rodar localmente
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "caminho/para/seu/token.json"

BUCKET_NAME = "atestados-saida-final" # Nome do seu bucket no projeto able-inn

st.set_page_config(page_title="Upload de Atestados", page_icon="📄")

st.title("📄 Sistema de Auditoria de Atestados")
st.markdown("Arraste os arquivos abaixo para iniciar o processamento automático.")

# Componente de Drag and Drop
uploaded_files = st.file_uploader(
    "Escolha os atestados (PDF, JPG, PNG)", 
    type=["pdf", "jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files:
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)

    for uploaded_file in uploaded_files:
        with st.spinner(f"Enviando {uploaded_file.name}..."):
            blob = bucket.blob(uploaded_file.name)
            blob.upload_from_string(
                uploaded_file.read(),
                content_type=uploaded_file.type
            )
            st.success(f"✅ {uploaded_file.name} enviado! A planilha será atualizada em instantes.")

st.divider()
st.info("Os arquivos enviados são processados por IA para identificar fraudes, escrita manual e extração de dados.")