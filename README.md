# Production-Grade RAG AI Agent

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Async-green)
![Inngest](https://img.shields.io/badge/Inngest-Event--Driven-purple)
![Gemini](https://img.shields.io/badge/Gemini-1.5--Flash-orange)
![Embeddings](https://img.shields.io/badge/Embedding-Text--Embedding--004-red)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector--DB-blueviolet)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-ff4b4b)
![LlamaIndex](https://img.shields.io/badge/LlamaIndex-RAG-yellow)

---

## Overview

This project is a production-grade Retrieval-Augmented Generation (RAG) system built for enterprise-scale document intelligence.

It is designed with asynchronous orchestration, background ingestion workflows, strict schema validation, and isolated vector contexts to ensure high performance, reliability, and maintainability.

Unlike prototype RAG implementations, this system separates ingestion from querying using an event-driven workflow engine, enabling scalable document processing without blocking API responsiveness.

---

## Architecture

### 1. Asynchronous Orchestration

Long-running tasks such as PDF parsing, chunking, embedding generation, and vector upserts are executed as background workflows using Inngest. This ensures the API layer remains responsive.

### 2. Context Isolation

Each document or knowledge source operates in an isolated vector namespace within Qdrant. This prevents cross-document contamination and ensures clean contextual retrieval.

### 3. Observability

Every LLM inference, embedding call, and vector search is traceable through the orchestration layer. This enables debugging, monitoring, and performance tracking at a granular level.

### 4. Resiliency

The system includes:

* Automatic retries with exponential backoff
* Rate-limit handling
* Function-level throttling
* Graceful timeout recovery

---

## System Workflow

### Document Ingestion Pipeline

1. User uploads a PDF.
2. An ingestion event is triggered.
3. The document is parsed and split into chunks with overlap.
4. 768-dimensional embeddings are generated.
5. Embeddings are upserted into Qdrant.

All ingestion steps run asynchronously.

### Query & Retrieval Pipeline

1. User submits a query.
2. Query embedding is generated.
3. Cosine similarity search retrieves top-K relevant chunks.
4. Retrieved chunks are injected into a strict system prompt.
5. The LLM generates a context-grounded response.

The model is constrained to answer only from retrieved context.

---

## Tech Stack

### Artificial Intelligence

* Large Language Model: Google Gemini 1.5 Flash
* Embeddings: Google Text-Embedding-004 (768-dimensional vectors)
* RAG Framework: LlamaIndex

### Backend & Infrastructure

* Workflow Engine: Inngest
* Vector Database: Qdrant (Dockerized deployment)
* API Framework: FastAPI (Async Python backend)
* Frontend: Streamlit
* Package Manager: UV
* Data Validation: Pydantic v2
* Python Version: 3.12+

---

## Project Structure

```
├── app.py              # Streamlit interface
├── main.py             # FastAPI entry point + Inngest functions
├── data_loader.py      # PDF parsing + embedding generation
├── vector_db.py        # Qdrant similarity search logic
├── custom_types.py     # Pydantic models
├── .env                # Environment variables
└── pyproject.toml      # Dependency configuration
```

---

## Installation & Setup

### 1. Deploy Vector Database

Ensure Docker is running, then start Qdrant:

```
docker run -d --name qdrant-rag-db -p 6333:6333 qdrant/qdrant
```

---

### 2. Install Dependencies

```
uv sync
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

Create a `.env` file:

```
GEMINI_API_KEY=your_google_ai_studio_key
```

---

### 3. Run the System

Start FastAPI backend:

```
uv run uvicorn main:app --reload
```

Start Inngest development server:

```
npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/ingest
```

Start Streamlit frontend:

```
uv run streamlit run app.py
```

---

## Production Characteristics

* Event-driven ingestion pipeline
* Asynchronous background workflows
* Strong schema validation
* Vector database isolation
* Retry-aware architecture
* Observability at step level
* Clean separation of concerns

---

## References

* Inngest Documentation: [https://www.inngest.com/docs](https://www.inngest.com/docs)
* Gemini API Reference: [https://ai.google.dev/gemini-api/docs](https://ai.google.dev/gemini-api/docs)
* Qdrant Documentation: [https://qdrant.tech/documentation/](https://qdrant.tech/documentation/)

---

This system demonstrates production-level RAG architecture patterns including orchestration, reliability engineering, and scalable vector retrieval design.
