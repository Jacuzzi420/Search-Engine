from qdrant_client import QdrantClient, models
from qdrant_client.models import VectorParams, Distance
from chonkie import RecursiveChunker
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

def vectorize() -> None:
    text, titles, urls = get_search_data()
    points = []

    chunker = RecursiveChunker(
        tokenizer="nomic-ai/nomic-embed-text-v1",
        chunk_size=512
    )

    client = QdrantClient("localhost", port=6333)

    for index, (content, title, url) in enumerate(zip(text, titles, urls)):
        print(f"Processing document {index}")

        for chunk in chunker.chunk(content):
            emb = ollama.embeddings(
                model="nomic-embed-text",
                prompt=chunk.text
            )["embedding"]

            points.append({
                "id": str(uuid4()),
                "vector": emb,
                "payload": {
                    "title": title,
                    "url": url,
                }
            })

        if index % 10 == 0:
            client.upsert(
                collection_name="search-engine",
                points=points,
            )
            points.clear()

    if points:
        client.upsert(
            collection_name="search-engine",
            points=points,
        )

if __name__ == "__main__":
    vectorize()