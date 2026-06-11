# FastAPI Application Skeleton

This directory contains the FastAPI application skeleton for the Document Extraction Agent.

## Structure

```
src/api/
├── main.py                      # Main FastAPI application entry point
└── routers/
    ├── __init__.py              # Router package initialization
    ├── health.py                # Health check endpoints
    ├── documents.py             # Document upload and management endpoints
    ├── extractions.py           # Extraction query and management endpoints
    └── batches.py               # Batch processing endpoints
```

## Components

### Main Application (`main.py`)
- **FastAPI app** with title, description, and version
- **CORS middleware** configured for cross-origin requests
- **Global exception handlers** for ValueError and general exceptions
- **Lifespan context manager** for startup/shutdown events
- **Structured error responses** with error codes and timestamps
- **Router inclusion** for all API modules

### Health Router (`routers/health.py`)
- **GET /v1/health** - Health check endpoint
  - Returns service status (healthy/degraded/unhealthy)
  - Includes dependency health checks (database, storage, llm_service)
  - Provides latency metrics for each dependency
  - **Validates: Requirements 17.4**

### Documents Router (`routers/documents.py`)
- **POST /v1/documents/upload** - Upload single document
  - Accepts PDF, JPEG, PNG, TXT formats
  - Maximum file size: 50MB
  - Returns unique document identifier
  - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**

- **GET /v1/documents/{document_id}** - Get document status
  - Returns document metadata and processing status
  - **Validates: Requirements 10.1**

- **POST /v1/documents/batch** - Upload batch of documents
  - Up to 100 documents per batch
  - **Validates: Requirements 1.6, 8.3**

- **GET /v1/documents/{document_id}/extraction** - Get extraction results
  - Returns extracted fields with confidence scores
  - **Validates: Requirements 10.1, 10.3**

### Extractions Router (`routers/extractions.py`)
- **GET /v1/extractions** - Query extractions with filters
  - Filter by document_type, status, needs_review, date range
  - Supports pagination
  - **Validates: Requirements 10.2, 10.5, 7.6**

- **PATCH /v1/extractions/{extraction_id}** - Correct extraction
  - Update extracted fields after human review
  - Creates audit log entries
  - **Validates: Requirements 7.4, 9.2**

- **POST /v1/extractions/{extraction_id}/approve** - Approve extraction
  - Marks extraction as reviewed and verified
  - **Validates: Requirements 7.5**

- **GET /v1/extractions/{extraction_id}/history** - Get extraction history
  - Returns all versions and audit logs
  - **Validates: Requirements 9.5**

### Batches Router (`routers/batches.py`)
- **GET /v1/batches/{batch_id}/status** - Get batch status
  - Returns counts of completed/in-progress/failed documents
  - **Validates: Requirements 8.4**

- **GET /v1/batches/{batch_id}/details** - Get detailed batch status
  - Includes individual document statuses

- **POST /v1/batches/{batch_id}/retry-failed** - Retry failed documents
  - Re-enqueues failed documents for processing
  - **Validates: Requirements 8.5**

## Features Implemented

✅ FastAPI application skeleton with proper structure
✅ CORS middleware configuration
✅ Global exception handlers (ValueError, general exceptions)
✅ Structured error responses with error codes
✅ Lifespan management (startup/shutdown)
✅ Health check endpoint with dependency status (FULLY IMPLEMENTED)
✅ Router structure for all major components:
   - Documents router (4 endpoints)
   - Extractions router (4 endpoints)
   - Batches router (3 endpoints)
   - Health router (1 endpoint)
✅ Pydantic models for request/response validation
✅ Comprehensive docstrings with requirement mappings
✅ TODO comments marking implementation points

## Running the Application

Once dependencies are installed, you can run the application with:

```bash
uvicorn src.api.main:app --reload
```

The API will be available at: http://localhost:8000

API documentation will be auto-generated at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Next Steps

The skeleton is complete with all router structure in place. Future tasks will implement:
1. Database session management and dependency injection
2. Actual endpoint logic for document processing
3. Integration with storage layer (S3/MinIO)
4. Integration with extraction agent and LLM services
5. Authentication and authorization middleware
6. Rate limiting and request throttling
7. Metrics and observability endpoints

## Testing

Unit tests for the health check endpoint are available in `tests/test_api_health.py`.

Run tests with:
```bash
pytest tests/test_api_health.py -v
```
