import logging
from pathlib import Path
import pymupdf4llm

logger = logging.getLogger(__name__)

class ScannedPDFError(Exception):
    pass

def pdf_to_md(path: str) -> str:
    """
    Convert PDF to Markdown using PyMuPDF4LLM.
    Raises ScannedPDFError if extracted text < 100 chars (likely scanned image).
    """
    md = pymupdf4llm.to_markdown(path)
    if len(md.strip()) < 100:
        raise ScannedPDFError(
            f"PDF possivelmente escaneado — texto < 100 caracteres extraídos de {path}"
        )
    logger.info(f"PDF converted: {len(md)} chars from {path}")
    return md
