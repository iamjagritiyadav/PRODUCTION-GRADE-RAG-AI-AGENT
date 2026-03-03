import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

EMBED_MODEL = "text-embedding-004"
EMBED_DIM = 768

splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)

def load_and_chunk_pdf(path: str):
  
    docs = PDFReader().load_data(file=Path(path))
    chunks = []
    
   
    for d in docs:
        if hasattr(d, "text") and d.text:
            
            split_nodes = splitter.split_text(d.text)
            chunks.extend(split_nodes)
            
    return chunks

def embed_texts(texts: list[str]) -> list[list[float]]:
    result = client.models.embed_content(
        model=EMBED_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=EMBED_DIM
        )
    )
    return [e.values for e in result.embeddings]
