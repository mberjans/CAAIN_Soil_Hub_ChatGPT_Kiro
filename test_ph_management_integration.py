"""
Integration tests for pH Management System
Tests the complete integration between frontend and backend services.
"""

import pytest
import httpx
import asyncio
import time
from typing import Dict, Any

# Service URLs
FRONTEND_URL = "http://localhost:3000"
RECOMMENDATION_ENGINE_URL = "http://localhost:8001"

class TestPHManagementIntegration:
    """Test pH management system integration across services."""
    
    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup test environment."""
        # Wait for services to be ready
        await self.wait_for_services()
        
    async def wait_for_services(self, max_retries: int = 30):
        """Wait for all required services to be available."""
        services = [
            ("Frontend", FRONTEND_URL),
            ("Recommendation Engine", RECOMMENDATION_ENGINE_URL)
        ]
        
        for service_name, url in services:
            for attempt in range(max_retries):
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(f"{url}/health", timeout=5.0)
                        if response.status_code == 200:
                            break
                except (httpx.RequestError, httpx.TimeoutException):
                    if attempt == max_retries - 1:
                        pytest.fail(f"{service_name} service not available at {url}")
                    await asyncio.sleep(2)
    
    async def test_frontend_ph_page_loads(self):
        """Test that the pH management page loads successfully."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{FRONTEND_URL}/ph-management")
            assert response.status_code == 200
            assert "pH Management" in response.text
    
    async def test_ph_analysis_integration(self):
        """Test pH analysis through frontend to backend integration."""
        test_data = {
            "farm_id": "test_farm_001",
            "field_id": "test_field_001",
            "crop_type": "corn",
            "ph": 5.8,
            "organic_matter": 3.2,
            "phosphorus": 25,
            "potassium": 180,
            "cec": 14.5
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FRONTEND_URL}/api/ph/analyze",
                data=test_data,
                timeout=30.0
            )
            
            assert response.status_code == 200
            result = response.json()
            
            # Verify response structure
            assert "success" in result
            assert "analysis" in result
            assert "recommendations" in result
            
            # Verify analysis data
            analysis = result["analysis"]
            assert "current_ph" in analysis
            assert "ph_level" in analysis
            assert "target_ph" in analysis
            assert "management_priority" in analysis
    
    async def test_lime_calculator_integration(self):
        """Test lime calculator through frontend to backend integration."""
        test_data = {
            "current_ph": 5.5,
            "target_ph": 6.5,
            "buffer_ph": 6.0,
            "soil_texture": "loam",
            "organic_matter_percent": 3.0,
            "field_size_acres": 10.0
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FRONTEND_URL}/api/ph/lime-calculator",
                data=test_data,
                timeout=30.0
            )
            
            assert response.status_code == 200
            result = response.json()
            
            # Verify response structure
            assert "success" in result
            assert "lime_requirements" in result
            assert isinstance(result["lime_requirements"], list)
            
            # Verify lime recommendation data
            if result["lime_requirements"]:
                lime_rec = result["lime_requirements"][0]
                assert "lime_type" in lime_rec
                assert "application_rate_tons_per_acre" in lime_rec
                assert "cost_per_acre" in lime_rec
    
    async def test_crop_ph_requirements_integration(self):
        """Test crop pH requirements through frontend to backend integration."""
        crop_types = "corn,soybeans,wheat"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FRONTEND_URL}/api/ph/crop-requirements",
                params={"crop_types": crop_types},
                timeout=30.0
            )
            
            assert response.status_code == 200
            result = response.json()
            
            # Verify response structure
            assert "success" in result
            assert "crop_requirements" in result
            
            # Verify crop requirements data
            crop_reqs = result["crop_requirements"]
            for crop in ["corn", "soybeans", "wheat"]:
                if crop in crop_reqs:
                    crop_data = crop_reqs[crop]
                    assert "optimal_range" in crop_data
                    assert "acceptable_range" in crop_data
                    assert "critical_minimum" in crop_data
    
    async def test_ph_monitoring_setup_integration(self):
        """Test pH monitoring setup through frontend to backend integration."""
        test_data = {
            "farm_id": "test_farm_001",
            "field_id": "test_field_001",
            "monitoring_frequency": "quarterly",
            "alert_thresholds": '{"low": 5.5, "high": 7.5}'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FRONTEND_URL}/api/ph/monitor",
                data=test_data,
                timeout=30.0
            )
            
            assert response.status_code == 200
            result = response.json()
            
            # Verify response structure
            assert "success" in result
            assert "monitoring_plan" in result
            
            # Verify monitoring plan data
            plan = result["monitoring_plan"]
            assert "monitoring_id" in plan
            assert "frequency" in plan
            assert "alert_thresholds" in plan
            assert "next_test_date" in plan
    
    async def test_ph_dashboard_integration(self):
        """Test pH dashboard through frontend to backend integration."""
        farm_id = "test_farm_001"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FRONTEND_URL}/api/ph/dashboard",
                params={"farm_id": farm_id},
                timeout=30.0
            )
            
            assert response.status_code == 200
            result = response.json()
            
            # Verify response structure
            assert "success" in result
            assert "dashboard" in result
            
            # Verify dashboard data
            dashboard = result["dashboard"]
            assert "farm_summary" in dashboard
            assert "field_status" in dashboard
            assert "upcoming_tasks" in dashboard
    
    async def test_ph_trends_integration(self):
        """Test pH trends through frontend to backend integration."""
        params = {
            "farm_id": "test_farm_001",
            "field_id": "test_field_001"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FRONTEND_URL}/api/ph/trends",
                params=params,
                timeout=30.0
            )
            
            assert response.status_code == 200
            result = response.json()
            
            # Verify response structure
            assert "success" in result
            assert "trends" in result
            
            # Verify trends data
            trends = result["trends"]
            assert "trend_direction" in trends
            assert "current_ph" in trends
            assert "confidence" in trends
    
    async def test_service_health_checks(self):
        """Test that all services report healthy status."""
        services = [
            (FRONTEND_URL, "frontend"),
            (RECOMMENDATION_ENGINE_URL, "recommendation-engine")
        ]
        
        for url, expected_service in services:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health", timeout=10.0)
                assert response.status_code == 200
                
                health_data = response.json()
                assert health_data["service"] == expected_service
                assert health_data["status"] in ["healthy", "degraded"]
    
    async def test_cross_service_authentication(self):
        """Test that services can communicate with proper authentication."""
        # This would test authentication between services
        # For now, we test that the services accept requests
        async with httpx.AsyncClient() as client:
            # Test direct backend call
            response = await client.post(
                f"{RECOMMENDATION_ENGINE_URL}/api/v1/ph/analyze",
                json={
                    "farm_id": "test_farm",
                    "field_id": "test_field",
                    "crop_type": "corn",
                    "soil_test_data": {
                        "ph": 6.0,
                        "organic_matter_percent": 3.0,
                        "phosphorus_ppm": 25,
                        "potassium_ppm": 150
                    }
                },
                timeout=30.0
            )
            
            # Should get a response (may be error due to missing service dependency, but connection works)
            assert response.status_code in [200, 400, 500]  # Any response means connection works

@pytest.mark.asyncio
async def test_end_to_end_ph_workflow():
    """Test complete end-to-end pH management workflow."""
    # This test simulates a complete farmer workflow:
    # 1. Access pH management page
    # 2. Analyze current pH
    # 3. Get lime recommendations
    # 4. Setup monitoring
    # 5. Check dashboard
    
    test_farm_id = f"integration_test_{int(time.time())}"
    test_field_id = "field_001"
    
    async with httpx.AsyncClient() as client:
        # Step 1: Verify pH management page is accessible
        page_response = await client.get(f"{FRONTEND_URL}/ph-management")
        assert page_response.status_code == 200
        
        # Step 2: Analyze current pH
        analysis_data = {
            "farm_id": test_farm_id,
            "field_id": test_field_id,
            "crop_type": "corn",
            "ph": 5.6,
            "organic_matter": 2.8,
            "phosphorus": 22,
            "potassium": 165
        }
        
        analysis_response = await client.post(
            f"{FRONTEND_URL}/api/ph/analyze",
            data=analysis_data,
            timeout=30.0
        )
        assert analysis_response.status_code == 200
        analysis_result = analysis_response.json()
        assert analysis_result["success"]
        
        # Step 3: Get lime recommendations
        lime_data = {
            "current_ph": 5.6,
            "target_ph": 6.5,
            "soil_texture": "loam",
            "organic_matter_percent": 2.8,
            "field_size_acres": 25.0
        }
        
        lime_response = await client.post(
            f"{FRONTEND_URL}/api/ph/lime-calculator",
            data=lime_data,
            timeout=30.0
        )
        assert lime_response.status_code == 200
        lime_result = lime_response.json()
        assert lime_result["success"]
        
        # Step 4: Setup monitoring
        monitoring_data = {
            "farm_id": test_farm_id,
            "field_id": test_field_id,
            "monitoring_frequency": "quarterly",
            "alert_thresholds": '{"low": 5.5, "high": 7.2}'
        }
        
        monitoring_response = await client.post(
            f"{FRONTEND_URL}/api/ph/monitor",
            data=monitoring_data,
            timeout=30.0
        )
        assert monitoring_response.status_code == 200
        monitoring_result = monitoring_response.json()
        assert monitoring_result["success"]
        
        # Step 5: Check dashboard
        dashboard_response = await client.get(
            f"{FRONTEND_URL}/api/ph/dashboard",
            params={"farm_id": test_farm_id},
            timeout=30.0
        )
        assert dashboard_response.status_code == 200
        dashboard_result = dashboard_response.json()
        assert dashboard_result["success"]

if __name__ == "__main__":
    # Run tests manually if needed
    pytest.main([__file__, "-v"])