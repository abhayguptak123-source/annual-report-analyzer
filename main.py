import os
import json
import pandas as pd
from config import OUTPUT_DIR
from fetcher import find_all_pdfs
from extractor import extract_text
from ai_summarizer import extract_ratios_with_ai, generate_summary
from verifier import verify_ratios, verify_summary

os.makedirs(OUTPUT_DIR, exist_ok=True)


def process(company):
    name = company["name"]
    ticker = company["ticker"]
    pdf_path = company["pdf_path"]

    print(f"\n=== {name} ===")
    print(f"  [OK] PDF: {pdf_path}")

    text = extract_text(pdf_path)

    print(f"  [AI] Ratios nikaal raha hoon...")
    ratios = extract_ratios_with_ai(name, text)
    print(f"  [AI] Ratios: {ratios}")

    print(f"  [AI] Summary likh raha hoon...")
    summary = generate_summary(name, ratios)

    r_check = verify_ratios(ratios, text)
    s_check = verify_summary(summary, ratios)

    return {
        "company": name,
        "ticker": ticker,
        "ratios": ratios,
        "ai_summary": summary,
        "verification": {"ratios": r_check, "summary": s_check},
        "status": "ok" if r_check["verified"] and s_check["clean"] else "review",
    }


def save_excel(results, path):
    """Results ko Excel file mein save karta hai."""
    rows = []
    for r in results:
        if r["status"] == "no_report":
            continue

        ratios = r.get("ratios", {})
        row = {
            "Company": r["company"],
            "P/E": ratios.get("pe"),
            "Debt/Equity": ratios.get("debt_equity"),
            "ROE (%)": ratios.get("roe"),
            "ROA (%)": ratios.get("roa"),
            "Current Ratio": ratios.get("current_ratio"),
            "Operating Margin (%)": ratios.get("operating_margin"),
            "Net Margin (%)": ratios.get("net_margin"),
            "EPS": ratios.get("eps"),
            "Book Value": ratios.get("book_value"),
            "Dividend Yield (%)": ratios.get("dividend_yield"),
            "AI Summary": r.get("ai_summary"),
            "Status": r.get("status"),
        }
        rows.append(row)

    if not rows:
        print("[EXCEL] Koi data nahi hai save karne ke liye.")
        return

    df = pd.DataFrame(rows)
    df.to_excel(path, index=False, engine="openpyxl")
    print(f"[EXCEL] Save: {path}")


def main():
    companies = find_all_pdfs()

    if not companies:
        print("[ERROR] Koi PDF nahi mili data/reports/ folder mein!")
        print(f"[INFO] PDF daalo yahan: {os.path.abspath('data/reports')}")
        return

    print(f"[INFO] {len(companies)} PDF mili:")
    for c in companies:
        print(f"   - {c['name']}")
    print()

    results = [process(c) for c in companies]

    # JSON save
    json_path = os.path.join(OUTPUT_DIR, "results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[SAVE] JSON: {json_path}")

    # Excel save
    excel_path = os.path.join(OUTPUT_DIR, "results.xlsx")
    save_excel(results, excel_path)

    # Summary print
    print(f"\n{'='*60}")
    for r in results:
        print(f"{r['company']:25s} | {r['status']}")
        if r["status"] != "no_report":
            print(f"  Ratios: {r['ratios']}")
            print(f"  AI    : {r['ai_summary']}")
            print()


if __name__ == "__main__":
    main()