from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model.engine import load_model, get_search
from qdrant_client import QdrantClient
import ollama

@asynccontextmanager
async def lifespan(app: FastAPI):
    matrix, vectorizer, metadata = load_model(1200)
    app.qdrant = QdrantClient("localhost", port=6333)
    app.matrix = matrix
    app.vectorizer = vectorizer
    app.metadata = metadata
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search/")
async def get_search_results(query: str):
    query_emb = ollama.embeddings(
        model="nomic-embed-text",
        prompt=query
    )["embedding"]

    results = await app.search_groups(
        collection_name="search-engine",
        query_vector=query_emb,
        group_by="url",
        limit=20,
        group_size=1
    )

    return get_search(query, 20, app.matrix, app.vectorizer, app.metadata)