# Database Migrations

This directory contains Alembic database migrations for the Document Extraction Agent.

## Setup

1. Ensure PostgreSQL is running and accessible
2. Update the database URL in `alembic.ini` if needed:
   ```ini
   sqlalchemy.url = postgresql://postgres:password@localhost:5432/document_extraction
   ```

## Running Migrations

### Apply all migrations (upgrade to latest)
```bash
alembic upgrade head
```

### Rollback one migration
```bash
alembic downgrade -1
```

### Rollback all migrations
```bash
alembic downgrade base
```

### View migration history
```bash
alembic history
```

### Check current migration version
```bash
alembic current
```

## Creating New Migrations

### Auto-generate migration from model changes
```bash
alembic revision --autogenerate -m "description of changes"
```

### Create empty migration
```bash
alembic revision -m "description of changes"
```

## Database Schema

The initial migration creates the following tables:

### documents
Stores document metadata and processing status
- `id` (UUID, PK): Unique document identifier
- `created_at`, `updated_at` (TIMESTAMP): Audit timestamps
- `filename`, `file_size_bytes`, `file_format`: File metadata
- `storage_key`: S3 object reference
- `status`: Processing status (queued, processing, completed, failed, review)
- `document_type`: Classification (invoice, receipt, purchase_order, etc.)
- `document_type_confidence`: Classification confidence score
- `metadata` (JSONB): Flexible source metadata
- `uploaded_by`: User identifier

**Indexes**: status, document_type, created_at

### extractions
Stores extracted field data and validation results
- `id` (UUID, PK): Unique extraction identifier
- `document_id` (UUID, FK): Reference to documents table
- `created_at`, `updated_at` (TIMESTAMP): Audit timestamps
- `extracted_fields` (JSONB): Flexible schema for different document types
- `field_confidence_scores` (JSONB): Confidence per field
- `overall_confidence` (DECIMAL): Minimum field confidence
- `validation_results` (JSONB): Rule validation outcomes
- `validation_passed` (BOOLEAN): Overall validation status
- `needs_review` (BOOLEAN): Human review flag
- `reviewed_at`, `reviewed_by`, `review_notes`: Review metadata
- `processing_time_ms`: Performance tracking
- `extraction_method`: LLM model used
- `version`, `is_latest`: Version tracking for corrections

**Indexes**: document_id, needs_review, overall_confidence, created_at

### extraction_audit_log
Audit trail for extraction modifications
- `id` (UUID, PK): Unique log entry identifier
- `extraction_id` (UUID, FK): Reference to extractions table
- `created_at` (TIMESTAMP): Log timestamp
- `action`: Type of change (created, updated, reviewed)
- `actor`: User or system identifier
- `field_name`: Specific field modified
- `old_value`, `new_value` (JSONB): Change tracking
- `change_reason`: Context for modification

**Indexes**: extraction_id, created_at

### batches
Batch processing tracking
- `id` (UUID, PK): Unique batch identifier
- `created_at`, `updated_at` (TIMESTAMP): Audit timestamps
- `total_documents`: Documents in batch
- `completed_documents`, `failed_documents`: Progress counters
- `status`: Batch status (processing, completed, partial_failure)
- `uploaded_by`: User identifier

**Indexes**: status, created_at

### batch_documents
Many-to-many relationship between batches and documents
- `batch_id` (UUID, FK, PK): Reference to batches table
- `document_id` (UUID, FK, PK): Reference to documents table

**Indexes**: batch_id

## Design Decisions

1. **JSONB Fields**: Used for `extracted_fields`, `validation_results`, and `metadata` to provide schema flexibility across different document types without requiring schema migrations for new document types.

2. **UUID Primary Keys**: Provides globally unique identifiers, useful for distributed systems and avoiding sequential ID enumeration attacks.

3. **Cascading Deletes**: Foreign keys use `ON DELETE CASCADE` to maintain referential integrity and automatically clean up dependent records.

4. **Indexes**: Strategic indexes on frequently queried columns (status, document_type, needs_review) and foreign keys to optimize query performance.

5. **Timestamps**: All tables include `created_at` and `updated_at` for audit trails and debugging.

6. **Version Tracking**: Extractions table includes `version` and `is_latest` fields to track corrections and maintain history.

7. **Decimal Precision**: Confidence scores use DECIMAL(3,2) to store values 0.00-1.00 with exact precision.

## Validation Requirements

The schema supports the following requirements from the design document:

- **Requirement 9.1**: Document persistence with metadata
- **Requirement 9.2**: Audit trail for extraction modifications
- **Requirement 9.3**: 7-year retention (application-level policy)
- **Requirement 1.5**: Document upload metadata storage
- **Requirement 7.4**: Review corrections tracking
- **Requirement 8.3-8.4**: Batch processing status tracking

## Performance Considerations

1. **JSONB Performance**: PostgreSQL JSONB type supports efficient indexing and querying of JSON data. Consider adding GIN indexes on JSONB columns if specific field queries become frequent.

2. **Connection Pooling**: Use PgBouncer or similar for production deployments to manage connection overhead.

3. **Partitioning**: For high-volume deployments (>100M documents), consider table partitioning by created_at.

4. **Archival**: Implement archival strategy for old documents to maintain query performance.
