import asyncio
from pathlib import Path
import time
import streamlit as st
import inngest
from dotenv import load_dotenv
import os
import requests

load_dotenv()

st.set_page_config(
    page_title="Smart Context Engine",
    layout="centered"
)

# -------------------------
# Minimal Professional Styling
# -------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.main-container {
    max-width: 800px;
    margin: auto;
    padding-top: 40px;
}

.header-title {
    font-size: 32px;
    font-weight: 600;
    margin-bottom: 6px;
}

.header-subtitle {
    font-size: 15px;
    color: #6b7280;
    margin-bottom: 40px;
}

.section-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 10px;
    margin-top: 40px;
}

.answer-box {
    border-left: 3px solid #111827;
    padding-left: 16px;
    margin-top: 20px;
    font-size: 16px;
    line-height: 1.6;
}

.source-text {
    font-size: 13px;
    color: #6b7280;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# -------------------------
# Header
# -------------------------
st.markdown('<div class="header-title">Smart Context Engine</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="header-subtitle">A retrieval-augmented system that answers strictly from your uploaded documents.</div>',
    unsafe_allow_html=True
)

# -------------------------
# Inngest Client
# -------------------------
@st.cache_resource
def get_inngest_client() -> inngest.Inngest:
    return inngest.Inngest(app_id="rag_app", is_production=False)

def save_uploaded_pdf(file) -> Path:
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    file_path = uploads_dir / file.name
    file_path.write_bytes(file.getbuffer())
    return file_path

async def send_rag_ingest_event(pdf_path: Path) -> None:
    client = get_inngest_client()
    await client.send(
        inngest.Event(
            name="rag/ingest_pdf",
            data={
                "pdf_path": str(pdf_path.resolve()),
                "source_id": pdf_path.name,
            },
        )
    )

# -------------------------
# Document Ingestion
# -------------------------
st.markdown('<div class="section-title">Document Ingestion</div>', unsafe_allow_html=True)

uploaded = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded:
    with st.spinner("Indexing document..."):
        path = save_uploaded_pdf(uploaded)
        asyncio.run(send_rag_ingest_event(path))
        time.sleep(0.3)
    st.success(f"Indexed: {path.name}")

# -------------------------
# Query Section
# -------------------------
st.markdown('<div class="section-title">Ask a Question</div>', unsafe_allow_html=True)

async def send_rag_query_event(question: str, top_k: int):
    client = get_inngest_client()
    result = await client.send(
        inngest.Event(
            name="rag/query_pdf_ai",
            data={
                "question": question,
                "top_k": top_k,
            },
        )
    )
    return result[0]

def _inngest_api_base() -> str:
    return os.getenv("INNGEST_API_BASE", "http://127.0.0.1:8288/v1")

def fetch_runs(event_id: str):
    url = f"{_inngest_api_base()}/events/{event_id}/runs"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json().get("data", [])

def wait_for_run_output(event_id: str, timeout_s=120, poll_interval_s=0.5):
    start = time.time()
    while True:
        runs = fetch_runs(event_id)
        if runs:
            run = runs[0]
            if run.get("status") in ("Completed", "Succeeded", "Success", "Finished"):
                return run.get("output") or {}
        if time.time() - start > timeout_s:
            raise TimeoutError("Timed out waiting for response.")
        time.sleep(poll_interval_s)

with st.form("query_form"):
    question = st.text_input("Enter your question")
    top_k = st.slider("Context depth", 1, 20, 5)
    submitted = st.form_submit_button("Generate")

if submitted and question.strip():
    with st.spinner("Retrieving context and generating response..."):
        event_id = asyncio.run(send_rag_query_event(question.strip(), top_k))
        output = wait_for_run_output(event_id)
        answer = output.get("answer", "")
        sources = output.get("sources", [])

    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
    st.markdown(answer if answer else "No answer returned.")
    st.markdown('</div>', unsafe_allow_html=True)

    if sources:
        st.markdown('<div class="section-title">Sources</div>', unsafe_allow_html=True)
        for s in sources:
            st.markdown(f'<div class="source-text">{s}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
