"""Unit tests for health check endpoint."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health_check_returns_200():
    """Test that health check endpoint returns 200 status code."""
    response = client.get("/v1/health")
    assert response.status_code == 200


def test_health_check_response_structure():
    """Test that health check response has required fields."""
    response = client.get("/v1/health")
    data = response.json()
    
    # Verify top-level fields
    assert "status" in data
    assert "timestamp" in data
    assert "service" in data
    assert "version" in data
    assert "dependencies" in data
    
    # Verify status is valid
    assert data["status"] in ["healthy", "degraded", "unhealthy"]
    
    # Verify service information
    assert data["service"] == "Document Extraction Agent"
    assert data["version"] == "1.0.0"


def test_health_check_dependencies_structure():
    """Test that health check includes dependency health information."""
    response = client.get("/v1/health")
    data = response.json()
    
    dependencies = data["dependencies"]
    
    # Verify expected dependencies are present
    assert "database" in dependencies
    assert "storage" in dependencies
    assert "llm_service" in dependencies
    
    # Verify each dependency has required fields
    for dep_name, dep_info in dependencies.items():
        assert "status" in dep_info
        assert dep_info["status"] in ["healthy", "degraded", "unhealthy"]
        # latency_ms and message are optional but should be present in our implementation
        if "latency_ms" in dep_info:
            assert isinstance(dep_info["latency_ms"], (int, float))
            assert dep_info["latency_ms"] >= 0


def test_health_check_overall_status_healthy_when_all_deps_healthy():
    """Test that overall status is healthy when all dependencies are healthy."""
    response = client.get("/v1/health")
    data = response.json()
    
    # Current implementation returns all dependencies as healthy
    assert data["status"] == "healthy"
    
    # Verify all dependencies are healthy
    for dep_info in data["dependencies"].values():
        assert dep_info["status"] == "healthy"


def test_root_endpoint():
    """Test that root endpoint returns basic API information."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert "status" in data
    assert data["service"] == "Document Extraction Agent"
