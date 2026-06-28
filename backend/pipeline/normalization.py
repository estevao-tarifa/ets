import logging
import re
from functools import lru_cache
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def _load_aliases() -> dict[str, list[str]]:
    path = Path(__file__).parent.parent.parent / "data" / "aliases.yaml"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def _normalize_name(name: str) -> str:
    """lowercase + strip + collapse whitespace."""
    return re.sub(r"\s+", " ", name.lower().strip())

def _resolve_alias(name: str, aliases: dict[str, list[str]]) -> str:
    """If name matches any alias list, return the canonical key."""
    norm = _normalize_name(name)
    for canonical, alias_list in aliases.items():
        if norm in [_normalize_name(a) for a in alias_list]:
            return canonical
    return norm

def _invert(name: str) -> str:
    """'integral de função' → also check 'função integral'."""
    parts = name.split()
    if len(parts) >= 3 and parts[1] in ("de", "do", "da", "dos", "das"):
        return " ".join([parts[2]] + [parts[1]] + [parts[0]] + parts[3:])
    return name

def normalize_one(name: str) -> str:
    """Return canonical normalized name."""
    aliases = _load_aliases()
    norm = _normalize_name(name)
    resolved = _resolve_alias(norm, aliases)
    if resolved == norm:
        # Try inverted form
        inv = _invert(norm)
        resolved = _resolve_alias(inv, aliases)
    return resolved

def normalize_concepts(concepts: list[dict]) -> list[dict]:
    """Normalize 'nome' field in each concept dict. Returns new list."""
    return [{**c, "nome": normalize_one(c["nome"])} for c in concepts]
