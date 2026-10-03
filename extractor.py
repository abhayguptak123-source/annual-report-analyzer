import pdfplumber


def extract_text(pdf_path, max_pages=100):
    """PDF se text nikaalta hai."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[:max_pages]:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
    except Exception as e:
        print(f"[PDF ERROR] {pdf_path}: {e}")
    return text