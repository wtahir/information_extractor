import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from raw PDF bytes using PyMuPDF
    
    Args:
        pdf_bytes: Raw PDF content as bytes
        
    Returns:
        Extracted text as a single string
    """
    try:
        # Open directly from bytes
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = []
        
        for page in doc:
            page_text = page.get_text()
            if page_text.strip():  # Skip empty pages
                text.append(page_text)
        
        return "\n".join(text)
    
    except Exception as e:
        raise ValueError(f"PDF text extraction failed: {str(e)}")