# Document Extraction Agent

An intelligent document processing system that extracts structured data from business documents including invoices, receipts, purchase orders, insurance policies, and contracts. The system uses AI-powered field extraction with confidence scoring, validation rules, and human-in-the-loop review to ensure high accuracy.

## Features

- **Multi-format Support**: PDF, JPEG, PNG, TXT documents
- **AI-Powered Extraction**: LangGraph-based agent with LLM integration
- **Confidence Scoring**: Field-level confidence scoring for quality assurance
- **Validation Engine**: Configurable business rules for data validation
- **Human Review**: Low-confidence extractions routed to review queue
- **Batch Processing**: Process up to 100 documents per batch
- **REST API**: FastAPI-based API for integration
- **Audit Trail**: Complete history of extractions and modifications
- **High Performance**: Sub-2-second p50 latency, 99.9% uptime

## Architecture

The system follows a pipeline architecture:
1. **Ingestion** → Document upload and validation
2. **Text Extraction** → OCR and PDF parsing
3. **Classification** → Document type detection
4. **Field Extraction** → LLM-based structured data extraction
5. **Validation** → Business rule application
6. **Scoring** → Confidence calculation
7. **Routing** → Auto-approval or human review
8. **Storage** → Persistence and audit trail

## Tech Stack

- **API**: FastAPI, Uvicorn
- **Agents**: LangGraph, LangChain
- **Database**: PostgreSQL with SQLAlchemy
- **Storage**: S3-compatible object storage
- **Testing**: pytest, Hypothesis (property-based testing)
- **Language**: Python 3.10+

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Poetry (Python package manager)
- PostgreSQL 14+
- S3-compatible storage (AWS S3, MinIO, etc.)
- LLM API access (OpenAI, Anthropic, etc.)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd document-extraction-agent
```

2. Install dependencies with Poetry:
```bash
poetry install
```

3. Copy the environment template and configure:
```bash
cp .env.template .env
# Edit .env with your configuration
```

4. Set up the database:
```bash
poetry run alembic upgrade head
```

5. Run the API server:
```bash
poetry run uvicorn src.api.main:app --reload
```

The API will be available at `http://localhost:8000`

### Alternative: pip Installation

If you prefer pip over Poetry:

```bash
pip install -r requirements.txt
```

## Project Structure

```
document-extraction-agent/
├── src/
│   ├── api/           # FastAPI REST API layer
│   ├── processors/    # Document parsing (PDF, OCR)
│   ├── agents/        # LangGraph extraction agents
│   ├── validation/    # Business rule validation
│   ├── storage/       # Database models and operations
│   └── models/        # Shared data models
├── tests/             # Test suite
├── pyproject.toml     # Poetry configuration
├── .env.template      # Environment variable template
└── README.md          # This file
```

## Configuration

All configuration is managed through environment variables. See `.env.template` for available options.

Key configuration areas:
- **Database**: Connection URL, pool size
- **LLM Service**: Provider, API key, model selection
- **Object Storage**: S3 bucket, credentials
- **OCR Engine**: Engine selection (Tesseract/EasyOCR)
- **Processing**: Concurrency, timeouts, file size limits
- **Confidence Thresholds**: Per-document-type thresholds
- **Security**: TLS, encryption, authentication

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

- `POST /v1/documents/upload` - Upload single document
- `POST /v1/documents/batch` - Upload batch of documents
- `GET /v1/documents/{id}` - Get document status
- `GET /v1/documents/{id}/extraction` - Get extraction results
- `GET /v1/extractions` - Query extractions with filters
- `GET /v1/health` - Service health check

## Testing

Run the test suite:

```bash
# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=src --cov-report=html

# Run property-based tests only
poetry run pytest -k property

# Run with verbose output
poetry run pytest -v
```

## Development

### Code Quality

```bash
# Format code with Black
poetry run black src/ tests/

# Lint with flake8
poetry run flake8 src/ tests/

# Type checking with mypy
poetry run mypy src/
```

### Adding New Document Types

1. Create extraction schema in `config/schemas/`
2. Add validation rules in `config/rules/`
3. Configure confidence threshold in `.env`
4. Restart service (or rely on auto-reload if enabled)

## Performance

Target performance metrics:
- **Upload latency**: <200ms (p50)
- **Extraction latency**: <2s (p50), <5s (p99)
- **Query latency**: <100ms (p50)
- **Throughput**: 100+ documents/minute per node
- **Availability**: 99.9% uptime

## Security

- **Encryption at rest**: AES-256 for PII data
- **TLS/HTTPS**: Required for all API traffic
- **Authentication**: Token-based authentication
- **Audit logging**: Complete audit trail of all operations
- **PII redaction**: Configurable PII masking in logs

## License

[Your License Here]

## Contributing

[Contributing guidelines here]

## Support

[Support contact information here]
