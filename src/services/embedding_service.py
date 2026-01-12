"""
임베딩 서비스

단일 책임: 텍스트를 벡터로 변환하고 캐싱
sentence-transformers 기반, 파일 기반 캐싱으로 로컬 실행
"""
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from loguru import logger

from src.core.interfaces import EmbeddingProtocol
from src.core.config import get_config


class SentenceTransformerEmbedding(EmbeddingProtocol):
    """sentence-transformers 기반 임베딩 서비스

    파일 기반 캐싱으로 API 호출 없이 로컬에서 임베딩 생성.
    """

    MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DIM = 384

    def __init__(self, cache_dir: Optional[Path] = None):
        config = get_config()
        self._cache_dir = cache_dir or config.data_dir / "embeddings"
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._model = None
        self._cache: Dict[str, np.ndarray] = {}

    @property
    def model(self):
        """Lazy loading - 필요할 때만 모델 로드"""
        if self._model is None:
            logger.info(f"Loading model: {self.MODEL_NAME}")
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.MODEL_NAME)
        return self._model

    def _get_text_hash(self, text: str) -> str:
        """텍스트 해시 생성 (캐시 키)"""
        return hashlib.md5(text.encode()).hexdigest()[:12]

    async def embed(self, text: str) -> List[float]:
        """단일 텍스트 임베딩"""
        text_hash = self._get_text_hash(text)

        # 메모리 캐시 확인
        if text_hash in self._cache:
            return self._cache[text_hash].tolist()

        # 임베딩 생성
        embedding = self.model.encode(text, convert_to_numpy=True)
        self._cache[text_hash] = embedding

        return embedding.tolist()

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """배치 임베딩"""
        if not texts:
            return []

        # 캐시 히트/미스 분리
        uncached_indices = []
        uncached_texts = []
        results: List[Optional[List[float]]] = [None] * len(texts)

        for i, text in enumerate(texts):
            text_hash = self._get_text_hash(text)
            if text_hash in self._cache:
                results[i] = self._cache[text_hash].tolist()
            else:
                uncached_indices.append(i)
                uncached_texts.append(text)

        # 캐시 미스된 것만 임베딩
        if uncached_texts:
            logger.info(f"Embedding {len(uncached_texts)} new texts")
            embeddings = self.model.encode(uncached_texts, convert_to_numpy=True)

            for idx, embedding, text in zip(uncached_indices, embeddings, uncached_texts):
                text_hash = self._get_text_hash(text)
                self._cache[text_hash] = embedding
                results[idx] = embedding.tolist()

        return results

    def save_embeddings(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        name: str
    ) -> Path:
        """임베딩을 파일로 저장

        Args:
            ids: ID 리스트
            embeddings: 임베딩 벡터 리스트
            name: 저장 이름 (jobs/profiles)

        Returns:
            저장된 파일 경로
        """
        # numpy 저장
        arr = np.array(embeddings)
        npy_path = self._cache_dir / f"{name}.npy"
        np.save(npy_path, arr)

        # 메타데이터 저장
        metadata_path = self._cache_dir / f"{name}_metadata.json"
        metadata = {
            "ids": ids,
            "model": self.MODEL_NAME,
            "dim": self.EMBEDDING_DIM,
            "count": len(ids),
        }
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved {len(ids)} embeddings to {npy_path}")
        return npy_path

    def load_embeddings(self, name: str) -> Tuple[List[str], np.ndarray]:
        """임베딩 파일 로드

        Returns:
            (ID 리스트, 임베딩 배열)
        """
        npy_path = self._cache_dir / f"{name}.npy"
        metadata_path = self._cache_dir / f"{name}_metadata.json"

        if not npy_path.exists():
            logger.warning(f"Embedding file not found: {npy_path}")
            return [], np.array([])

        embeddings = np.load(npy_path)

        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        logger.info(f"Loaded {metadata['count']} embeddings from {npy_path}")
        return metadata["ids"], embeddings

    def embeddings_exist(self, name: str) -> bool:
        """임베딩 파일 존재 여부 확인"""
        npy_path = self._cache_dir / f"{name}.npy"
        return npy_path.exists()
