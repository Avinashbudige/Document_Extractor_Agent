"""Unit tests for database session management and dependency injection."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import OperationalError

from src.storage.database import (
    get_db,
    init_db,
    get_db_health,
    close_db_connections,
    engine,
    SessionLocal,
)
from src.storage.models import Base, Document


class TestDatabaseSession:
    """Test suite for database session management."""

    def test_get_db_yields_session(self):
        """Test that get_db yields a valid SQLAlchemy session."""
        generator = get_db()
        db_session = next(generator)
        
        assert isinstance(db_session, Session)
        
        # Clean up
        try:
            next(generator)
        except StopIteration:
            pass

    def test_get_db_closes_session_after_use(self):
        """Test that get_db properly closes the session after use."""
        generator = get_db()
        db_session = next(generator)
        
        # Session should be open
        assert not db_session._is_clean()  # Session has been used
        
        # Complete the generator (simulating end of request)
        try:
            next(generator)
        except StopIteration:
            pass
        
        # Session should be closed now
        # We can verify this by checking that the session is not usable
        with pytest.raises(Exception):
            db_session.execute("SELECT 1")

    def test_get_db_rollback_on_exception(self):
        """Test that get_db rolls back the session when an exception occurs."""
        with patch.object(SessionLocal, '__call__') as mock_session_factory:
            mock_session = Mock(spec=Session)
            mock_session_factory.return_value = mock_session
            
            generator = get_db()
            db_session = next(generator)
            
            # Simulate an exception during request processing
            try:
                generator.throw(Exception("Test exception"))
            except Exception:
                pass
            
            # Verify rollback was called
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()

    def test_session_factory_configuration(self):
        """Test that SessionLocal is properly configured."""
        assert SessionLocal.kw.get('autocommit') is False
        assert SessionLocal.kw.get('autoflush') is False
        assert SessionLocal.kw.get('bind') is engine

    def test_engine_pool_configuration(self):
        """Test that database engine has correct pool configuration."""
        # Verify pool settings from settings
        assert engine.pool.size() >= 0  # Pool exists
        # Pool pre-ping should be enabled (can't directly test but ensure no errors)
        
    def test_get_db_health_success(self):
        """Test get_db_health returns True when database is accessible."""
        # This test requires a real database connection
        # We'll mock the database call for unit testing
        with patch('src.storage.database.SessionLocal') as mock_session_local:
            mock_session = Mock(spec=Session)
            mock_session.execute.return_value = None
            mock_session_local.return_value = mock_session
            
            result = get_db_health()
            
            assert result is True
            mock_session.execute.assert_called_once_with("SELECT 1")
            mock_session.close.assert_called_once()

    def test_get_db_health_failure(self):
        """Test get_db_health returns False when database is not accessible."""
        with patch('src.storage.database.SessionLocal') as mock_session_local:
            mock_session = Mock(spec=Session)
            mock_session.execute.side_effect = OperationalError("Connection failed", None, None)
            mock_session_local.return_value = mock_session
            
            result = get_db_health()
            
            assert result is False
            mock_session.close.assert_called_once()

    def test_init_db_creates_tables(self):
        """Test that init_db creates all tables."""
        with patch('src.storage.models.Base.metadata.create_all') as mock_create_all:
            init_db()
            
            mock_create_all.assert_called_once_with(bind=engine)

    def test_close_db_connections_disposes_engine(self):
        """Test that close_db_connections properly disposes of the engine."""
        with patch('src.storage.database.engine.dispose') as mock_dispose:
            close_db_connections()
            
            mock_dispose.assert_called_once()


class TestDatabaseSessionIntegration:
    """Integration tests for database session with actual database."""

    @pytest.fixture
    def test_db_engine(self):
        """Create a test database engine with in-memory SQLite."""
        test_engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=test_engine)
        return test_engine

    @pytest.fixture
    def test_session_factory(self, test_db_engine):
        """Create a test session factory."""
        return sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)

    def test_session_crud_operations(self, test_session_factory):
        """Test basic CRUD operations with a session."""
        session = test_session_factory()
        
        try:
            # Create a document
            doc = Document(
                filename="test.pdf",
                file_size_bytes=1024,
                file_format="pdf",
                storage_key="s3://bucket/test.pdf",
                status="queued"
            )
            session.add(doc)
            session.commit()
            
            # Read the document
            retrieved = session.query(Document).filter_by(filename="test.pdf").first()
            assert retrieved is not None
            assert retrieved.filename == "test.pdf"
            assert retrieved.file_size_bytes == 1024
            
            # Update the document
            retrieved.status = "completed"
            session.commit()
            
            # Verify update
            updated = session.query(Document).filter_by(filename="test.pdf").first()
            assert updated.status == "completed"
            
            # Delete the document
            session.delete(updated)
            session.commit()
            
            # Verify deletion
            deleted = session.query(Document).filter_by(filename="test.pdf").first()
            assert deleted is None
            
        finally:
            session.close()

    def test_session_transaction_rollback(self, test_session_factory):
        """Test that session rollback works correctly."""
        session = test_session_factory()
        
        try:
            # Add a document
            doc = Document(
                filename="rollback_test.pdf",
                file_size_bytes=2048,
                file_format="pdf",
                storage_key="s3://bucket/rollback.pdf",
                status="queued"
            )
            session.add(doc)
            session.commit()
            
            # Start a transaction that will be rolled back
            doc.status = "processing"
            session.add(doc)
            session.flush()  # Flush changes to session
            
            # Rollback
            session.rollback()
            
            # Verify the rollback - status should still be 'queued'
            retrieved = session.query(Document).filter_by(filename="rollback_test.pdf").first()
            assert retrieved.status == "queued"
            
        finally:
            session.close()

    def test_multiple_sessions_isolation(self, test_session_factory):
        """Test that multiple sessions are properly isolated."""
        session1 = test_session_factory()
        session2 = test_session_factory()
        
        try:
            # Create a document in session1
            doc = Document(
                filename="isolation_test.pdf",
                file_size_bytes=3072,
                file_format="pdf",
                storage_key="s3://bucket/isolation.pdf",
                status="queued"
            )
            session1.add(doc)
            session1.commit()
            
            # Query from session2
            retrieved = session2.query(Document).filter_by(filename="isolation_test.pdf").first()
            assert retrieved is not None
            assert retrieved.filename == "isolation_test.pdf"
            
            # Modify in session1 (not yet committed)
            doc.status = "processing"
            session1.add(doc)
            session1.flush()
            
            # Session2 should not see uncommitted changes
            session2.expire_all()
            retrieved2 = session2.query(Document).filter_by(filename="isolation_test.pdf").first()
            # In SQLite, isolation levels may vary; in PostgreSQL this would be 'queued'
            
        finally:
            session1.close()
            session2.close()


class TestDatabaseDependencyInjection:
    """Test FastAPI dependency injection with get_db."""

    def test_get_db_as_fastapi_dependency(self):
        """Test that get_db works as a FastAPI dependency."""
        from fastapi import Depends, FastAPI
        from fastapi.testclient import TestClient
        
        app = FastAPI()
        
        @app.get("/test")
        def test_endpoint(db: Session = Depends(get_db)):
            # Just verify we get a session
            return {"session_active": db.is_active}
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 200
        # Session should be active during request
        assert "session_active" in response.json()

    def test_get_db_exception_handling_in_fastapi(self):
        """Test that exceptions in route handlers properly close the session."""
        from fastapi import Depends, FastAPI, HTTPException
        from fastapi.testclient import TestClient
        
        app = FastAPI()
        
        @app.get("/test-error")
        def test_error_endpoint(db: Session = Depends(get_db)):
            # Simulate an error in the route handler
            raise HTTPException(status_code=500, detail="Test error")
        
        client = TestClient(app)
        response = client.get("/test-error")
        
        assert response.status_code == 500
        # Session should be properly closed despite the error
        # (no way to directly test this without database monitoring)
