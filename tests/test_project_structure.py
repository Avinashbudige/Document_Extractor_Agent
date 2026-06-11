"""Test to validate the project structure is correctly initialized."""

import os
from pathlib import Path


def test_root_files_exist():
    """Verify all required root-level files exist."""
    root = Path(".")
    
    required_files = [
        "pyproject.toml",
        "requirements.txt",
        ".env.template",
        ".gitignore",
        "README.md"
    ]
    
    for file in required_files:
        assert (root / file).exists(), f"Missing required file: {file}"


def test_src_directories_exist():
    """Verify all required src subdirectories exist."""
    src = Path("src")
    
    required_dirs = [
        "api",
        "processors",
        "agents",
        "validation",
        "storage",
        "models"
    ]
    
    for directory in required_dirs:
        dir_path = src / directory
        assert dir_path.exists(), f"Missing required directory: src/{directory}"
        assert dir_path.is_dir(), f"src/{directory} is not a directory"
        
        # Verify __init__.py exists in each directory
        init_file = dir_path / "__init__.py"
        assert init_file.exists(), f"Missing __init__.py in src/{directory}"


def test_tests_directory_exists():
    """Verify tests directory exists."""
    tests = Path("tests")
    assert tests.exists(), "Missing tests directory"
    assert tests.is_dir(), "tests is not a directory"
    assert (tests / "__init__.py").exists(), "Missing __init__.py in tests"


def test_pyproject_toml_content():
    """Verify pyproject.toml contains required dependencies."""
    with open("pyproject.toml", "r") as f:
        content = f.read()
    
    required_deps = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "psycopg2",
        "langgraph",
        "langchain",
        "hypothesis",
        "pytest"
    ]
    
    for dep in required_deps:
        assert dep in content, f"Missing required dependency: {dep}"


def test_env_template_content():
    """Verify .env.template contains required configuration variables."""
    with open(".env.template", "r") as f:
        content = f.read()
    
    required_vars = [
        "DATABASE_URL",
        "LLM_API_KEY",
        "S3_BUCKET",
        "OCR_ENGINE",
        "CONFIDENCE_THRESHOLD"
    ]
    
    for var in required_vars:
        assert var in content, f"Missing required environment variable: {var}"


def test_requirements_txt_exists():
    """Verify requirements.txt exists for pip users."""
    assert Path("requirements.txt").exists(), "Missing requirements.txt"
    
    with open("requirements.txt", "r") as f:
        content = f.read()
    
    # Should contain at least the core dependencies
    assert "fastapi" in content
    assert "sqlalchemy" in content
    assert "langgraph" in content
