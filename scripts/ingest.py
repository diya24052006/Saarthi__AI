from pypdf import PdfReader
from pathlib import Path


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

PDF_PATH = "data/bgita.pdf"
OUTPUT_PATH = "data/raw_gita.txt"


# --------------------------------------------------
# LOAD PDF
# --------------------------------------------------

print("Loading Bhagavad Gita PDF...")

reader = PdfReader(PDF_PATH)

print(f"Total pages: {len(reader.pages)}")


# --------------------------------------------------
# EXTRACT TEXT
# --------------------------------------------------

all_pages = []

for page_number, page in enumerate(reader.pages, start=1):

    print(f"Extracting page {page_number}/{len(reader.pages)}...")

    text = page.extract_text()

    if text:
        all_pages.append(
            f"\n\n{'=' * 80}\n"
            f"PAGE {page_number}\n"
            f"{'=' * 80}\n\n"
            f"{text}"
        )


# --------------------------------------------------
# SAVE RAW TEXT
# --------------------------------------------------

output_file = Path(OUTPUT_PATH)

output_file.parent.mkdir(parents=True, exist_ok=True)

output_file.write_text(
    "".join(all_pages),
    encoding="utf-8"
)


print("\nExtraction completed successfully!")
print(f"Saved raw text to: {OUTPUT_PATH}")