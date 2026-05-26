import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Document, Organization, User, DocumentChunk
from app.documents.service import process_document


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


def get_or_create_dev_user(db: Session) -> User:
    """
    Temporary development user.

    Later, this will be replaced with real authentication.
    For now, we need a user and organization so every uploaded document
    still has org_id and user_id ownership.
    """

    org = db.query(Organization).filter(
        Organization.name == "Dev Organization"
    ).first()

    if not org:
        org = Organization(
            name="Dev Organization"
        )
        db.add(org)
        db.commit()
        db.refresh(org)

    user = db.query(User).filter(
        User.email == "dev@example.com"
    ).first()

    if not user:
        user = User(
            org_id=org.id,
            email="dev@example.com",
            name="Dev User",
            role="admin"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    dev_user = get_or_create_dev_user(db)

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".txt",
        ".md",
        ".xlsx",
        ".xls",
        ".csv",
        ".png",
        ".jpg",
        ".jpeg"
    }

    original_file_name = file.filename

    if not original_file_name:
        raise HTTPException(
            status_code=400,
            detail="File name is missing"
        )

    file_extension = Path(original_file_name).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}"
        )

    safe_file_name = original_file_name.replace(" ", "_")
    unique_file_name = f"{uuid4()}_{safe_file_name}"

    storage_dir = Path(settings.LOCAL_STORAGE_DIR) / dev_user.org_id
    storage_dir.mkdir(parents=True, exist_ok=True)

    storage_path = storage_dir / unique_file_name

    with open(storage_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document = Document(
        org_id=dev_user.org_id,
        uploaded_by_user_id=dev_user.id,
        file_name=original_file_name,
        file_type=file_extension,
        storage_path=str(storage_path),
        processing_status="uploaded"
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "message": "Document uploaded successfully",
        "document": {
            "id": document.id,
            "org_id": document.org_id,
            "uploaded_by_user_id": document.uploaded_by_user_id,
            "file_name": document.file_name,
            "file_type": document.file_type,
            "storage_path": document.storage_path,
            "processing_status": document.processing_status,
            "created_at": document.created_at
        }
    }


@router.get("/")
def list_documents(
    db: Session = Depends(get_db)
):
    dev_user = get_or_create_dev_user(db)

    documents = db.query(Document).filter(
        Document.org_id == dev_user.org_id
    ).order_by(
        Document.created_at.desc()
    ).all()

    return {
        "documents": [
            {
                "id": doc.id,
                "file_name": doc.file_name,
                "file_type": doc.file_type,
                "storage_path": doc.storage_path,
                "processing_status": doc.processing_status,
                "created_at": doc.created_at
            }
            for doc in documents
        ]
    }


@router.get("/{document_id}")
def get_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    dev_user = get_or_create_dev_user(db)

    document = db.query(Document).filter(
        Document.id == document_id,
        Document.org_id == dev_user.org_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return {
        "document": {
            "id": document.id,
            "org_id": document.org_id,
            "uploaded_by_user_id": document.uploaded_by_user_id,
            "file_name": document.file_name,
            "file_type": document.file_type,
            "storage_path": document.storage_path,
            "processing_status": document.processing_status,
            "created_at": document.created_at
        }
    }
    
    
@router.post("/{document_id}/process")
def process_uploaded_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    dev_user = get_or_create_dev_user(db)

    document = db.query(Document).filter(
        Document.id == document_id,
        Document.org_id == dev_user.org_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    try:
        result = process_document(
            db=db,
            document=document
        )
    except Exception as error:
        document.processing_status = "failed"
        db.commit()

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    return result


@router.get("/{document_id}/chunks")
def get_document_chunks(
    document_id: str,
    db: Session = Depends(get_db)
):
    dev_user = get_or_create_dev_user(db)

    document = db.query(Document).filter(
        Document.id == document_id,
        Document.org_id == dev_user.org_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    chunks = db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document.id,
        DocumentChunk.org_id == dev_user.org_id
    ).order_by(
        DocumentChunk.chunk_index.asc()
    ).all()

    return {
        "document_id": document.id,
        "file_name": document.file_name,
        "chunks_count": len(chunks),
        "chunks": [
            {
                "id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "chunk_type": chunk.chunk_type,
                "page_number": chunk.page_number,
                "sheet_name": chunk.sheet_name,
                "text_preview": chunk.chunk_text[:700],
                "word_count": len(chunk.chunk_text.split()),
                "char_count": len(chunk.chunk_text)
            }
            for chunk in chunks
        ]
    }