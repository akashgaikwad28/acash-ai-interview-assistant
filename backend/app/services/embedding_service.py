"""Embedding generation service.

Purpose:
    Produce vector embeddings for RAG chunks and user queries.
Responsibilities:
    Use Gemini embeddings when configured and provide a deterministic local
    fallback for development/test environments.
Dependencies:
    Optional google-genai SDK; hashlib for local fallback.
Usage:
    vectors = EmbeddingService(settings).embed_documents(["hello"])
"""

from hashlib import sha256
from math import sqrt

from app.core.config import Settings
from app.utils.logger import log_json


class EmbeddingService:
    """Embedding adapter for Gemini and local deterministic embeddings."""

    dimensions = 768

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = None

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple documents."""
        if not texts:
            return []
            
        if self._settings.gemini_api_key:
            from google import genai
            if self._client is None:
                self._client = genai.Client(api_key=self._settings.gemini_api_key)
                
            all_embeddings = []
            # Batch in chunks of 50 to avoid rate limits
            for i in range(0, len(texts), 50):
                batch = texts[i:i + 50]
                response = self._client.models.embed_content(
                    model=self._settings.gemini_embedding_model,
                    contents=batch,
                )
                for emb in response.embeddings:
                    all_embeddings.append([float(v) for v in emb.values])
            return all_embeddings
            
        return [self._embed_locally(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        """Embed one query or document string."""

        if self._settings.gemini_api_key:
            return self._embed_with_gemini(text)
        return self._embed_locally(text)

    def _embed_with_gemini(self, text: str) -> list[float]:
        """Call Gemini embeddings through the google-genai SDK when available."""

        from google import genai  # type: ignore

        if self._client is None:
            self._client = genai.Client(api_key=self._settings.gemini_api_key)

        response = self._client.models.embed_content(
            model=self._settings.gemini_embedding_model,
            contents=text,
        )
        values = response.embeddings[0].values
        return [float(value) for value in values]

    def _embed_locally(self, text: str) -> list[float]:
        """Create a stable normalized hash embedding for offline development."""

        stopwords = {
            "what", "are", "the", "you", "have", "do", "did", "does", "is", "was", "were", "been", 
            "has", "had", "a", "an", "of", "in", "on", "at", "to", "for", "with", "about", "your", 
            "his", "he", "she", "him", "her", "me", "my", "i", "we", "us", "they", "them", "their", 
            "our", "and", "or", "but", "if", "then", "else", "not", "no", "yes", "how", "why", "who", 
            "where", "when", "this", "that", "these", "those", "can", "could", "would", "should", "here"
        }

        vector = [0.0] * self.dimensions
        raw_tokens = [token.strip(".,:;!?()[]{}*•-").lower() for token in text.split() if token.strip()]
        
        tokens = []
        import re
        for token in raw_tokens:
            if not token or token in stopwords:
                continue
            
            # Split trailing digits (e.g., gemini2025 -> gemini and 2025)
            match = re.match(r"^([a-zA-Z]+)(\d+)$", token)
            if match:
                parts = [match.group(1), match.group(2)]
            else:
                parts = [token]
                
            for part in parts:
                if part in stopwords:
                    continue
                # Simple stemming / normalization
                if part == "built":
                    part = "build"
                elif part == "done":
                    part = "do"
                elif part.endswith("s") and len(part) > 3:
                    part = part[:-1]
                elif part.endswith("ing") and len(part) > 5:
                    part = part[:-3]
                elif part.endswith("ed") and len(part) > 4:
                    part = part[:-2]
                    
                tokens.append(part)

        for token in tokens or [text]:
            digest = sha256(token.encode("utf-8")).digest()
            for offset, byte in enumerate(digest):
                index = (byte + offset * 31) % self.dimensions
                vector[index] += 1.0
                
        norm = sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]
