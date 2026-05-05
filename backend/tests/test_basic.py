"""
Basic tests for Kenyan Gov Assist backend
Run with: pytest tests/test_basic.py -v
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient

# Mock the problematic imports
sys.modules['sentence_transformers'] = type(sys)('sentence_transformers')
sys.modules['sentence_transformers'].SentenceTransformer = None

from app.main import app
from app.config import settings

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_endpoint(self):
        """Test that health endpoint returns OK."""
        response = client.get("/api/health")
        assert response.status_code == 200
    
    def test_root_endpoint(self):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "services" in data
        assert "supported_languages" in data


class TestTranslationEndpoint:
    """Test translation endpoint."""
    
    def test_translation_missing_text(self):
        """Test translation with missing text."""
        response = client.post(
            "/api/translate",
            json={
                "source_language": "english",
                "target_language": "swahili",
            }
        )
        # Should fail with validation error
        assert response.status_code in [400, 422]
    
    def test_translation_valid_request(self):
        """Test translation with valid request."""
        response = client.post(
            "/api/translate",
            json={
                "text": "Hello, how are you?",
                "source_language": "english",
                "target_language": "swahili",
                "domain": "civic",
            }
        )
        # Should return success or error (if Ollama not running)
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "data" in data or "error" in data


class TestConfig:
    """Test configuration."""
    
    def test_supported_languages(self):
        """Test that supported languages are configured."""
        assert len(settings.SUPPORTED_LANGUAGES) >= 3
        assert "english" in settings.SUPPORTED_LANGUAGES
        assert "swahili" in settings.SUPPORTED_LANGUAGES
    
    def test_model_config(self):
        """Test model configuration."""
        assert settings.OLLAMA_MODEL is not None
        assert len(settings.OLLAMA_MODEL) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
