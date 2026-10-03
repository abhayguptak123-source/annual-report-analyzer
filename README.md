\# Annual Report Analyzer



An AI-powered Python tool that extracts financial ratios from annual report PDFs and generates analyst summaries using Google Gemini AI.



\## What It Does



\- Reads PDFs from `data/reports/` folder

\- Extracts 10 financial ratios (P/E, Debt/Equity, ROE, ROA, etc.)

\- Generates 2-line AI summary for each company

\- Validates output with sanity checks

\- Saves results to `output/results.json`



\## How To Run



1\. Install dependencies: `pip install -r requirements.txt`

2\. Add Gemini API key in `.env` file

3\. Place PDFs in `data/reports/`

4\. Run: `py main.py`

5\. Check `output/results.json` for results



\## Tech Stack



\- Python 3.10

\- Google Gemini API

\- pdfplumber (PDF reading)

\- python-dotenv (config)



\## Project Structure



\- `config.py` — settings

\- `fetcher.py` — finds PDFs

\- `extractor.py` — reads PDF text

\- `ai\_summarizer.py` — AI calls

\- `verifier.py` — validation

\- `main.py` — runs everything



\## Limitations



\- P/E ratio not always in annual reports (needs market price)

\- Free AI tier has rate limits

\- Different PDF formats may affect accuracy



\## Author



Abhay — AI + Python workflow demo

