"""
PDF Text Extraction for P&ID Analysis
Extracts text content from P&ID PDF documents for intelligent processing
"""

import sys
from pathlib import Path

try:
    import PyPDF2
except ImportError:
    print("PyPDF2 not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
    import PyPDF2

def extract_pdf_text(pdf_path: str) -> str:
    """
    Extract all text from a PDF file
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as string
    """
    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    text_content = []

    with open(pdf_file, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)

        print(f"📄 PDF: {pdf_file.name}")
        print(f"📊 Pages: {len(pdf_reader.pages)}")
        print(f"📝 Metadata: {pdf_reader.metadata}")
        print("\n" + "="*80)
        print("EXTRACTING TEXT...")
        print("="*80 + "\n")

        for page_num, page in enumerate(pdf_reader.pages, 1):
            print(f"Processing page {page_num}...")
            page_text = page.extract_text()
            text_content.append(f"\n\n{'='*80}\nPAGE {page_num}\n{'='*80}\n\n{page_text}")

    full_text = "\n".join(text_content)
    return full_text

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_pdf.py <pdf_file_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    try:
        extracted_text = extract_pdf_text(pdf_path)

        # Save to output file
        output_path = Path(pdf_path).stem + "_extracted.txt"
        output_file = Path("/Users/reh3376/repos/plc-gbt/docs/FT") / output_path

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(extracted_text)

        print("\n✅ Text extracted successfully!")
        print(f"📄 Output saved to: {output_file}")
        print(f"📊 Total characters: {len(extracted_text):,}")

        # Show preview
        print("\n" + "="*80)
        print("TEXT PREVIEW (First 2000 characters)")
        print("="*80 + "\n")
        print(extracted_text[:2000])

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

