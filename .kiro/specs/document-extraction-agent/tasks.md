# Implementation Plan: Document Extraction Agent

## Overview

This implementation plan follows a 7-phase build order to create a production-ready document extraction system using Python, FastAPI, LangGraph, PostgreSQL, and property-based testing. The system will process business documents (invoices, receipts, purchase orders, insurance policies, contracts) with AI-powered extraction, validation, confidence scoring, and human-in-the-loop review.

**Technology Stack**: Python 3.11+, FastAPI, LangGraph, PostgreSQL, SQLAlchemy, Hypothesis (property testing), pytest, PyMuPDF, Tesseract/EasyOCR, OpenAI/Anthropic LLMs

**Build Order**:
1. Foundation (project setup, database, API skeleton)
2. Core Pipeline (document processor, text extraction, storage)
3. Extraction (LangGraph agent, LLM integration, schemas)
4. Validation (rule engine, confidence scoring)
5. Review System (review queue, routing, corrections)
6. Advanced Features (batch processing, OCR, multi-format)
7. Production (monitoring, security, performance, testing)

## Tasks

- [ ] 1. Phase 1: Foundation - Project Setup and Core Infrastructure
  - [x] 1.1 Initialize Python project with Poetry/pip and create directory structure
    - Create pyproject.toml with dependencies: fastapi, uvicorn, sqlalchemy, psycopg2, langgraph, langchain, hypothesis, pytest
    - Create directory structure: src/api, src/processors, src/agents, src/validation, src/storage, src/models, tests/
    - Set up .env template for configuration (DATABASE_URL, LLM_API_KEY, S3_BUCKET, etc.)
    - _Requirements: 14.1, 14.2, 14.3, 14.4_

  - [ ]* 1.2 Write property test for project setup validation
    - **Property: Environment Configuration Completeness**
    - **Validates: Requirements 14.1-14.5**

  - [x] 1.3 Create PostgreSQL database schema with all tables
    - Implement documents table with indexes
    - Implement extractions table with JSONB fields for flexibility
    - Implement extraction_audit_log table for change tracking
    - Implement batches and batch_documents tables
    - Create database migration script using Alembic
    - _Requirements: 9.1, 9.2, 9.3_

  - [ ]* 1.4 Write unit tests for database schema and migrations
    - Test table creation and constraints
    - Test indexes and foreign keys
    - _Requirements: 9.1_

  - [x] 1.5 Create FastAPI application skeleton with router structure
    - Set up main FastAPI app with CORS, error handlers
    - Create routers: documents_router, extractions_router, batches_router, health_router
    - Implement basic health check endpoint (GET /v1/health)
    - _Requirements: 17.4_

  - [ ]* 1.6 Write property test for API skeleton
    - **Property 47: Health Check Status**
    - **Validates: Requirements 17.4**

  - [-] 1.7 Set up SQLAlchemy models and database session management
    - Create Document, Extraction, ExtractionAuditLog, Batch models
    - Implement database session dependency for FastAPI
    - Create connection pooling configuration
    - _Requirements: 9.1_

  - [ ] 1.8 Implement S3-compatible object storage client
    - Create StorageClient class with upload, download, delete methods
    - Support AWS S3 and MinIO through configuration
    - Implement pre-signed URL generation
    - _Requirements: 1.5, 9.4_

  - [ ]* 1.9 Write unit tests for storage client
    - Test upload and download operations
    - Test error handling for network failures
    - _Requirements: 9.4_

- [ ] 2. Checkpoint - Ensure foundation tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 3. Phase 2: Core Pipeline - Document Processing and Text Extraction
  - [ ] 3.1 Implement document upload API endpoint (POST /v1/documents/upload)
    - Accept multipart/form-data with file and metadata
    - Validate file format (PDF, JPEG, PNG, TXT) and size (≤50MB)
    - Return 413 for oversized files, 415 for unsupported formats
    - Generate unique document ID and return within 200ms
    - Store original file to S3 and metadata to database
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [ ]* 3.2 Write property tests for document upload
    - **Property 1: Supported Format Acceptance**
    - **Validates: Requirements 1.1, 1.2, 1.4**

  - [ ]* 3.3 Write property test for document persistence
    - **Property 2: Document Persistence Completeness**
    - **Validates: Requirements 1.5, 9.1**

  - [ ] 3.4 Create DocumentProcessor class for multi-format text extraction
    - Implement extract_text() method dispatching by format
    - Add PDF text extraction using PyMuPDF
    - Add plain text file reading
    - Preserve text position metadata for structured extraction
    - _Requirements: 3.1, 3.4_

  - [ ]* 3.5 Write property test for text extraction
    - **Property 6: Text Extraction Completeness**
    - **Validates: Requirements 3.1, 3.2, 3.4**

  - [ ] 3.6 Implement error handling and logging for document processing
    - Log extraction failures with document ID and error details
    - Mark document status as 'failed' in database
    - Emit structured logs with correlation IDs
    - _Requirements: 3.3, 17.5_

  - [ ]* 3.7 Write property test for extraction failure handling
    - **Property 7: Extraction Failure Handling**
    - **Validates: Requirements 3.3**

  - [ ] 3.8 Implement document status query endpoint (GET /v1/documents/{id})
    - Query document metadata from database
    - Return 404 if document not found
    - Return status, document_type, upload timestamp, processing metadata
    - _Requirements: 10.1_

  - [ ]* 3.9 Write unit tests for status query endpoint
    - Test successful retrieval
    - Test 404 for non-existent documents
    - _Requirements: 10.1_

- [ ] 4. Checkpoint - Ensure core pipeline tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Phase 3: Extraction - LangGraph Agent and LLM Integration
  - [ ] 5.1 Create extraction schema data models and JSON schema definitions
    - Define ExtractionSchema model with fields, types, validation_rules
    - Create JSON schemas for invoice, receipt, purchase_order document types
    - Implement schema parser that loads schemas from JSON files
    - _Requirements: 4.1, 16.1_

  - [ ]* 5.2 Write property test for schema parsing
    - **Property 42: Schema Parsing Validity**
    - **Validates: Requirements 16.1**

  - [ ]* 5.3 Write property test for schema parsing errors
    - **Property 43: Schema Parsing Error Messages**
    - **Validates: Requirements 16.2**

  - [ ]* 5.4 Write property test for schema round-trip
    - **Property 44: Schema Round-Trip Property**
    - **Validates: Requirements 16.4**

  - [ ]* 5.5 Write property test for schema required field validation
    - **Property 45: Schema Required Field Validation**
    - **Validates: Requirements 16.5**

  - [ ] 5.6 Implement LangGraph state machine for extraction agent
    - Create ExtractionState model with all state fields
    - Define state machine nodes: parse, extract, validate, score, route
    - Set up transitions between nodes
    - Implement StateGraph using LangGraph
    - _Requirements: 4.1, 4.5_

  - [ ]* 5.7 Write unit tests for state machine transitions
    - Test each node function independently
    - Test state transitions for success and error paths
    - _Requirements: 4.1_

  - [ ] 5.8 Implement document type classification in parse node
    - Use LLM to classify document as invoice, receipt, purchase_order, etc.
    - Return classification confidence score
    - Mark documents with confidence <0.7 for manual type selection
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [ ]* 5.9 Write property test for document type classification
    - **Property 4: Document Type Classification**
    - **Validates: Requirements 2.1, 2.4**

  - [ ]* 5.10 Write property test for low confidence type routing
    - **Property 5: Low Confidence Type Routing**
    - **Validates: Requirements 2.3**

  - [ ] 5.11 Implement LLM integration for field extraction in extract node
    - Set up LangChain LLM client (OpenAI/Anthropic)
    - Create prompt template with document type and extraction schema
    - Use structured output mode (JSON schema) for reliable extraction
    - Implement retry logic with exponential backoff
    - Extract fields per schema and return as structured JSON
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [ ]* 5.12 Write property test for schema application
    - **Property 8: Schema Application**
    - **Validates: Requirements 4.1, 4.5**

  - [ ]* 5.13 Write property test for JSON output validity
    - **Property 9: JSON Output Validity**
    - **Validates: Requirements 4.5**

  - [ ] 5.14 Implement extraction results retrieval endpoint (GET /v1/documents/{id}/extraction)
    - Query extraction from database by document_id
    - Return extracted_fields, confidence_scores, validation_results
    - Return 404 if document not found or extraction not complete
    - Include processing_time_ms and needs_review flag
    - _Requirements: 10.1, 10.3_

  - [ ]* 5.15 Write property test for extraction retrieval
    - **Property 26: Extraction Retrieval by ID**
    - **Validates: Requirements 10.1**

- [ ] 6. Checkpoint - Ensure extraction agent tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Phase 4: Validation - Rule Engine and Confidence Scoring
  - [ ] 7.1 Create ValidationEngine with pluggable rule system
    - Define ValidationRule base class and ValidationResult model
    - Implement rule registry pattern for dynamic rule loading
    - Create validation rule decorator for registering rules
    - _Requirements: 6.1, 14.2_

  - [ ]* 7.2 Write property test for validation rule execution
    - **Property 13: Validation Rule Execution**
    - **Validates: Requirements 6.1**

  - [ ] 7.3 Implement built-in validation rules for common field types
    - Date format validation (ISO 8601, MM/DD/YYYY, etc.)
    - Amount field validation (positive, proper decimal precision)
    - Field range validation (min/max values)
    - Regex pattern matching for custom formats
    - _Requirements: 6.2, 6.3_

  - [ ]* 7.4 Write property test for field format validation
    - **Property 14: Field Format Validation**
    - **Validates: Requirements 6.2, 6.3**

  - [ ] 7.5 Implement cross-field validation rules for invoices
    - Invoice total validation: |total - (sum(line_items) + tax)| ≤ 0.01
    - Line item amount validation: amount == quantity * unit_price
    - Date range validation (invoice date not in future)
    - _Requirements: 6.4_

  - [ ]* 7.6 Write property test for invoice total validation
    - **Property 15: Invoice Total Validation**
    - **Validates: Requirements 6.4**

  - [ ] 7.7 Implement custom validation rule loading from configuration
    - Support loading custom rule Python modules from config directory
    - Validate rule signatures and automatically register
    - _Requirements: 6.6, 14.2_

  - [ ]* 7.8 Write property test for custom rule execution
    - **Property 17: Custom Rule Execution**
    - **Validates: Requirements 6.6**

  - [ ] 7.9 Implement validation failure recording in validate node
    - Store ValidationResult for each rule with passed/failed status
    - Record specific error messages for failed rules
    - _Requirements: 6.5_

  - [ ]* 7.10 Write property test for validation failure recording
    - **Property 16: Validation Failure Recording**
    - **Validates: Requirements 6.5**

  - [ ] 7.11 Create ConfidenceScorer component with scoring algorithm
    - Calculate base confidence from LLM metadata (logprobs)
    - Apply validation boosts (+0.1 per passed rule)
    - Apply validation penalties (-0.2 per failed rule)
    - Clamp scores to [0.0, 1.0] range
    - Calculate overall confidence as min(field_confidences)
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ]* 7.12 Write property test for confidence score range
    - **Property 10: Confidence Score Range**
    - **Validates: Requirements 5.1**

  - [ ]* 7.13 Write property test for validation impact on confidence
    - **Property 11: Validation Impact on Confidence**
    - **Validates: Requirements 5.3, 5.4**

  - [ ] 7.14 Integrate ConfidenceScorer into score node of state machine
    - Pass extraction and validation results to scorer
    - Store field-level and overall confidence scores in state
    - _Requirements: 5.5_

  - [ ]* 7.15 Write property test for confidence score persistence
    - **Property 12: Confidence Score Persistence**
    - **Validates: Requirements 5.5**

- [ ] 8. Checkpoint - Ensure validation and scoring tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Phase 5: Review System - Queue, Routing, and Corrections
  - [ ] 9.1 Implement ReviewRouter logic in route node
    - Check if any field confidence < configured threshold
    - Check if any validation rule failed
    - Set needs_review flag based on routing logic
    - Support per-document-type thresholds from configuration
    - _Requirements: 7.1, 7.2, 14.3_

  - [ ]* 9.2 Write property test for review routing logic
    - **Property 18: Review Routing Logic**
    - **Validates: Requirements 7.1, 7.2**

  - [ ]* 9.3 Write property test for per-type confidence thresholds
    - **Property 36: Per-Type Confidence Thresholds**
    - **Validates: Requirements 14.3**

  - [ ] 9.4 Create review queue query endpoint (GET /v1/extractions?needs_review=true)
    - Query extractions with needs_review=true from database
    - Support filtering by document_type, confidence_range, validation_status
    - Return extraction with original document reference
    - _Requirements: 7.6_

  - [ ]* 9.5 Write property test for review queue filtering
    - **Property 21: Review Queue Filtering**
    - **Validates: Requirements 7.6**

  - [ ] 9.6 Implement extraction correction endpoint (PATCH /v1/extractions/{id})
    - Accept corrected field values from reviewer
    - Create new extraction version with corrected data
    - Mark old version as superseded (is_latest=false)
    - Create audit log entry with old and new values
    - _Requirements: 7.4, 9.2_

  - [ ]* 9.7 Write property test for review correction persistence
    - **Property 19: Review Correction Persistence**
    - **Validates: Requirements 7.4**

  - [ ]* 9.8 Write property test for audit trail creation
    - **Property 24: Audit Trail Creation**
    - **Validates: Requirements 9.2, 13.5**

  - [ ] 9.9 Implement extraction approval endpoint (POST /v1/extractions/{id}/approve)
    - Mark extraction as reviewed and approved
    - Set reviewed_at timestamp and reviewed_by user
    - Update extraction status to 'verified'
    - _Requirements: 7.5_

  - [ ]* 9.10 Write property test for review approval status
    - **Property 20: Review Approval Status**
    - **Validates: Requirements 7.5**

  - [ ] 9.11 Implement extraction history endpoint (GET /v1/extractions/{id}/history)
    - Return all versions of the extraction in chronological order
    - Include audit log entries with changes and reviewer identities
    - _Requirements: 9.5_

  - [ ]* 9.12 Write property test for extraction history completeness
    - **Property 25: Extraction History Completeness**
    - **Validates: Requirements 9.5**

- [ ] 10. Checkpoint - Ensure review system tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Phase 6: Advanced Features - Batch Processing and OCR
  - [ ] 11.1 Implement batch upload endpoint (POST /v1/documents/batch)
    - Accept up to 100 files in multipart/form-data
    - Create batch record and associate all documents
    - Enqueue documents for parallel processing
    - Return batch_id and document_ids list
    - _Requirements: 1.6, 8.3_

  - [ ]* 11.2 Write property test for batch size acceptance
    - **Property 3: Batch Size Acceptance**
    - **Validates: Requirements 1.6, 8.3**

  - [ ] 11.3 Implement task queue for parallel document processing
    - Set up Celery with Redis backend for task distribution
    - Create process_document task that runs extraction agent
    - Configure concurrency limits per worker node
    - Implement result tracking and error handling
    - _Requirements: 8.1, 8.2_

  - [ ]* 11.4 Write unit tests for task queue processing
    - Test task enqueueing and execution
    - Test error handling and retries
    - _Requirements: 8.1_

  - [ ] 11.5 Implement batch status endpoint (GET /v1/batches/{id}/status)
    - Query batch with completed, in-progress, failed document counts
    - Ensure counts sum to total_documents
    - Return status: 'processing', 'completed', 'partial_failure'
    - _Requirements: 8.4_

  - [ ]* 11.6 Write property test for batch processing status accuracy
    - **Property 22: Batch Processing Status Accuracy**
    - **Validates: Requirements 8.4**

  - [ ] 11.7 Implement batch fault isolation
    - Ensure document processing failures don't stop other documents
    - Track failed documents separately in batch status
    - Allow retry of individual failed documents
    - _Requirements: 8.5_

  - [ ]* 11.8 Write property test for batch fault isolation
    - **Property 23: Batch Fault Isolation**
    - **Validates: Requirements 8.5**

  - [ ] 11.9 Implement OCR engine integration for image documents
    - Create OCREngine interface with Tesseract and EasyOCR implementations
    - Add configuration option to select OCR engine
    - Implement image preprocessing (enhancement, deskew, denoise)
    - Apply preprocessing when image quality <150 DPI
    - Extract text with character-level confidence scores
    - _Requirements: 14.4, 15.1, 15.2, 15.3_

  - [ ]* 11.10 Write property test for OCR engine configuration
    - **Property 37: OCR Engine Configuration**
    - **Validates: Requirements 14.4**

  - [ ]* 11.11 Write property test for OCR text region detection
    - **Property 39: OCR Text Region Detection**
    - **Validates: Requirements 15.1, 15.2**

  - [ ]* 11.12 Write property test for low quality image preprocessing
    - **Property 40: Low Quality Image Preprocessing**
    - **Validates: Requirements 15.3**

  - [ ] 11.13 Integrate OCR into DocumentProcessor for JPEG and PNG formats
    - Update extract_text() to use OCR for image formats
    - Handle OCR failures with descriptive error messages
    - _Requirements: 3.2, 15.5_

  - [ ]* 11.14 Write property test for OCR failure error reporting
    - **Property 41: OCR Failure Error Reporting**
    - **Validates: Requirements 15.5**

- [ ] 12. Checkpoint - Ensure batch and OCR tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 13. Phase 7: Production - Monitoring, Security, and Testing
  - [ ] 13.1 Implement authentication and authorization middleware
    - Add JWT token validation for all API endpoints
    - Require Bearer token in Authorization header
    - Return 401 for missing or invalid tokens
    - _Requirements: 13.2_

  - [ ]* 13.2 Write property test for authentication requirement
    - **Property 32: Authentication Requirement**
    - **Validates: Requirements 13.2**

  - [ ] 13.3 Implement data encryption at rest
    - Configure database encryption using AES-256
    - Encrypt PII fields at application level before storage
    - Store encryption keys in secure key management service
    - _Requirements: 13.1, 13.4_

  - [ ]* 13.4 Write property test for PII encryption at rest
    - **Property 31: PII Encryption at Rest**
    - **Validates: Requirements 13.1, 13.4**

  - [ ] 13.5 Implement TLS/HTTPS configuration
    - Configure Uvicorn to enforce TLS 1.2+
    - Set up SSL certificate loading from environment
    - _Requirements: 13.3_

  - [ ]* 13.6 Write unit tests for TLS configuration
    - Test HTTPS-only enforcement
    - _Requirements: 13.3_

  - [ ] 13.7 Implement PII redaction in logs
    - Create logging filter that masks PII fields
    - Apply filter to all structured log output
    - Support configuration of PII field patterns
    - _Requirements: 13.5, 13.6_

  - [ ]* 13.8 Write property test for PII redaction in logs
    - **Property 33: PII Redaction in Logs**
    - **Validates: Requirements 13.6**

  - [ ] 13.9 Implement Prometheus metrics exposition
    - Add prometheus-client dependency
    - Expose metrics endpoint (GET /metrics)
    - Track document processing rate (docs/min)
    - Track latency percentiles (p50, p95, p99) for upload and extraction
    - Track error rate by error type
    - Track review queue depth
    - Track confidence score distributions by document_type
    - _Requirements: 17.1, 17.2, 17.3_

  - [ ]* 13.10 Write property test for metrics exposure
    - **Property 46: Metrics Exposure**
    - **Validates: Requirements 17.1, 17.2, 17.3**

  - [ ] 13.11 Implement structured logging with correlation IDs
    - Use structlog for structured JSON logging
    - Generate correlation ID for each request
    - Include correlation ID in all log entries
    - Propagate correlation ID through async task queue
    - _Requirements: 17.5_

  - [ ]* 13.12 Write property test for structured error logging
    - **Property 48: Structured Error Logging**
    - **Validates: Requirements 17.5**

  - [ ] 13.13 Implement error handling with retry and circuit breaker
    - Add exponential backoff retry for LLM API calls
    - Implement circuit breaker using tenacity library
    - Configure fallback to alternative LLM provider
    - Add graceful degradation for non-critical features
    - _Requirements: 11.2_

  - [ ]* 13.14 Write unit tests for error handling and retries
    - Test exponential backoff timing
    - Test circuit breaker state transitions
    - _Requirements: 11.2_

  - [ ] 13.15 Implement rate limiting and request throttling
    - Add rate limiting middleware using slowapi
    - Configure per-client rate limits
    - Return 429 with Retry-After header when limit exceeded
    - _Requirements: 11.4_

  - [ ]* 13.16 Write unit tests for rate limiting
    - Test rate limit enforcement
    - Test 429 response format
    - _Requirements: 11.4_

  - [ ] 13.17 Implement query extractions endpoint with filtering (GET /v1/extractions)
    - Support query parameters: document_type, status, start_date, end_date
    - Filter extractions matching all specified criteria
    - Support pagination with page and page_size parameters
    - _Requirements: 10.2, 10.5_

  - [ ]* 13.18 Write property test for filtered extraction queries
    - **Property 27: Filtered Extraction Queries**
    - **Validates: Requirements 10.2**

  - [ ]* 13.19 Write property test for pagination correctness
    - **Property 29: Pagination Correctness**
    - **Validates: Requirements 10.5**

  - [ ] 13.20 Implement multi-format export (JSON, CSV, XML)
    - Add export format parameter to extraction retrieval endpoints
    - Implement JSON serializer (default)
    - Implement CSV serializer for flat field structures
    - Implement XML serializer
    - _Requirements: 10.4_

  - [ ]* 13.21 Write property test for multi-format export validity
    - **Property 28: Multi-Format Export Validity**
    - **Validates: Requirements 10.4**

  - [ ] 13.22 Implement configuration reload without restart
    - Watch configuration files for changes
    - Reload extraction schemas when schema files updated
    - Reload validation rules when rule files updated
    - Reload confidence thresholds from config
    - _Requirements: 14.5_

  - [ ]* 13.23 Write property test for configuration reload
    - **Property 38: Configuration Reload Without Restart**
    - **Validates: Requirements 14.5**

  - [ ] 13.24 Implement custom schema and rule loading
    - Support loading extraction schemas from config directory
    - Support loading custom validation rules from Python modules
    - Validate and register custom rules at startup
    - _Requirements: 14.1, 14.2_

  - [ ]* 13.25 Write property test for custom schema loading
    - **Property 34: Custom Schema Loading**
    - **Validates: Requirements 14.1**

  - [ ]* 13.26 Write property test for custom validation rule loading
    - **Property 35: Custom Validation Rule Loading**
    - **Validates: Requirements 14.2**

  - [ ] 13.27 Implement database failover and connection pooling
    - Configure SQLAlchemy connection pool with retry logic
    - Set up read replica support for query endpoints
    - Implement automatic failover to replica on primary failure
    - _Requirements: 9.4, 11.5_

  - [ ]* 13.28 Write integration tests for database failover
    - Test connection retry on transient failures
    - Test failover to replica
    - _Requirements: 11.5_

  - [ ] 13.29 Add performance optimization for high throughput
    - Implement database query optimization with proper indexes
    - Add caching layer using Redis for frequent queries
    - Optimize LLM prompt to reduce token usage
    - Configure worker concurrency for 100 docs/min target
    - _Requirements: 8.2, 12.5_

  - [ ]* 13.30 Write performance tests to verify latency targets
    - Test upload response time <200ms p50
    - Test extraction time <2s p50, <5s p99
    - Test query response time <100ms p50
    - Test throughput ≥100 docs/min
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

  - [ ] 13.31 Implement component failure logging and alerting
    - Create centralized error logging with severity levels
    - Emit alerts to monitoring system for critical failures
    - Include component name, error details, and stack trace
    - _Requirements: 11.2_

  - [ ]* 13.32 Write property test for component failure logging
    - **Property 30: Component Failure Logging**
    - **Validates: Requirements 11.2**

- [ ] 14. Final Checkpoint - Run full test suite and verify completeness
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 15. Integration and Documentation
  - [ ] 15.1 Create end-to-end integration tests
    - Test complete workflow: upload → extraction → validation → scoring → routing
    - Test low confidence review workflow with corrections
    - Test batch processing with mixed results
    - Test error recovery scenarios
    - _Requirements: All_

  - [ ] 15.2 Create Docker Compose setup for local development
    - Add Dockerfile for application
    - Add docker-compose.yml with PostgreSQL, Redis, MinIO services
    - Include environment configuration examples
    - _Requirements: Infrastructure_
