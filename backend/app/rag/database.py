"""ChromaDB connector and Hybrid search engine.

Purpose:
    Execute dense vector queries, sparse BM25 searches, and hybrid ranking.
Dependencies:
    httpx, json, math, and backend configurations.
"""

import json
import math
from pathlib import Path
import httpx
from typing import Any

from app.core.config import Settings
from app.schemas.rag import DocumentChunk, RetrievedChunk, ChunkMetadata
from app.services.embedding_service import EmbeddingService
from app.utils.logger import log_json


class BM25Scorer:
    """Pure-Python BM25 keyword search indexer and scorer."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b

    def score(self, query: str, documents: list[str]) -> list[float]:
        """Compute BM25 scores for a query across a list of document strings."""
        def tokenize(text: str) -> list[str]:
            return [t.lower().strip(".,:;!?()[]{}") for t in text.split() if t.strip()]

        tokenized_docs = [tokenize(doc) for doc in documents]
        query_tokens = tokenize(query)

        N = len(documents)
        if N == 0 or not query_tokens:
            return [0.0] * N

        doc_lens = [len(doc) for doc in tokenized_docs]
        avg_doc_len = sum(doc_lens) / N

        df = {}
        for token in query_tokens:
            df[token] = sum(1 for doc in tokenized_docs if token in doc)

        idf = {}
        for token in query_tokens:
            df_val = df.get(token, 0)
            idf[token] = math.log(1 + (N - df_val + 0.5) / (df_val + 0.5))

        scores = []
        for doc in tokenized_docs:
            doc_len = len(doc)
            score = 0.0
            for token in query_tokens:
                f = doc.count(token)
                idf_val = idf.get(token, 0.0)
                denom = f + self.k1 * (1 - self.b + self.b * (doc_len / avg_doc_len))
                if denom > 0:
                    score += idf_val * (f * (self.k1 + 1)) / denom
            scores.append(score)

        return scores


class ChromaRAGDatabase:
    """REST API-based ChromaDB client with hybrid search and JSON fallback."""

    def __init__(self, settings: Settings, embedder: EmbeddingService) -> None:
        self._settings = settings
        self._embedder = embedder
        self._base_url = f"http://{settings.chromadb_host}:{settings.chromadb_port}/api/v1"
        self._path = Path("data") / "vector_store.json"
        self._bm25 = BM25Scorer()
        self._client = httpx.Client(timeout=3.5)

    def _is_server_available(self) -> bool:
        """Check if the external ChromaDB server is reachable."""
        try:
            response = self._client.get(f"{self._base_url}/heartbeat")
            return response.status_code == 200
        except Exception:
            return False

    def upsert(self, collection_name: str, chunks: list[DocumentChunk]) -> list[str]:
        """Insert or update embedded chunks in ChromaDB and cache to JSON fallback."""
        vectors = self._embedder.embed_documents([chunk.text for chunk in chunks])

        # Always write to local JSON database first to ensure offline test coverage
        database = self._load_local()
        collection = {item["id"]: item for item in database.get(collection_name, [])}
        for chunk, vector in zip(chunks, vectors, strict=True):
            collection[chunk.id] = {
                "id": chunk.id,
                "text": chunk.text,
                "metadata": chunk.metadata.model_dump(),
                "embedding": vector,
            }
        database[collection_name] = list(collection.values())
        self._save_local(database)

        # Attempt to upload to active ChromaDB REST server if online
        if self._is_server_available():
            try:
                # 1. Get or create collection
                res = self._client.post(
                    f"{self._base_url}/collections",
                    json={"name": collection_name, "metadata": {"hnsw:space": "cosine"}, "get_or_create": True}
                )
                col_data = res.json()
                col_id = col_data["id"]

                # 2. Add documents to collection
                self._client.post(
                    f"{self._base_url}/collections/{col_id}/add",
                    json={
                        "ids": [chunk.id for chunk in chunks],
                        "embeddings": vectors,
                        "metadatas": [chunk.metadata.model_dump() for chunk in chunks],
                        "documents": [chunk.text for chunk in chunks],
                    }
                )
            except Exception as exc:
                log_json(30, "chroma_server_upsert_failed", error=str(exc))

        return [chunk.id for chunk in chunks]

    def query(
        self,
        collection_names: list[str],
        query: str,
        *,
        top_k: int = 5,
        min_score: float = 0.65,
    ) -> list[RetrievedChunk]:
        """Retrieve and rank grounded context chunks using hybrid vector + BM25 scores."""
        query_vector = self._embedder.embed_query(query)
        candidates: list[dict] = []

        if self._is_server_available():
            try:
                for col_name in collection_names:
                    res = self._client.post(
                        f"{self._base_url}/collections",
                        json={"name": col_name, "get_or_create": True}
                    )
                    col_id = res.json()["id"]
                    
                    q_res = self._client.post(
                        f"{self._base_url}/collections/{col_id}/query",
                        json={"query_embeddings": [query_vector], "n_results": 20}
                    )
                    q_data = q_res.json()
                    
                    if q_data.get("ids") and q_data["ids"][0]:
                        for i in range(len(q_data["ids"][0])):
                            candidates.append({
                                "id": q_data["ids"][0][i],
                                "text": q_data["documents"][0][i],
                                "metadata": q_data["metadatas"][0][i],
                                # Convert cosine distance to similarity
                                "vector_score": 1.0 - float(q_data["distances"][0][i] if q_data.get("distances") else 0.5),
                            })
            except Exception:
                candidates = []

        # Fallback to local if no candidates are fetched from the server
        if not candidates:
            database = self._load_local()
            for col_name in collection_names:
                for item in database.get(col_name, []):
                    # Local cosine distance logic
                    score = self._cosine_similarity(query_vector, item["embedding"])
                    candidates.append({
                        "id": item["id"],
                        "text": item["text"],
                        "metadata": item["metadata"],
                        "vector_score": score,
                    })

        if not candidates:
            return []

        # Run BM25 keyword search over all candidates
        bm25_scores = self._bm25.score(query, [c["text"] for c in candidates])
        max_bm25 = max(bm25_scores) if bm25_scores else 0.0

        # Detect if the query is about personal info (prioritize resume)
        personal_markers = (
            "experience", "education", "college", "degree", "skill", "tech stack",
            "achievement", "award", "cgpa", "gpa", "background", "about you",
            "tell me about", "introduce", "who are you", "favourite", "favorite",
            "resume", "work", "intern", "capgemini", "physics wallah",
        )
        query_lower = query.lower()
        is_personal = any(m in query_lower for m in personal_markers)

        retrieved_chunks: list[RetrievedChunk] = []
        for idx, cand in enumerate(candidates):
            # Normalize BM25 score to [0, 1] range
            normalized_bm25 = bm25_scores[idx] / max_bm25 if max_bm25 > 0.0 else 0.0
            
            # Hybrid consolidation: 70% semantic vector, 30% BM25 keyword overlap
            hybrid_score = 0.7 * cand["vector_score"] + 0.3 * normalized_bm25

            # Source-type boosting: resume chunks get priority
            source_type = cand["metadata"].get("source_type", "")
            if source_type == "resume":
                hybrid_score *= 1.25  # Boost resume chunks
            elif source_type == "github" and is_personal:
                hybrid_score *= 0.75  # Penalize GitHub code for personal queries

            if hybrid_score < min_score:
                continue

            metadata = ChunkMetadata(**cand["metadata"])
            chunk = DocumentChunk(id=cand["id"], text=cand["text"], metadata=metadata)
            retrieved_chunks.append(RetrievedChunk(chunk=chunk, score=hybrid_score))

        # Sort descending and take top_k
        return sorted(retrieved_chunks, key=lambda rc: rc.score, reverse=True)[:top_k]

    def _cosine_similarity(self, left: list[float], right: list[float]) -> float:
        numerator = sum(a * b for a, b in zip(left, right, strict=True))
        return max(0.0, min(1.0, numerator))

    def _load_local(self) -> dict[str, list[dict]]:
        if not self._path.exists():
            return {}
        return json.loads(self._path.read_text(encoding="utf-8"))

    def _save_local(self, database: dict[str, list[dict]]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(database, indent=2), encoding="utf-8")
