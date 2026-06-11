"""SQLAlchemy ORM models for the Document Extraction Agent."""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DECIMAL,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    TIMESTAMP,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


class Document(Base):
    """Document metadata and status tracking.
    
    Stores metadata about uploaded documents including file information,
    processing status, and document type classification.
    """

    __tablename__ = "documents"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # File metadata
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    file_format: Mapped[str] = mapped_column(
        String(10), nullable=False
    )  # 'pdf', 'jpeg', 'png', 'txt'
    storage_key: Mapped[str] = mapped_column(
        String(512), nullable=False
    )  # S3 object key

    # Processing metadata
    status: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # 'queued', 'processing', 'completed', 'failed', 'review'
    document_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # 'invoice', 'receipt', 'purchase_order', etc.
    document_type_confidence: Mapped[Optional[float]] = mapped_column(
        DECIMAL(3, 2), nullable=True
    )

    # Source metadata (JSONB for flexibility)
    source_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, nullable=True)

    # Audit
    uploaded_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    extractions: Mapped[list["Extraction"]] = relationship(
        "Extraction", back_populates="document", cascade="all, delete-orphan"
    )
    batch_associations: Mapped[list["BatchDocument"]] = relationship(
        "BatchDocument", back_populates="document", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_documents_status", "status"),
        Index("idx_documents_document_type", "document_type"),
        Index("idx_documents_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, filename={self.filename}, status={self.status})>"


class Extraction(Base):
    """Extracted field data and validation results.
    
    Stores the structured data extracted from documents, including confidence
    scores, validation results, and review status. JSONB fields provide
    flexibility for different document types with varying schemas.
    """

    __tablename__ = "extractions"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    # Foreign key
    document_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Extracted data (JSONB for flexible schema per document type)
    extracted_fields: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Confidence scores
    field_confidence_scores: Mapped[dict] = mapped_column(
        JSONB, nullable=False
    )  # {"invoice_number": 0.95, ...}
    overall_confidence: Mapped[float] = mapped_column(DECIMAL(3, 2), nullable=False)

    # Validation
    validation_results: Mapped[dict] = mapped_column(
        JSONB, nullable=False
    )  # [{"rule": "...", "passed": true}, ...]
    validation_passed: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Review status
    needs_review: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Processing metadata
    processing_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    extraction_method: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'llm_gpt4', 'llm_claude', etc.

    # Version tracking (for corrections)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_latest: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="extractions")
    audit_logs: Mapped[list["ExtractionAuditLog"]] = relationship(
        "ExtractionAuditLog", back_populates="extraction", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_extractions_document_id", "document_id"),
        Index("idx_extractions_needs_review", "needs_review"),
        Index("idx_extractions_overall_confidence", "overall_confidence"),
        Index("idx_extractions_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Extraction(id={self.id}, document_id={self.document_id}, overall_confidence={self.overall_confidence})>"


class ExtractionAuditLog(Base):
    """Audit trail for extraction data modifications.
    
    Records all changes to extraction data, including who made the change,
    when, and what was modified. Supports compliance and data lineage requirements.
    """

    __tablename__ = "extraction_audit_log"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    # Foreign key
    extraction_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("extractions.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, default=datetime.utcnow
    )

    # Change tracking
    action: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # 'created', 'updated', 'reviewed'
    actor: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # User or system identifier

    # Field-level changes
    field_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    old_value: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    new_value: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Context
    change_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    extraction: Mapped["Extraction"] = relationship(
        "Extraction", back_populates="audit_logs"
    )

    # Indexes
    __table_args__ = (
        Index("idx_extraction_audit_log_extraction_id", "extraction_id"),
        Index("idx_extraction_audit_log_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ExtractionAuditLog(id={self.id}, action={self.action}, actor={self.actor})>"


class Batch(Base):
    """Batch processing tracking.
    
    Tracks status and progress of batch document uploads and processing.
    """

    __tablename__ = "batches"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Batch metadata
    total_documents: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_documents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_documents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Status
    status: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # 'processing', 'completed', 'partial_failure'

    # Audit
    uploaded_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    batch_documents: Mapped[list["BatchDocument"]] = relationship(
        "BatchDocument", back_populates="batch", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_batches_status", "status"),
        Index("idx_batches_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Batch(id={self.id}, total={self.total_documents}, completed={self.completed_documents})>"


class BatchDocument(Base):
    """Many-to-many relationship between batches and documents.
    
    Links documents to their parent batches.
    """

    __tablename__ = "batch_documents"

    # Composite primary key
    batch_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("batches.id", ondelete="CASCADE"),
        primary_key=True,
    )
    document_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Relationships
    batch: Mapped["Batch"] = relationship("Batch", back_populates="batch_documents")
    document: Mapped["Document"] = relationship(
        "Document", back_populates="batch_associations"
    )

    # Indexes
    __table_args__ = (Index("idx_batch_documents_batch_id", "batch_id"),)

    def __repr__(self) -> str:
        return f"<BatchDocument(batch_id={self.batch_id}, document_id={self.document_id})>"
