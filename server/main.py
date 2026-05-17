from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model.engine import load_model, get_search

model = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    matrix, vectorizer, metadata = load_model(1000)
    model["matrix"] = matrix
    model["vectorizer"] = vectorizer
    model["metadata"] = metadata
    yield
    model.clear()

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
def get_search_results(query: str):
    print(query)
    return get_search(query, 10, model["matrix"], model["vectorizer"], model["metadata"])