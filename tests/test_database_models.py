"""Unit tests for database models.

Tests validate the structure, relationships, and basic functionality
of the SQLAlchemy ORM models.
"""

import pytest
from datetime import datetime
from uuid import uuid4

from src.storage.models import (
    Base,
    Batch,
    BatchDocument,
    Document,
    Extraction,
    ExtractionAuditLog,
)


class TestDocumentModel:
    """Tests for the Document model."""

    def test_document_has_required_fields(self):
        """Document model should have all required fields defined."""
        required_fields = {
            "id",
            "created_at"