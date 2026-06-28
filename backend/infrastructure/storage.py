import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

def save_pdf(file_bytes: bytes, material_id: int, data_dir: str = "./data") -> str:
    """Save PDF bytes to disk. Returns absolute path."""
    pdfs_dir = Path(data_dir) / "pdfs"
    pdfs_dir.mkdir(parents=True, exist_ok=True)
    path = pdfs_dir / f"material_{material_id}.pdf"
    path.write_bytes(file_bytes)
    logger.info(f"Saved PDF for material {material_id} to {path}")
    return str(path.resolve())
