import asyncio
from pathlib import Path
import time
import streamlit as st
import inngest
from dotenv import load_dotenv
import os
import requests

# Load Environment
load_dotenv()

# Page Config
st.set_page_config(
    page_title="Pulse RAG | Intelligent Document Insights", 
    page_icon="⚡", 
    layout="wide"
)

# Custom CSS for Professional Branding
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
    }
    .pulse-header {
        font-size: 3rem;
        font-weight: 800;
        color: #ff4b4b;
        margin-bottom: 0;
    }
    .pulse-subtitle {
        font-size: 1.2rem;
        color: #808495;
        margin-bottom: 2rem;
    }
    .sidebar-text {
        font-size: 0.9rem;
        color: #a3a8b4;
    }
    </style>
    """, unsafe_allow_html=True)

# Branding Header
st.markdown('<p class="pulse-header">⚡ Pulse RAG</p>', unsafe_allow_html=True)
st.markdown('<p class="pulse-subtitle">Event-driven Document Intelligence Agent</p>', unsafe_allow_html=True)

# Sidebar for Ingestion
with st.sidebar:
    st.header("📥 Data Ingestion")
    st.markdown("Upload documents to the **Pulse** engine to begin indexing.")
    uploaded = st.file_uploader("Choose a PDF", type=["pdf"], accept_multiple_files=False)
    
    st.divider()
    st.markdown('<p class="sidebar-text">Status: 🟢 System Active</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-text">Powered by Gemini & Inngest</p>', unsafe_allow_html=True)

@st.cache_resource
def get_inngest_client() -> inngest.Inngest:
    return inngest.Inngest(app_id="pulse_rag", is_production=False)

def save_uploaded_pdf(file) -> Path:
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    file_path = uploads_dir / file.name
    file_path.write_bytes(file.getbuffer())
    return file_path

async def send_pulse_ingest_event(pdf_path: Path) -> None:
    client = get_inngest_client()
    await client.send(
        inngest.Event(
            name="pulse/ingest_pdf", # Consistent with naya naming
            data={
                "pdf_path": str(pdf_path.resolve()),
                "source_id": pdf_path.name,
            },
        )
    )

def fetch_runs(event_id: str):
    # Local Inngest Dev Server API
    url = f"http://127.0.0.1:8288/api/events/{event_id}/runs"
    try:
        r = requests.get(url, timeout=2)
        return r.json() if r.status_code == 200 else []
    except:
        return []

def wait_for_pulse_output(event_id: str, timeout_s=60):
    start = time.time()
    while time.time() - start < timeout_s:
        runs = fetch_runs(event_id)
        if runs:
            run = runs[0]
            status = run.get("status")
            if status in ("Completed", "Succeeded", "Success"):
                return run.get("output") or {}
            if status in ("Failed", "Cancelled"):
                st.error(f"Function run failed with status: {status}")
                return {}
        time.sleep(1)
    st.warning("Request timed out. The backend is still processing.")
    return {}

# Main UI Area
col1, col2 = st.columns([2, 1])

with col1:
    if uploaded is not None:
        if st.sidebar.button("🚀 Trigger Pulse Ingest"):
            with st.status("Indexing document...", expanded=True) as status:
                path = save_uploaded_pdf(uploaded)
                asyncio.run(send_pulse_ingest_event(path))
                status.update(label="Ingestion event fired! Check Inngest Dev Server.", state="complete")
                st.sidebar.success(f"File '{uploaded.name}' scheduled!")

    st.subheader("🔍 Ask the Pulse")
    with st.form("pulse_query_form"):
        question = st.text_input("Enter your query about the uploaded knowledge base", placeholder="e.g., What is the revenue mentioned in the report?")
        top_k = st.slider("Depth of context (top_k)", 1, 10, 5)
        submitted = st.form_submit_button("Query Engine")

        if submitted and question.strip():
            with st.spinner("Pulse engine searching and generating..."):
                # Note: Aapko main.py mein bhi event name 'pulse/query' update karna hoga
                client = get_inngest_client()
                event_id = asyncio.run(client.send(inngest.Event(
                    name="pulse/query",
                    data={"question": question.strip(), "top_k": int(top_k)}
                )))
                
                output = wait_for_pulse_output(event_id[0])
                
                if output:
                    st.markdown("### 💡 Answer")
                    st.write(output.get("answer", "No response generated."))
                    
                    if output.get("sources"):
                        with st.expander("📚 Sources & References"):
                            for src in output["sources"]:
                                st.info(f"Source: {src}")

with col2:
    st.subheader("📊 System Health")
    st.metric(label="Backend Engine", value="FastAPI")
    st.metric(label="Workflow Engine", value="Inngest")
    st.metric(label="Vector DB", value="Qdrant")
