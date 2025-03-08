# pip install pdfplumber
# pip install pandas
# pip install tabula-py

# This script extracts tables from a PDF file using pdfplumber and saves them as CSV files.
import tabula
import pdfplumber
import pandas as pd

pdf_path = "example.pdf"

# Try extracting with Tabula
dfs = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
if not dfs:  # If Tabula fails, try pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        tables = []
        for page in pdf.pages:
            extracted_tables = page.extract_tables()
            for table in extracted_tables:
                df = pd.DataFrame(table)
                tables.append(df)

# Save extracted tables
for i, df in enumerate(dfs or tables):
    df.to_csv(f"table_{i}.csv", index=False)