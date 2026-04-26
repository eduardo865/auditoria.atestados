import streamlit as st
from google.cloud import storage
from google.oauth2 import service_account
from datetime import datetime
import os

st.set_page_config(
    page_title="Auditoria de Atestados",
    page_icon="📄",
    layout="centered"
)

BUCKET_NAME = "atestados-saida-final"


@st.cache_resource
def get_storage_client():
    try:
        info = dict(st.secrets["gcp_service_account"])

        if "private_key" in info:
            info["private_key"] = info["private_key"].replace("\\n", "\n")

        credentials = service_account.Credentials.from_service_account_info(info)

        return storage.Client(
            credentials=credentials,
            project=info["project_id"]
        )

    except Exception as e:
        st.error("Erro nas credenciais: verifique os Secrets no painel do Streamlit.")
        st.exception(e)
        st.stop()


storage_client = get_storage_client()


st.title("📄 Auditoria Automática de Atestados")

st.markdown("""
Envie seus arquivos de atestado para processamento via Inteligência Artificial.

Os arquivos serão enviados para o Google Cloud Storage.
""")

uploaded_files = st.file_uploader(
    "Arraste ou selecione seus atestados",
    type=["pdf", "jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:
    bucket = storage_client.bucket(BUCKET_NAME)

    for uploaded_file in uploaded_files:
        try:
            with st.spinner(f"Enviando {uploaded_file.name}..."):

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_filename = uploaded_file.name.replace(" ", "_")
                destination_blob_name = f"uploads/{timestamp}_{safe_filename}"

                blob = bucket.blob(destination_blob_name)

                blob.upload_from_string(
                    uploaded_file.getvalue(),
                    content_type=uploaded_file.type
                )

                st.success(f"✅ {uploaded_file.name} enviado com sucesso!")

        except Exception as e:
            st.error(f"❌ Erro ao enviar {uploaded_file.name}")
            st.exception(e)

st.divider()
st.caption("Desenvolvido para Auditoria de Saúde - Projeto able-inn-404618")
