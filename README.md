# Smart Context Engine

![Python](https://img.shields.io/badge/Python-3.12+-blue) 
![FastAPI](https://img.shields.io/badge/FastAPI-Async-green)
![Inngest](https://img.shields.io/badge/Inngest-Event--Driven-purple)
![Gemini](https://img.shields.io/badge/Gemini-1.5--Flash-orange)
![Embeddings](https://img.shields.io/badge/Embedding-Text--Embedding--004-red)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector--DB-blueviolet) 
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-ff4b4b)
![LlamaIndex](https://img.shields.io/badge/LlamaIndex-RAG-yellow)

Live App: [https://ai-rag-agent.streamlit.app/](https://ai-rag-agent.streamlit.app/)

A production-grade Retrieval-Augmented Generation (RAG) system for document-grounded intelligence.

It separates ingestion from querying using an event-driven workflow, ensuring scalability, reliability, and strict context isolation.

---

## Core Features

* Asynchronous PDF ingestion
* 768-dimension vector embeddings
* Isolated Qdrant namespaces
* Event-driven orchestration (Inngest)
* Context-grounded LLM responses
* Strict schema validation (Pydantic v2)

---

## Tech Stack

**AI Layer**

* Gemini 1.5 Flash
* Text-Embedding-004
* LlamaIndex

**Backend & Infra**

* FastAPI (Async)
* Inngest (Workflow Engine)
* Qdrant (Vector DB)
* Streamlit (Frontend)
* Python 3.12+

---

## Project Structure

```
.
├── app.py              # Streamlit frontend
├── main.py             # FastAPI app + Inngest workflows
├── data_loader.py      # PDF parsing & embedding pipeline
├── vector_db.py        # Qdrant search logic
├── custom_types.py     # Pydantic models
├── requirements.txt    # Dependencies
├── LICENSE             # MIT License
└── README.md
```

---

## Run Locally

Start Qdrant:

```
docker run -d -p 6333:6333 qdrant/qdrant
```

Install dependencies:

```
pip install -r requirements.txt
```

Run backend:

```
uvicorn main:app --reload
```

Run Streamlit:

```
streamlit run app.py
```

---

## License

MIT License

This project is open-sourced under the MIT License.

