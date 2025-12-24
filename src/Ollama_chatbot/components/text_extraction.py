import os
from ensure import ensure_annotations
from typing import Dict, Optional 
from pathlib import Path
import logging
from PyPDF2 import PdfReader

# -------------------------------------------------------------------
# Logging configuration
# -------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# -------------------------------------------------------------------
# Custom Exceptions
# -------------------------------------------------------------------
class PDFTextExtractionError(Exception):
    """Raised when PDF text extraction fails."""

# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------
@ensure_annotations
def _clean_text(text: str) -> str:
    """
    Clean extracted text for downstream NLP / LLM usage.
    """
    # Remove excessive whitespace
    text = text.replace("\x00", " ")
    text = " ".join(text.split())
    return text.strip()

# -------------------------------------------------------------------
# Core extraction function
# -------------------------------------------------------------------
@ensure_annotations
def extract_text_from_pdf(pdf_path: str, min_text_length: int = 20, preserve_page_breaks: bool = True) -> Dict:
    """
    Extract the text from the PDF file using PyPDF2 

    Args: 
        pdf_path (str): Path to the pdf file
        preserve_page_breaks (bool): Whether to insert page separators.
        
    Returns:
        Dict with:
            - full_text (str | None)
            - page_texts (List[str])
            - num_pages (int)
            - empty_pages (List[int])
            - extraction_success (bool)

    Returns:
        Dict with:
            - full_text (str | None)
            - page_texts (List[str])
            - num_pages (int)
            - empty_pages (List[int])
            - extraction_success (bool)
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Input file must be a PDF")

    try: 
        reader = PdfReader(str(pdf_path))
    except Exception as e:
        raise PDFTextExtractionError("Invalid or corrupted PDF") from e
    
    page_texts: List[str] = []
    empty_pages: List[int] = []

    for idx, page in enumerate(reader.pages):
        try: 
            text = page.extract_text()
        except Exception as e:
            logger.warning(f"failed to extract text from the page {idx}: {e}")
            empty_pages.append(idx)
            page_texts.append("")
            continue
        
        if not text or len(text.strip()) < min_text_length:
            empty_pages.append(idx)
            page_texts.append("")
            continue
        
        cleaned_text = _clean_text(text)
        page_texts.append(cleaned_text)

    if preserve_page_breaks:
        full_text = "\n\n------ PAGE BREAK ------\n\n".join(t for t in page_texts if t)
    else: 
        full_text = "\n\n".join(t for t in page_texts if t)
    extraction_success = bool(full_text and full_text.strip())

    if not extraction_success:
        logger.error("No extractable text found")
        raise PDFTextExtractionError("PDF contains no extractable text")

    return {
        "full_text": full_text,
        "page_texts": page_texts,
        "num_pages": len(reader.pages),
        "empty_pages": empty_pages,
        "extraction_success": extraction_success
    }