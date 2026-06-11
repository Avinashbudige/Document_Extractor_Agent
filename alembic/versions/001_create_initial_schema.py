"""Create initial database schema with all tables.

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables for the document extraction system."""
    
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('file_format', sa.String(10), nullable=False, comment="'pdf', 'jpeg', 'png', 'txt'"),
        sa.Column('storage_key', sa.String(512), nullable=False, comment='S3 object key'),
        sa.Column('status', sa.String(20), nullable=False, comment="'queued', 'processing', 'completed', 'failed', 'review'"),
        sa.Column('document_type', sa.String(50), nullable=True, comment="'invoice', 'receipt', 'purchase_order', etc."),
        sa.Column('document_type_confidence', sa.DECIMAL(3, 2), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Source metadata (JSONB for flexibility)'),
        sa.Column('uploaded_by', sa.String(100), nullable=True),
    )
    
    # Create indexes for documents table
    op.create_index('idx_documents_status', 'documents', ['status'])
    op.create_index('idx_documents_document_type', 'documents', ['document_type'])
    op.create_index('idx_documents_created_at', 'documents', ['created_at'])
    
    # Create extractions table
    op.create_table(
        'extractions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('extracted_fields', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='Flexible schema per document type'),
        sa.Column('field_confidence_scores', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='{"invoice_number": 0.95, ...}'),
        sa.Column('overall_confidence', sa.DECIMAL(3, 2), nullable=False),
        sa.Column('validation_results', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='[{"rule": "...", "passed": true}, ...]'),
        sa.Column('validation_passed', sa.Boolean(), nullable=False),
        sa.Column('needs_review', sa.Boolean(), nullable=False),
        sa.Column('reviewed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('reviewed_by', sa.String(100), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=False),
        sa.Column('extraction_method', sa.String(50), nullable=False, comment="'llm_gpt4', 'llm_claude', etc."),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_latest', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for extractions table
    op.create_index('idx_extractions_document_id', 'extractions', ['document_id'])
    op.create_index('idx_extractions_needs_review', 'extractions', ['needs_review'])
    op.create_index('idx_extractions_overall_confidence', 'extractions', ['overall_confidence'])
    op.create_index('idx_extractions_created_at', 'extractions', ['created_at'])
    
    # Create extraction_audit_log table
    op.create_table(
        'extraction_audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('extraction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('action', sa.String(20), nullable=False, comment="'created', 'updated', 'reviewed'"),
        sa.Column('actor', sa.String(100), nullable=False, comment='User or system identifier'),
        sa.Column('field_name', sa.String(100), nullable=True),
        sa.Column('old_value', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('new_value', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('change_reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['extraction_id'], ['extractions.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for extraction_audit_log table
    op.create_index('idx_extraction_audit_log_extraction_id', 'extraction_audit_log', ['extraction_id'])
    op.create_index('idx_extraction_audit_log_created_at', 'extraction_audit_log', ['created_at'])
    
    # Create batches table
    op.create_table(
        'batches',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('total_documents', sa.Integer(), nullable=False),
        sa.Column('completed_documents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_documents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(20), nullable=False, comment="'processing', 'completed', 'partial_failure'"),
        sa.Column('uploaded_by', sa.String(100), nullable=True),
    )
    
    # Create indexes for batches table
    op.create_index('idx_batches_status', 'batches', ['status'])
    op.create_index('idx_batches_created_at', 'batches', ['created_at'])
    
    # Create batch_documents junction table
    op.create_table(
        'batch_documents',
        sa.Column('batch_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    )
    
    # Create index for batch_documents table
    op.create_index('idx_batch_documents_batch_id', 'batch_documents', ['batch_id'])


def downgrade() -> None:
    """Drop all tables in reverse order."""
    
    # Drop batch_documents table (junction table, no foreign keys pointing to it)
    op.drop_index('idx_batch_documents_batch_id', table_name='batch_documents')
    op.drop_table('batch_documents')
    
    # Drop batches table
    op.drop_index('idx_batches_created_at', table_name='batches')
    op.drop_index('idx_batches_status', table_name='batches')
    op.drop_table('batches')
    
    # Drop extraction_audit_log table (foreign key to extractions)
    op.drop_index('idx_extraction_audit_log_created_at', table_name='extraction_audit_log')
    op.drop_index('idx_extraction_audit_log_extraction_id', table_name='extraction_audit_log')
    op.drop_table('extraction_audit_log')
    
    # Drop extractions table (foreign key to documents)
    op.drop_index('idx_extractions_created_at', table_name='extractions')
    op.drop_index('idx_extractions_overall_confidence', table_name='extractions')
    op.drop_index('idx_extractions_needs_review', table_name='extractions')
    op.drop_index('idx_extractions_document_id', table_name='extractions')
    op.drop_table('extractions')
    
    # Drop documents table (base table)
    op.drop_index('idx_documents_created_at', table_name='documents')
    op.drop_index('idx_documents_document_type', table_name='documents')
    op.drop_index('idx_documents_status', table_name='documents')
    op.drop_table('documents')
