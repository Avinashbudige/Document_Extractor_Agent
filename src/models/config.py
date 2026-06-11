"""Configuration management for Document Extraction Agent."""

from typing import Dict, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Database Configuration
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/document_extraction",
        description="PostgreSQL connection URL"
    )
    database_pool_size: int = Field(default=20, description="Database connection pool size")
    database_max_overflow: int = Field(default=40, description="Max overflow connections")
    
    # LLM Service Configuration
    llm_provider: str = Field(default="openai", description="LLM provider (openai, anthropic)")
    llm_api_key: str = Field(default="", description="LLM API key")
    llm_model: str = Field(default="gpt-4", description="LLM model name")
    llm_temperature: float = Field(default=0.0, description="LLM temperature")
    llm_max_retries: int = Field(default=3, description="Max LLM API retries")
    llm_timeout_seconds: int = Field(default=30, description="LLM request timeout")
    
    # Object Storage Configuration
    s3_bucket: str = Field(default="document-extraction-storage", description="S3 bucket name")
    s3_endpoint_url: str = Field(
        default="https://s3.amazonaws.com",
        description="S3 endpoint URL"
    )
    s3_access_key_id: str = Field(default="", description="S3 access key")
    s3_secret_access_key: str = Field(default="", description="S3 secret key")
    s3_region: str = Field(default="us-east-1", description="S3 region")
    
    # OCR Engine Configuration
    ocr_engine: str = Field(default="tesseract", description="OCR engine (tesseract, easyocr)")
    ocr_language: str = Field(default="eng", description="OCR language")
    ocr_min_confidence: float = Field(default=0.6, description="Minimum OCR confidence")
    
    # Processing Configuration
    max_file_size_mb: int = Field(default=50, description="Maximum file size in MB")
    max_batch_size: int = Field(default=100, description="Maximum batch size")
    processing_concurrency: int = Field(default=10, description="Processing concurrency")
    processing_timeout_seconds: int = Field(
        default=120,
        description="Processing timeout in seconds"
    )
    
    # Confidence Thresholds
    confidence_threshold_invoice: float = Field(default=0.85)
    confidence_threshold_receipt: float = Field(default=0.80)
    confidence_threshold_purchase_order: float = Field(default=0.85)
    confidence_threshold_insurance_policy: float = Field(default=0.90)
    confidence_threshold_contract: float = Field(default=0.90)
    confidence_threshold_default: float = Field(default=0.85)
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_workers: int = Field(default=4, description="Number of API workers")
    api_cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins"
    )
    api_auth_enabled: bool = Field(default=True, description="Enable API authentication")
    api_auth_token_secret: str = Field(default="", description="JWT secret for auth tokens")
    
    # Review Queue Configuration
    review_queue_max_size: int = Field(default=1000, description="Max review queue size")
    review_queue_alert_threshold: int = Field(
        default=100,
        description="Alert threshold for queue depth"
    )
    
    # Monitoring and Observability
    metrics_enabled: bool = Field(default=True, description="Enable metrics collection")
    metrics_port: int = Field(default=9090, description="Metrics endpoint port")
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json, text)")
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")
    
    # Feature Flags
    enable_pii_encryption: bool = Field(default=True, description="Enable PII encryption")
    enable_pii_redaction: bool = Field(default=True, description="Enable PII redaction in logs")
    enable_custom_schemas: bool = Field(default=True, description="Enable custom schemas")
    enable_custom_validation_rules: bool = Field(
        default=True,
        description="Enable custom validation rules"
    )
    enable_auto_config_reload: bool = Field(
        default=True,
        description="Enable automatic config reload"
    )
    
    # Performance Tuning
    extraction_latency_target_ms: int = Field(default=2000, description="Target extraction latency")
    upload_latency_target_ms: int = Field(default=200, description="Target upload latency")
    query_latency_target_ms: int = Field(default=100, description="Target query latency")
    min_throughput_per_node: int = Field(
        default=100,
        description="Minimum throughput per node (docs/min)"
    )
    
    # Security Configuration
    tls_enabled: bool = Field(default=False, description="Enable TLS")
    tls_cert_file: Optional[str] = Field(default=None, description="TLS certificate file")
    tls_key_file: Optional[str] = Field(default=None, description="TLS key file")
    encryption_key: str = Field(default="", description="Encryption key for PII")
    encryption_algorithm: str = Field(default="AES-256-GCM", description="Encryption algorithm")
    
    # Data Retention
    document_retention_days: int = Field(default=2555, description="Document retention (7 years)")
    audit_log_retention_days: int = Field(default=2555, description="Audit log retention")
    
    def get_confidence_threshold(self, document_type: str) -> float:
        """Get confidence threshold for a specific document type.
        
        Args:
            document_type: The document type (e.g., 'invoice', 'receipt')
            
        Returns:
            Confidence threshold value (0.0-1.0)
        """
        threshold_map: Dict[str, float] = {
            "invoice": self.confidence_threshold_invoice,
            "receipt": self.confidence_threshold_receipt,
            "purchase_order": self.confidence_threshold_purchase_order,
            "insurance_policy": self.confidence_threshold_insurance_policy,
            "contract": self.confidence_threshold_contract,
        }
        return threshold_map.get(document_type, self.confidence_threshold_default)


# Global settings instance
settings = Settings()
