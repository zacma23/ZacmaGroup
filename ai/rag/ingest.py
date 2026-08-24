from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OllamaEmbeddings

_client = None
_embeddings = None


def get_qdrant_client():
    global _client
    if _client is None:
        _client = QdrantClient(url="http://localhost:6333", timeout=1.0)
    return _client


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return _embeddings


def ingest_document(file_path: str, collection: str, tenant_id: str) -> int:
    client = get_qdrant_client()
    embeddings = get_embeddings()

    collections = [c.name for c in client.get_collections().collections]
    if collection not in collections:
        client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )

    docs = PyPDFLoader(file_path).load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    vectors = embeddings.embed_documents([chunk.page_content for chunk in chunks])

    points = [
        {
            "id": index,
            "vector": vector,
            "payload": {
                "text": chunk.page_content,
                "tenant_id": tenant_id,
                "source": file_path,
            },
        }
        for index, (vector, chunk) in enumerate(zip(vectors, chunks))
    ]

    client.upsert(collection_name=collection, points=points)
    return len(points)


def retrieve(query: str, collection: str, tenant_id: str, k: int = 4):
    client = get_qdrant_client()
    embeddings = get_embeddings()

    vector = embeddings.embed_query(query)
    results = client.search(
        collection_name=collection,
        query_vector=vector,
        limit=k,
        query_filter={"must": [{"key": "tenant_id", "match": {"value": tenant_id}}]},
    )
    return [result.payload.get("text") for result in results]
