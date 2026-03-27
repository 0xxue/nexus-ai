"""
Embedding Service — Freely switchable via .env

Supports:
  - local: sentence-transformers (free, no API needed, default)
  - ollama: Ollama local models (free, needs Ollama running)
  - openai: OpenAI embedding API (paid, highest quality)
  - openai_compatible: Any OpenAI-compatible API

Switch by setting EMBEDDING_PROVIDER in .env
"""

import numpy as np
import structlog
from typing import Optional
from app.core.config import get_settings

logger = structlog.get_logger()


class EmbeddingService:
    """Unified embedding interface. Provider selected by .env config."""

    def __init__(self):
        self.settings = get_settings()
        self.provider = self.settings.embedding_provider
        self._engine = None
        logger.info("Embedding provider", provider=self.provider)

    async def embed(self, texts: list[str]) -> np.ndarray:
        """Convert texts to embeddings. Auto-selects provider."""
        if self._engine is None:
            self._engine = self._init_engine()
        return await self._engine(texts)

    def _init_engine(self):
        match self.provider:
            case "local":
                return self._local_engine()
            case "ollama":
                return self._ollama_engine()
            case "openai" | "openai_compatible":
                return self._openai_engine()
            case _:
                logger.warning("Unknown embedding provider, falling back to local", provider=self.provider)
                return self._local_engine()

    def _local_engine(self):
        """sentence-transformers — free, no API, runs on CPU."""
        from sentence_transformers import SentenceTransformer
        model_name = self.settings.embedding_model or "paraphrase-multilingual-MiniLM-L12-v2"
        model = SentenceTransformer(model_name)
        logger.info("Loaded local embedding model", model=model_name)

        async def embed(texts: list[str]) -> np.ndarray:
            return model.encode(texts, normalize_embeddings=True)
        return embed

    def _ollama_engine(self):
        """Ollama local — free, needs Ollama running."""
        import httpx
        base_url = self.settings.ollama_base_url or "http://localhost:11434"
        model_name = self.settings.embedding_model or "nomic-embed-text"
        logger.info("Using Ollama embedding", base_url=base_url, model=model_name)

        async def embed(texts: list[str]) -> np.ndarray:
            embeddings = []
            async with httpx.AsyncClient(timeout=30) as client:
                for text in texts:
                    resp = await client.post(
                        f"{base_url}/api/embeddings",
                        json={"model": model_name, "prompt": text},
                    )
                    resp.raise_for_status()
                    embeddings.append(resp.json()["embedding"])
            return np.array(embeddings)
        return embed

    def _openai_engine(self):
        """OpenAI or any compatible API — paid."""
        from openai import AsyncOpenAI
        api_key = self.settings.embedding_api_key or self.settings.openai_api_key
        base_url = self.settings.embedding_api_base or None
        model_name = self.settings.embedding_model or "text-embedding-3-small"
        client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        logger.info("Using OpenAI embedding", model=model_name, custom_base=bool(base_url))

        async def embed(texts: list[str]) -> np.ndarray:
            response = await client.embeddings.create(input=texts, model=model_name)
            return np.array([d.embedding for d in response.data])
        return embed


# Singleton
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
