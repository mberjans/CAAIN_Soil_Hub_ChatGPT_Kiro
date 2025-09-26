"""
Test Planting Date API Routes

Integration tests for planting date calculation API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import date, datetime
import json
import sys
import os

# Add the services directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'recommendation-engine', 'src'))

from api.planting_date_routes import router
from fastapi import FastAPI

# Create test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)


@pytest.fixture
def sample_location_data():
    """Sample location data for API requests."""
    return {
        "latitude": 42.3601,
        "longitude": -71.0589,
        "elevation_ft": 20,
        "address": "Boston, MA",
        "state": "Massachusetts", 
        "county": "Suffolk",
        "climate_zone": "6a",
        "climate_zone_name": "USDA Zone 6a"
    }


@pytest.fixture
def planting_date_request(sample_location_data):
    """Sample planting date request."""
    return {
        "crop_name": "corn",
        "location": sample_location_data,
        "planting_season": "spring"
    }


@pytest.fixture
def planting_window_request(sample_location_data):
    """Sample planting window request."""
    return {
        "crop_name": "lettuce",
        "location": sample_location_data,
        "succession_planting": True,
        "max_plantings": 3
    }


class TestPlantingDateCalculation:
    """Test planting date calculation endpoints."""
    
    def test_calculate_planting_dates_success(self, planting_date_request):
        """Test successful planting date calculation."""
        
        response = client.post("/api/v1/planting/calculate-dates", json=planting_date_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "crop_name" in data
        assert data["crop_name"] == "corn"
        assert "optimal_date" in data
        assert "earliest_safe_date" in data
        assert "latest_safe_date" in data
        assert "planting_season" in data
        assert data["planting_season"] == "spring"
        
        # Verify date format and logic
        optimal_date = datetime.fromisoformat(data["optimal_date"]).date()
        earliest_date = datetime.fromisoformat(data["earliest_safe_date"]).date()
        latest_date = datetime.fromisoformat(data["latest_safe_date"]).date()
        
        assert earliest_date <= optimal_date <= latest_date
        
        # Verify other fields
        assert isinstance(data["safety_margin_days"], int)
        assert 0.0 <= data["confidence_score"] <= 1.0
        assert isinstance(data["frost_considerations"], list)
        assert isinstance(data["climate_warnings"], list)
    
    def test_calculate_planting_dates_invalid_crop(self, planting_date_request):
        """Test error handling for invalid crop name."""
        
        planting_date_request["crop_name"] = "invalid_crop"
        response = client.post("/api/v1/planting/calculate-dates", json=planting_date_request)
        
        assert response.status_code == 400
        assert "No timing data available" in response.json()["detail"]
    
    def test_calculate_planting_dates_invalid_season(self, planting_date_request):
        """Test error handling for invalid planting season."""
        
        planting_date_request["planting_season"] = "invalid_season"
        response = client.post("/api/v1/planting/calculate-dates", json=planting_date_request)
        
        assert response.status_code == 422  # Validation error
    
    def test_calculate_planting_dates_missing_location(self, planting_date_request):
        """Test error handling for missing location data."""
        
        del planting_date_request["location"]
        response = client.post("/api/v1/planting/calculate-dates", json=planting_date_request)
        
        assert response.status_code == 422  # Validation error
    
    def test_calculate_planting_dates_different_seasons(self, planting_date_request):
        """Test calculation for different seasons."""
        
        # Test spring planting
        planting_date_request["planting_season"] = "spring"
        response = client.post("/api/v1/planting/calculate-dates", json=planting_date_request)
        assert response.status_code == 200
        spring_data = response.json()
        
        # Test fall planting for appropriate crop
        planting_date_request["crop_name"] = "wheat"  # Supports fall planting
        planting_date_request["planting_season"] = "fall"
        response = client.post("/api/v1/planting/calculate-dates", json=planting_date_request)
        assert response.status_code == 200
        fall_data = response.json()
        
        # Fall planting should be later in year than spring
        spring_date = datetime.fromisoformat(spring_data["optimal_date"])
        fall_date = datetime.fromisoformat(fall_data["optimal_date"])
        assert fall_date.month > spring_date.month


class TestFrostDateEndpoint:
    """Test frost date information endpoint."""
    
    def test_get_frost_dates_success(self, sample_location_data):
        """Test successful frost date retrieval."""
        
        request_data = {"location": sample_location_data}
        response = client.post("/api/v1/planting/frost-dates", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "last_frost_date" in data
        assert "first_frost_date" in data
        assert "growing_season_length" in data
        assert "frost_free_days" in data
        assert "confidence_level" in data
        assert "location_summary" in data
        
        # Verify frost date logic if present
        if data["last_frost_date"] and data["first_frost_date"]:
            last_frost = datetime.fromisoformat(data["last_frost_date"]).date()
            first_frost = datetime.fromisoformat(data["first_frost_date"]).date()
            
            # First frost should be after last frost (different years or later in year)
            if last_frost.year == first_frost.year:
                assert first_frost > last_frost
        
        # Verify confidence level
        valid_confidence = ["historical", "estimated", "default"]
        assert data["confidence_level"] in valid_confidence
        
        # Verify location summary includes relevant info
        assert "Zone" in data["location_summary"] or "Boston" in data["location_summary"]
    
    def test_get_frost_dates_minimal_location(self):
        """Test frost date calculation with minimal location data."""
        
        minimal_location = {
            "latitude": 40.0,
            "longitude": -95.0
        }
        request_data = {"location": minimal_location}
        
        response = client.post("/api/v1/planting/frost-dates", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should still provide estimated frost dates
        assert data["confidence_level"] in ["estimated", "default"]
        assert "40.00, -95.00" in data["location_summary"]
    
    def test_get_frost_dates_invalid_coordinates(self):
        """Test error handling for invalid coordinates."""
        
        invalid_location = {
            "latitude": 91.0,  # Invalid latitude
            "longitude": -95.0
        }
        request_data = {"location": invalid_location}
        
        response = client.post("/api/v1/planting/frost-dates", json=request_data)
        
        assert response.status_code == 422  # Validation error


class TestPlantingWindowEndpoint:
    """Test comprehensive planting window endpoint."""
    
    def test_get_planting_window_success(self, planting_window_request):
        """Test successful comprehensive planting window analysis."""
        
        response = client.post("/api/v1/planting/planting-window", json=planting_window_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "crop_name" in data
        assert data["crop_name"] == "lettuce"
        assert "location_summary" in data
        assert "frost_dates" in data
        assert "planting_windows" in data
        assert "recommendations" in data
        assert "warnings" in data
        
        # Verify frost dates section
        frost_data = data["frost_dates"]
        assert "last_frost_date" in frost_data
        assert "confidence_level" in frost_data
        
        # Verify planting windows
        windows = data["planting_windows"]
        assert len(windows) > 0
        
        for window in windows:
            assert "crop_name" in window
            assert "optimal_date" in window
            assert "planting_season" in window
            assert isinstance(window["confidence_score"], (int, float))
        
        # Verify recommendations
        assert isinstance(data["recommendations"], list)
        assert len(data["recommendations"]) > 0
        
        # Check for succession schedule if requested
        if planting_window_request["succession_planting"]:
            assert "succession_schedule" in data
            if data["succession_schedule"]:
                assert len(data["succession_schedule"]) <= planting_window_request["max_plantings"]
    
    def test_get_planting_window_no_succession(self, planting_window_request):
        """Test planting window without succession planting."""
        
        planting_window_request["succession_planting"] = False
        response = client.post("/api/v1/planting/planting-window", json=planting_window_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should not include succession schedule
        assert data.get("succession_schedule") is None
    
    def test_get_planting_window_single_season_crop(self, sample_location_data):
        """Test planting window for crop with limited seasonal options."""
        
        request_data = {
            "crop_name": "corn",  # Typically spring only
            "location": sample_location_data,
            "succession_planting": False
        }
        
        response = client.post("/api/v1/planting/planting-window", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have at least spring planting
        windows = data["planting_windows"]
        seasons = [w["planting_season"] for w in windows]
        assert "spring" in seasons


class TestSuccessionScheduleEndpoint:
    """Test succession planting schedule endpoint."""
    
    def test_get_succession_schedule_success(self, sample_location_data):
        """Test successful succession schedule generation."""
        
        request_data = {
            "crop_name": "lettuce",
            "location": sample_location_data,
            "start_date": "2024-05-01",
            "end_date": "2024-07-01",
            "max_plantings": 4
        }
        
        response = client.post("/api/v1/planting/succession-schedule", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response is list of planting windows
        assert isinstance(data, list)
        assert len(data) <= 4
        
        # Verify each planting window
        for i, window in enumerate(data):
            assert window["crop_name"] == "lettuce"
            assert "optimal_date" in window
            
            # Check succession timing
            if i > 0:
                current_date = datetime.fromisoformat(window["optimal_date"])
                previous_date = datetime.fromisoformat(data[i-1]["optimal_date"])
                days_diff = (current_date - previous_date).days
                assert days_diff > 0  # Should be spaced apart
    
    def test_get_succession_schedule_invalid_dates(self, sample_location_data):
        """Test error handling for invalid date range."""
        
        request_data = {
            "crop_name": "lettuce",
            "location": sample_location_data,
            "start_date": "2024-07-01",
            "end_date": "2024-05-01",  # End before start
            "max_plantings": 3
        }
        
        response = client.post("/api/v1/planting/succession-schedule", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_get_succession_schedule_non_succession_crop(self, sample_location_data):
        """Test error for crop not suitable for succession planting."""
        
        request_data = {
            "crop_name": "wheat",  # Not succession plantable
            "location": sample_location_data,
            "start_date": "2024-05-01",
            "end_date": "2024-07-01",
            "max_plantings": 3
        }
        
        response = client.post("/api/v1/planting/succession-schedule", json=request_data)
        
        assert response.status_code == 400
        assert "not suitable for succession planting" in response.json()["detail"]


class TestAvailableCropsEndpoint:
    """Test available crops information endpoint."""
    
    def test_get_available_crops_success(self):
        """Test successful retrieval of available crops."""
        
        response = client.get("/api/v1/planting/available-crops")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "available_crops" in data
        assert "total_crops" in data
        
        crops = data["available_crops"]
        assert len(crops) > 0
        assert data["total_crops"] == len(crops)
        
        # Verify each crop entry
        for crop in crops:
            assert "crop_name" in crop
            assert "crop_category" in crop
            assert "frost_tolerance" in crop
            assert "days_to_maturity" in crop
            assert "succession_planting" in crop
            assert "fall_planting" in crop
            assert "winter_hardy" in crop
            
            # Verify data types and values
            assert isinstance(crop["crop_name"], str)
            assert crop["crop_category"] in ["cool_season", "warm_season", "heat_sensitive"]
            assert crop["frost_tolerance"] in ["tolerant", "sensitive", "very_sensitive"]
            assert isinstance(crop["days_to_maturity"], int)
            assert crop["days_to_maturity"] > 0
            assert isinstance(crop["succession_planting"], bool)
            assert isinstance(crop["fall_planting"], bool)
            assert isinstance(crop["winter_hardy"], bool)
    
    def test_get_available_crops_includes_expected_crops(self):
        """Test that response includes expected crop types."""
        
        response = client.get("/api/v1/planting/available-crops")
        
        assert response.status_code == 200
        data = response.json()
        
        crop_names = [crop["crop_name"] for crop in data["available_crops"]]
        
        # Should include major crop categories
        expected_crops = ["corn", "soybean", "wheat", "lettuce", "tomato"]
        for expected_crop in expected_crops:
            assert expected_crop in crop_names


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    def test_complete_planting_workflow(self, sample_location_data):
        """Test complete workflow: frost dates -> planting calculation -> succession schedule."""
        
        # Step 1: Get frost dates for location
        frost_request = {"location": sample_location_data}
        frost_response = client.post("/api/v1/planting/frost-dates", json=frost_request)
        assert frost_response.status_code == 200
        frost_data = frost_response.json()
        
        # Step 2: Calculate planting dates for multiple crops
        crops_to_test = ["corn", "lettuce", "wheat"]
        
        for crop in crops_to_test:
            planting_request = {
                "crop_name": crop,
                "location": sample_location_data,
                "planting_season": "spring"
            }
            
            planting_response = client.post("/api/v1/planting/calculate-dates", json=planting_request)
            assert planting_response.status_code == 200
            
            planting_data = planting_response.json()
            assert planting_data["crop_name"] == crop
        
        # Step 3: Get comprehensive analysis for succession crop
        window_request = {
            "crop_name": "lettuce",
            "location": sample_location_data,
            "succession_planting": True,
            "max_plantings": 3
        }
        
        window_response = client.post("/api/v1/planting/planting-window", json=window_request)
        assert window_response.status_code == 200
        window_data = window_response.json()
        
        # Should have multiple planting options
        assert len(window_data["planting_windows"]) > 0
        assert window_data["succession_schedule"] is not None
    
    def test_seasonal_comparison_workflow(self, sample_location_data):
        """Test comparing planting dates across seasons for appropriate crops."""
        
        # Test wheat for both spring and fall planting
        seasons = ["spring", "fall"]
        planting_dates = {}
        
        for season in seasons:
            request_data = {
                "crop_name": "wheat",
                "location": sample_location_data,
                "planting_season": season
            }
            
            response = client.post("/api/v1/planting/calculate-dates", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                planting_dates[season] = datetime.fromisoformat(data["optimal_date"])
        
        # If both seasons available, fall should be later in year than spring
        if "spring" in planting_dates and "fall" in planting_dates:
            assert planting_dates["fall"].month > planting_dates["spring"].month