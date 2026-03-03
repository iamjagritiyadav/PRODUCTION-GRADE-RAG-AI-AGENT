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
    page_icon="🧠",
    layout="centered"
)

# ---------------------------
# Custom Styling
# ---------------------------
st.markdown("""
<style>
.main {
    padding-top: 1rem;
}
.block-container {
    padding-top: 2rem;
}
h1 {
    font-size: 2.5rem !important;
}
.stButton>button {
    width: 100%;
    border-radius: 8px;
    height: 3em;
    font-weight: 600;
}
.card {
    padding: 1.5rem;
    border-radius: 12px;
    background-color: #111827;
    border: 1px solid #1f2937;
    margin-bottom: 1.5rem;
}
.answer-box {
    padding: 1.2rem;
    border-radius: 10px;
    background-color: #0f172a;
    border: 1px solid #334155;
}
.source-box {
    font-size: 0.9rem;
    color: #94a3b8;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Header
# ---------------------------
st.markdown("""
<h1 style='text-align:center;'>🧠 Smart Context Engine</h1>
<p style='text-align:center; color:#94a3b8;'>
A grounded RAG system that answers strictly from your uploaded documents.
</p>
""", unsafe_allow_html=True)

st.divider()

# ---------------------------
# Inngest Client
# ---------------------------
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

# ---------------------------
# Ingest Section
# ---------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📄 Document Ingestion")

uploaded = st.file_uploader("Upload a PDF to index", type=["pdf"])

if uploaded:
    with st.spinner("Indexing document into vector memory..."):
        path = save_uploaded_pdf(uploaded)
        asyncio.run(send_rag_ingest_event(path))
        time.sleep(0.3)
    st.success(f"Document indexed: {path.name}")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# Query Section
# ---------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🔎 Ask From Your Context")

async def send_rag_query_event(question: str, top_k: int) -> None:
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

def fetch_runs(event_id: str) -> list[dict]:
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
    top_k = st.slider("Context depth (retrieved chunks)", 1, 20, 5)
    submitted = st.form_submit_button("Generate Answer")

if submitted and question.strip():
    with st.spinner("Retrieving relevant context and generating grounded response..."):
        event_id = asyncio.run(send_rag_query_event(question.strip(), top_k))
        output = wait_for_run_output(event_id)
        answer = output.get("answer", "")
        sources = output.get("sources", [])

    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
    st.markdown("### 🧾 Grounded Answer")
    st.write(answer if answer else "No answer returned.")
    st.markdown('</div>', unsafe_allow_html=True)

    if sources:
        st.markdown("#### 📌 Source References")
        for s in sources:
            st.markdown(f"<div class='source-box'>• {s}</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# Trust Footer
# ---------------------------
st.divider()
st.caption("✔ Responses are generated strictly from indexed documents.")
st.caption("✔ No external internet knowledge used.")
st.caption("✔ Retrieval-augmented, context-grounded reasoning.")
