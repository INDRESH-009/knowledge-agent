from datetime import datetime
from uuid import uuid4

from sqlalchemy import String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def generate_uuid() -> str:
    return str(uuid4())


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=generate_uuid
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    users = relationship(
        "User",
        back_populates="organization"
    )

    documents = relationship(
        "Document",
        back_populates="organization"
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=generate_uuid
    )

    org_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("organizations.id"),
        nullable=False,
        index=True
    )

    email: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String,
        default="user"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    organization = relationship(
        "Organization",
        back_populates="users"
    )

    documents = relationship(
        "Document",
        back_populates="uploaded_by"
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=generate_uuid
    )

    org_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("organizations.id"),
        nullable=False,
        index=True
    )

    uploaded_by_user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    file_name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    file_type: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    storage_path: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    processing_status: Mapped[str] = mapped_column(
        String,
        default="uploaded"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    organization = relationship(
        "Organization",
        back_populates="documents"
    )

    uploaded_by = relationship(
        "User",
        back_populates="documents"
    )
    
class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=generate_uuid
    )

    document_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("documents.id"),
        nullable=False,
        index=True
    )

    org_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    chunk_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    chunk_type: Mapped[str] = mapped_column(
        String,
        default="text"
    )

    page_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    sheet_name: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )