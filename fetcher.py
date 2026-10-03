import os
from config import REPORTS_DIR

os.makedirs(REPORTS_DIR, exist_ok=True)


def find_all_pdfs():
    """data/reports/ folder mein jitni bhi PDF hain, unki list return karta hai."""
    if not os.path.exists(REPORTS_DIR):
        return []

    pdfs = []
    for filename in os.listdir(REPORTS_DIR):
        if filename.lower().endswith(".pdf"):
            full_path = os.path.join(REPORTS_DIR, filename)
            # Filename se company ka naam nikaalo (bina .pdf extension ke)
            company_name = os.path.splitext(filename)[0]
            pdfs.append({
                "ticker": company_name.upper(),
                "name": company_name,
                "pdf_path": full_path,
            })

    return pdfs