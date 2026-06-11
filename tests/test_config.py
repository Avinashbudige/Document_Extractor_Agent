"""Test configuration management."""

from src.models.config import Settings


def test_settings_initialization():
    """Test that settings can be initialized with defaults."""
    settings = Settings()
    
    # Verify default values
    assert settings.max_file_size_mb == 50
    assert settings.max_batch_size == 100
    assert settings.ocr_engine == "tesseract"
    assert settings.llm_provider == "openai"


def test_confidence_threshold_retrieval():
    """Test getting confidence thresholds by document type."""
    settings = Settings()
    
    # Test known document types
    assert settings.get_confidence_threshold("invoice") == 0.85
    assert settings.get_confidence_threshold("receipt") == 0.80
    assert settings.get_confidence_threshold("purchase_order") == 0.85
    assert settings.get_confidence_threshold("insurance_policy") == 0.90
    assert settings.get_confidence_threshold("contract") == 0.90
    
    # Test unknown document type returns default
    assert settings.get_confidence_threshold("unknown_type") == 0.85


def test_settings_override_from_env(monkeypatch):
    """Test that environment variables override defaults."""
    # Set environment variables
    monkeypatch.setenv("MAX_FILE_SIZE_MB", "100")
    monkeypatch.setenv("OCR_ENGINE", "easyocr")
    monkeypatch.setenv("CONFIDENCE_THRESHOLD_INVOICE", "0.90")
    
    # Create settings with environment overrides
    settings = Settings()
    
    assert settings.max_file_size_mb == 100
    assert settings.ocr_engine == "easyocr"
    assert settings.confidence_threshold_invoice == 0.90
