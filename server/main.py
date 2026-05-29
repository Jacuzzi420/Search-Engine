from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model.engine import load_model, get_search
from qdrant_client import AsyncQdrantClient
import ollama

@asynccontextmanager
async def lifespan(app: FastAPI):
    matrix, Vt, vectorizer, metadata = load_model(1024)
    app.qdrant = AsyncQdrantClient("localhost", port=6333)
    app.matrix = matrix
    app.Vt = Vt
    app.vectorizer = vectorizer
    app.metadata = metadata
    app.search_number = 20
    app.emb_weight = 0
    app.svd_weight = 1
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
    try:
        query_emb = ollama.embeddings(
            model="nomic-embed-text",
            prompt=query
        )["embedding"]

        results = await app.qdrant.query_points_groups(
            collection_name="search-engine",
            query=query_emb,
            group_by="url",
            limit=app.search_number,
            group_size=1
        )

        emb_result = [(result.hits[0].payload['title'], result.hits[0].payload['url']) for result in results.groups]
        svd_result = get_search(query, app.search_number, app.matrix, app.Vt, app.vectorizer, app.metadata)

        weights = {}
        for index, (emb, svd) in enumerate(zip(emb_result, svd_result)):
            val = app.search_number - index
            weights[emb] = weights.get(emb, 0) + val * app.emb_weight
            weights[svd] = weights.get(svd, 0) + val * app.svd_weight

        return { 'results': [k for k, _ in sorted(weights.items(), reverse=True, key=lambda item: item[1])] }
    except Exception as e:
        print(e)
        return { 'results': [] }