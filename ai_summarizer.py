import os
import json
import re
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODELS = [
    "gemini-flash-latest",
    "gemini-2.5-flash",
    "gemini-3.5-flash",
]

def _call_gemini(prompt, max_retries=3):
    """Gemini ko call karta hai — har model try karta hai, retry ke saath."""
    last_error = None

    for model_name in MODELS:
        for attempt in range(1, max_retries + 1):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                print(f"  [OK] Model: {model_name}")
                return response.text.strip()
            except Exception as e:
                err_msg = str(e)
                last_error = err_msg

                if "503" in err_msg or "429" in err_msg or "UNAVAILABLE" in err_msg:
                    if attempt < max_retries:
                        wait = attempt * 5
                        print(f"  [RETRY] {model_name} busy. {wait}s wait... ({attempt}/{max_retries})")
                        time.sleep(wait)
                        continue
                    else:
                        print(f"  [FAIL] {model_name} 3 tries ke baad fail. Next model try...")
                        break
                else:
                    raise

    raise Exception(f"Sab models fail. Last error: {last_error}")


def extract_ratios_with_ai(company_name, pdf_text):
    """PDF text se Gemini AI ke through ratios nikalwata hai."""
    text_chunk = pdf_text[:80000]
    prompt = f"""You are a financial analyst. From the following annual report text of {company_name}, extract these 10 financial ratios:

1. P/E Ratio (Price to Earnings) - key: "pe"
2. Debt to Equity Ratio - key: "debt_equity"
3. ROE (Return on Equity) in percentage - key: "roe"
4. ROA (Return on Assets) in percentage - key: "roa"
5. Current Ratio - key: "current_ratio"
6. Operating Margin in percentage - key: "operating_margin"
7. Net Profit Margin in percentage - key: "net_margin"
8. EPS (Earnings Per Share) - key: "eps"
9. Book Value per share - key: "book_value"
10. Dividend Yield in percentage - key: "dividend_yield"

IMPORTANT RULES:
- Return ONLY a valid JSON object. No explanation, no markdown, no code blocks.
- If a ratio is not found in the text, use null.
- Numbers only (no % symbol, no commas).
- Example output format: {{"pe": 24.5, "debt_equity": 0.42, "roe": 9.8, "roa": 5.2, "current_ratio": 1.8, "operating_margin": 18.5, "net_margin": 12.3, "eps": 45.6, "book_value": 320.5, "dividend_yield": 1.2}}

Annual report text:
---
{text_chunk}
---

Return ONLY the JSON object:"""

    try:
        raw = _call_gemini(prompt)

        # Markdown strip karo
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        data = json.loads(raw)

        return {
            "pe": data.get("pe"),
            "debt_equity": data.get("debt_equity"),
            "roe": data.get("roe"),
            "roa": data.get("roa"),
            "current_ratio": data.get("current_ratio"),
            "operating_margin": data.get("operating_margin"),
            "net_margin": data.get("net_margin"),
            "eps": data.get("eps"),
            "book_value": data.get("book_value"),
            "dividend_yield": data.get("dividend_yield"),
        }
    except json.JSONDecodeError as e:
        print(f"[AI JSON ERROR] {company_name}: {e}")
        return {"pe": None, "debt_equity": None, "roe": None}
    except Exception as e:
        print(f"[AI RATIO ERROR] {company_name}: {e}")
        return {"pe": None, "debt_equity": None, "roe": None}


def generate_summary(company_name, ratios):
    """Gemini se 2-line summary banwata hai."""
    prompt = f"""You are a financial analyst. Given these ratios for {company_name}:
- P/E: {ratios.get('pe')}
- Debt/Equity: {ratios.get('debt_equity')}
- ROE: {ratios.get('roe')}%

Write EXACTLY 2 lines:
Line 1: Valuation + leverage takeaway.
Line 2: Profitability takeaway.
No preamble. No bullet points. Just 2 sentences."""

    try:
        return _call_gemini(prompt)
    except Exception as e:
        return f"[AI ERROR] {e}"