from pathlib import Path

from sqlalchemy.orm import Session

from app.models import Document, DocumentChunk
from app.documents.parsers import parse_file
from app.documents.chunker import chunk_text


def process_document(
    db: Session,
    document: Document
) -> dict:
    file_path = Path(document.storage_path)

    if not file_path.exists():
        document.processing_status = "failed"
        db.commit()

        raise FileNotFoundError(
            f"File not found at path: {document.storage_path}"
        )

    # Remove old chunks if document is reprocessed
    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document.id
    ).delete()

    document.processing_status = "processing"
    db.commit()

    extracted_items = parse_file(
        file_path=str(file_path),
        file_type=document.file_type
    )

    total_chunks = 0

    for item in extracted_items:
        chunks = chunk_text(item["text"])

        for chunk in chunks:
            document_chunk = DocumentChunk(
                document_id=document.id,
                org_id=document.org_id,
                chunk_index=total_chunks,
                chunk_text=chunk,
                chunk_type=item["content_type"],
                page_number=item.get("page_number"),
                sheet_name=item.get("sheet_name")
            )

            db.add(document_chunk)
            total_chunks += 1

    document.processing_status = "processed"
    db.commit()

    return {
        "document_id": document.id,
        "file_name": document.file_name,
        "chunks_created": total_chunks,
        "status": document.processing_status
    }