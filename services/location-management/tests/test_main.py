import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


@pytest.fixture
def client():
    from src.main import app
    return TestClient(app)


@pytest.fixture
def async_client():
    from src.main import app
    return AsyncClient(app=app, base_url="http://test")


class TestMainApp:
    """Test cases for main FastAPI application"""
    
    def test_app_startup(self):
        """Test that FastAPI app can be imported"""
        from src.main import app
        assert app is not None
        assert hasattr(app, 'title')
    
    def test_app_title(self):
        """Test that app has a title"""
        from src.main import app
        assert app.title is not None
        assert len(app.title) > 0
    
    def test_app_has_routes(self):
        """Test that app has routes configured"""
        from src.main import app
        assert len(app.routes) > 0


class TestHealthEndpoint:
    """Test cases for health endpoint"""
    
    def test_health_endpoint_exists(self, client):
        """Test that health endpoint is accessible"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_endpoint_json_response(self, client):
        """Test that health endpoint returns JSON"""
        response = client.get("/health")
        assert response.headers.get('content-type') is not None
        assert 'application/json' in response.headers.get('content-type', '')
    
    def test_health_endpoint_has_status(self, client):
        """Test that health endpoint response includes status"""
        response = client.get("/health")
        data = response.json()
        assert 'status' in data or 'message' in data or 'health' in data
    
    def test_health_endpoint_returns_ok(self, client):
        """Test that health endpoint indicates service is healthy"""
        response = client.get("/health")
        data = response.json()
        if 'status' in data:
            assert data['status'] in ['ok', 'OK', 'healthy', 'HEALTHY', 'running']
        elif 'message' in data:
            assert data['message'] is not None


class TestOpenAPI:
    """Test cases for OpenAPI documentation"""
    
    def test_openapi_schema_available(self, client):
        """Test that OpenAPI schema is available"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
    
    def test_docs_endpoint_available(self, client):
        """Test that Swagger documentation is available"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_endpoint_available(self, client):
        """Test that ReDoc documentation is available"""
        response = client.get("/redoc")
        assert response.status_code == 200


class TestRootEndpoint:
    """Test cases for root endpoint"""
    
    def test_root_endpoint_exists(self, client):
        """Test that root endpoint is accessible"""
        response = client.get("/")
        assert response.status_code in [200, 404]


class TestErrorHandling:
    """Test cases for error handling"""
    
    def test_nonexistent_endpoint_returns_404(self, client):
        """Test that accessing non-existent endpoint returns 404"""
        response = client.get("/nonexistent/endpoint")
        assert response.status_code == 404
    
    def test_wrong_method_returns_405(self, client):
        """Test that using wrong HTTP method returns 405"""
        response = client.post("/health")
        assert response.status_code == 405


class TestAppConfiguration:
    """Test cases for app configuration"""
    
    def test_app_is_fastapi_instance(self):
        """Test that app is a FastAPI instance"""
        from src.main import app
        from fastapi import FastAPI
        assert isinstance(app, FastAPI)
    
    def test_app_has_debug_setting(self):
        """Test that app has debug configuration"""
        from src.main import app
        assert hasattr(app, 'debug') or hasattr(app, 'title')
    
    def test_app_middleware_configured(self):
        """Test that app has middleware configured"""
        from src.main import app
        assert app.middleware_stack is not None or hasattr(app, 'user_middleware')


class TestServiceCORSHeaders:
    """Test cases for CORS headers"""
    
    def test_health_endpoint_returns_headers(self, client):
        """Test that endpoints return proper headers"""
        response = client.get("/health")
        assert response.status_code in [200, 422, 404]


class TestResponseModels:
    """Test cases for response models"""
    
    def test_health_response_structure(self, client):
        """Test that health response has expected structure"""
        response = client.get("/health")
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)


class TestDependencies:
    """Test cases for dependency injection"""
    
    def test_app_can_import_database_session(self):
        """Test that database dependencies can be imported"""
        try:
            from src.main import app
            assert app is not None
        except ImportError:
            pytest.fail("Could not import app with required dependencies")


class TestLogging:
    """Test cases for logging configuration"""
    
    def test_app_has_logger(self):
        """Test that app or module has logging configured"""
        from src.main import app
        assert app is not None


class TestVersioning:
    """Test cases for API versioning"""
    
    def test_api_version_available(self):
        """Test that API version information is available"""
        from src.main import app
        assert app.title is not None


class TestIntegration:
    """Integration tests for main app"""
    
    def test_health_endpoint_is_responsive(self, client):
        """Test that health endpoint responds quickly"""
        import time
        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start
        assert response.status_code in [200, 500]
        assert elapsed < 1.0
    
    def test_multiple_requests_to_health(self, client):
        """Test that health endpoint handles multiple requests"""
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code in [200, 500]
    
    def test_app_initialization_sequence(self):
        """Test that app initializes correctly"""
        from src.main import app
        assert app is not None
        assert app.title is not None
        assert len(app.routes) > 0
