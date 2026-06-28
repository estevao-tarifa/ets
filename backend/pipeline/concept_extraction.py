import json
import logging
import re
from backend.infrastructure.llm import call_llm

logger = logging.getLogger(__name__)

CHUNK_SIZE = 3000  # chars per chunk
OVERLAP = 200


def _chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - OVERLAP
    return chunks


def _parse_concepts_json(raw: str) -> list[dict]:
    """Parse LLM JSON output; returns [] on failure."""
    try:
        # Strip markdown code fences if present
        clean = re.sub(r"```json?\s*|\s*```", "", raw).strip()
        data = json.loads(clean)
        if isinstance(data, dict) and "concepts" in data:
            return data["concepts"]
        if isinstance(data, list):
            return data
        return []
    except json.JSONDecodeError:
        logger.warning("Failed to parse concepts JSON")
        return []


INTRA_PROMPT = """Extraia os conceitos de aprendizagem do trecho abaixo.
Responda APENAS em JSON com este schema (sem comentários, sem texto extra):
{"concepts": [{"nome": "string", "descricao": "string", "nivel": "conceito|subtopico|topico|area", "relacoes": ["nome_conceito_relacionado"]}]}

Trecho:
"""

CROSS_PROMPT = """Abaixo estão listas de conceitos extraídos de diferentes partes de um documento.
Mescle duplicatas óbvias (mesmo conceito, nomes levemente diferentes).
Responda APENAS em JSON:
{"concepts": [{"nome": "string", "descricao": "string", "nivel": "conceito|subtopico|topico|area", "relacoes": ["string"]}]}

Conceitos:
"""


async def extract_concepts(
    markdown: str, provider: str, api_key: str, model: str
) -> list[dict]:
    """Two-pass extraction. Returns list of concept dicts."""
    chunks = _chunk_text(markdown)
    all_concepts: list[dict] = []

    # Pass 1: intra-chunk extraction
    for i, chunk in enumerate(chunks):
        raw = await call_llm(
            INTRA_PROMPT + chunk, provider, api_key, model, max_tokens=1024, json_mode=True
        )
        concepts = _parse_concepts_json(raw)
        logger.info(f"Chunk {i+1}/{len(chunks)}: extracted {len(concepts)} concepts")
        all_concepts.extend(concepts)

    if not all_concepts:
        return []

    # Pass 2: cross-chunk merge (only if > 1 chunk)
    if len(chunks) > 1:
        concepts_str = json.dumps({"concepts": all_concepts[:100]}, ensure_ascii=False)  # limit to 100
        raw2 = await call_llm(
            CROSS_PROMPT + concepts_str, provider, api_key, model, max_tokens=2048, json_mode=True
        )
        merged = _parse_concepts_json(raw2)
        if merged:
            return merged

    return all_concepts
