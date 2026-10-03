import streamlit as st
import os
import tempfile
from extractor import extract_text
from ai_summarizer import extract_ratios_with_ai, generate_summary
from verifier import verify_ratios, verify_summary


# Page config
st.set_page_config(
    page_title="Annual Report Analyzer",
    page_icon="📊",
    layout="wide",
)

# Header
st.title("📊 Annual Report Analyzer")
st.markdown("*AI-powered extraction of financial ratios from annual reports*")
st.divider()

# Sidebar info
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    Upload any annual report PDF.
    
    **Extracts:**
    - P/E Ratio
    - Debt/Equity
    - ROE
    - ROA
    - Current Ratio
    - Operating Margin
    - Net Profit Margin
    - EPS
    - Book Value
    - Dividend Yield
    
    **Powered by:** Google Gemini AI
    """)

# File uploader
uploaded_file = st.file_uploader(
    "📄 Choose an annual report PDF",
    type=["pdf"],
)

# Analyze button
if uploaded_file is not None:
    st.success(f"✅ File uploaded: **{uploaded_file.name}**")

    if st.button("🚀 Analyze", type="primary", use_container_width=True):
        # Temporary file banao
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name

        try:
            # Step 1: Extract text
            with st.spinner("📖 Reading PDF..."):
                text = extract_text(tmp_path)

            if not text.strip():
                st.error("❌ PDF se text nahi nikal paya. Corrupted ya scanned PDF ho sakti hai.")
                st.stop()

            # Step 2: Extract ratios via AI
            company_name = os.path.splitext(uploaded_file.name)[0]
            with st.spinner(f"🤖 AI is extracting ratios for {company_name}..."):
                ratios = extract_ratios_with_ai(company_name, text)

            # Step 3: Generate summary
            with st.spinner("✍️ Writing summary..."):
                summary = generate_summary(company_name, ratios)

            # Step 4: Verify
            r_check = verify_ratios(ratios, text)
            s_check = verify_summary(summary, ratios)

            # Display results
            st.divider()
            st.header(f"📈 Results: {company_name}")

            # Ratios
            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader("Financial Ratios")

                # Table format
                ratio_labels = {
                    "pe": "P/E Ratio",
                    "debt_equity": "Debt / Equity",
                    "roe": "ROE (%)",
                    "roa": "ROA (%)",
                    "current_ratio": "Current Ratio",
                    "operating_margin": "Operating Margin (%)",
                    "net_margin": "Net Profit Margin (%)",
                    "eps": "EPS (₹)",
                    "book_value": "Book Value (₹)",
                    "dividend_yield": "Dividend Yield (%)",
                }

                import pandas as pd
                rows = []
                for key, label in ratio_labels.items():
                    val = ratios.get(key)
                    rows.append({
                        "Ratio": label,
                        "Value": val if val is not None else "Not found",
                    })

                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True, hide_index=True)

            with col2:
                st.subheader("Verification")
                if r_check["verified"]:
                    st.success("✅ All ratios look valid")
                else:
                    st.warning(f"⚠️ {len(r_check['issues'])} issue(s) found")
                    with st.expander("See issues"):
                        for issue in r_check["issues"]:
                            st.write(f"- {issue}")

                if s_check["clean"]:
                    st.success("✅ Summary verified")
                else:
                    st.warning("⚠️ Summary has extra numbers")
                    with st.expander("See problems"):
                        for p in s_check["problems"]:
                            st.write(f"- {p}")

            # AI Summary
            st.subheader("🤖 AI Summary")
            st.info(summary)

            # Download JSON
            import json
            result = {
                "company": company_name,
                "ratios": ratios,
                "ai_summary": summary,
                "verification": {"ratios": r_check, "summary": s_check},
            }
            st.download_button(
                label="⬇️ Download JSON",
                data=json.dumps(result, indent=2, ensure_ascii=False),
                file_name=f"{company_name}_analysis.json",
                mime="application/json",
            )
	            # Excel download
            import io
            import pandas as pd

            excel_row = {
                "Company": company_name,
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
                "AI Summary": summary,
            }
            df_excel = pd.DataFrame([excel_row])

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df_excel.to_excel(writer, index=False, sheet_name="Analysis")

            st.download_button(
                label="⬇️ Download Excel",
                data=buffer.getvalue(),
                file_name=f"{company_name}_analysis.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        except Exception as e:
            st.error(f"❌ Error: {e}")
        finally:
            # Temp file delete karo
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)