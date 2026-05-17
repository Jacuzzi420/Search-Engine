from qdrant_client import QdrantClient, models
from qdrant_client.models import VectorParams, Distance
from engine import get_search_data
from uuid import uuid4
import ollama

def init() -> None:
    client = QdrantClient("localhost", port=6333)
    
    client.create_collection(
        collection_name="search-engine",
        vectors_config=VectorParams(
            size=768,
            distance=Distance.COSINE
        )
    )

    client.create_payload_index(
        collection_name="search-engine",
        field_name="url",
        field_schema=models.PayloadSchemaType.KEYWORD
    )

def drop() -> None:
    client = QdrantClient("localhost", port=6333)
    client.delete_collection("search-engine")

#todo
def make_chunks(text: str) -> list[str]:
    pass

def vectorize() -> None:
    text, titles, urls = get_search_data()
    points = []

    for index, (content, title, url) in enumerate(zip(text, titles, urls)):
        print(f"Processing website {index}")

        for chunk in make_chunks(content):
            emb = ollama.embeddings(
                model="nomic-embed-text",
                prompt=chunk
            )["embedding"]

            points.append({
                "id": str(uuid4()),
                "vector": emb,
                "payload": {
                    "title": title,
                    "url": url,
                }
            })

    client = QdrantClient("localhost", port=6333)

    client.upsert(
        collection_name="search-engine",
        points=points,
    )

if __name__ == "__main__":
    vectorize()