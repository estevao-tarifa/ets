import logging
from functools import lru_cache
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    logger.info(f"Loading embedding model: {MODEL_NAME}")
    return SentenceTransformer(MODEL_NAME)

def encode(texts: list[str]) -> list[list[float]]:
    """Returns list of 384-dim float vectors."""
    model = _get_model()
    vectors: np.ndarray = model.encode(texts, convert_to_numpy=True)
    return vectors.tolist()

def encode_one(text: str) -> list[float]:
    return encode([text])[0]
