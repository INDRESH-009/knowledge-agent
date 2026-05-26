from pathlib import Path

import fitz  # PyMuPDF
import pandas as pd
from docx import Document as DocxDocument


def parse_pdf(file_path: str) -> list[dict]:
    """
    Extract text page by page from a text-based PDF.
    This will not work well for scanned PDFs yet.
    """

    pdf = fitz.open(file_path)
    extracted_items = []

    for page_index, page in enumerate(pdf):
        text = page.get_text().strip()

        if text:
            extracted_items.append({
                "text": text,
                "page_number": page_index + 1,
                "sheet_name": None,
                "content_type": "text"
            })

    return extracted_items


def parse_txt_or_md(file_path: str) -> list[dict]:
    text = Path(file_path).read_text(
        encoding="utf-8",
        errors="ignore"
    ).strip()

    if not text:
        return []

    return [{
        "text": text,
        "page_number": None,
        "sheet_name": None,
        "content_type": "text"
    }]


def parse_docx(file_path: str) -> list[dict]:
    doc = DocxDocument(file_path)

    paragraphs = [
        paragraph.text.strip()
        for paragraph in doc.paragraphs
        if paragraph.text.strip()
    ]

    text = "\n".join(paragraphs)

    if not text:
        return []

    return [{
        "text": text,
        "page_number": None,
        "sheet_name": None,
        "content_type": "text"
    }]


def parse_csv(file_path: str) -> list[dict]:
    df = pd.read_csv(file_path)

    text = df.to_csv(index=False)

    return [{
        "text": text,
        "page_number": None,
        "sheet_name": "CSV",
        "content_type": "table"
    }]


def parse_excel(file_path: str) -> list[dict]:
    sheets = pd.read_excel(
        file_path,
        sheet_name=None
    )

    extracted_items = []

    for sheet_name, df in sheets.items():
        text = df.to_csv(index=False)

        if text.strip():
            extracted_items.append({
                "text": text,
                "page_number": None,
                "sheet_name": sheet_name,
                "content_type": "table"
            })

    return extracted_items


def parse_file(file_path: str, file_type: str) -> list[dict]:
    file_type = file_type.lower()

    if file_type == ".pdf":
        return parse_pdf(file_path)

    if file_type in [".txt", ".md"]:
        return parse_txt_or_md(file_path)

    if file_type == ".docx":
        return parse_docx(file_path)

    if file_type == ".csv":
        return parse_csv(file_path)

    if file_type in [".xlsx", ".xls"]:
        return parse_excel(file_path)

    raise ValueError(f"Parsing not yet supported for file type: {file_type}")