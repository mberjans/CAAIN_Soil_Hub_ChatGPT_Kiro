"""
CAAIN Soil Hub Integration Service for Fertilizer Application Method Service

Comprehensive integration service for connecting the fertilizer-application service
with all other CAAIN Soil Hub services, ensuring seamless data flow,
API compatibility, and cross-service functionality.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import json
import sys
from pathlib import Path

# Add shared utilities to path
shared_utils_path = Path(__file__).parent.parent.parent.parent.parent / "shared" / "utils"
sys.path.insert(0, str(shared_utils_path))

try:
    from service_client import ServiceClient, ServiceRegistry, ServiceClientError
except ImportError:
    # Fallback if shared utilities not available
    import aiohttp
    from typing import Dict, Any, Optional
    
    class ServiceClientError(Exception):
        """Base exception for service client errors."""
        pass
    
    class ServiceClient:
        """Basic HTTP client for service communication."""
        def __init__(self, base_url: str, service_name: str):
            self.base_url = base_url.rstrip('/')
            self.service_name = service_name
            self._session: Optional[aiohttp.ClientSession] = None
        
        async def __aenter__(self):
            if self._session is None or self._session.closed:
                timeout = aiohttp.ClientTimeout(total=30)
                self._session = aiohttp.ClientSession(timeout=timeout)
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            if self._session and not self._session.closed:
                await self._session.close()
        
        async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            async with self._session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise ServiceClientError(f"HTTP {response.status}: {await response.text()}")
        
        async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            async with self._session.post(url, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise ServiceClientError(f"HTTP {response.status}: {await response.text()}")
        
        async def health_check(self) -> bool:
            try:
                response = await self.get('/health')
                return response.get('status') in ['healthy', 'ok']
            except:
                return False

logger = logging.getLogger(__name__)


class CAAINFertilizerIntegrationService:
    """
    Comprehensive integration service for CAAIN Soil Hub fertilizer application services.
    
    Features:
    - Service discovery and health monitoring
    - Cross-service data synchronization
    - API compatibility management
    - Data consistency validation
    - Error handling and fallback mechanisms
    - Performance monitoring and optimization
    - Fertilizer-specific integration workflows
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize the CAAIN fertilizer integration service."""
        self.database_url = database_url
        self.service_clients: Dict[str, ServiceClient] = {}
        self.service_status: Dict[str, Dict[str, Any]] = {}
        self.integration_config = self._load_integration_config()
        self.data_sync_cache: Dict[str, Any] = {}
        self.last_sync_times: Dict[str, datetime] = {}
        
        # Initialize service clients
        self._initialize_service_clients()
        
        logger.info("CAAIN Fertilizer Integration Service initialized")
    
    def _load_integration_config(self) -> Dict[str, Dict[str, Any]]:
        """Load integration configuration for all CAAIN services."""
        return {
            "recommendation-engine": {
                "base_url": "http://localhost:8001",
                "endpoints": {
                    "health": "/health",
                    "crop_recommendations": "/api/v1/recommendations/crop-varieties",
                    "soil_analysis": "/api/v1/soil/analyze",
                    "fertilizer_recommendations": "/api/v1/fertilizer/recommendations",
                    "ph_management": "/api/v1/ph/analyze",
                    "nutrient_analysis": "/api/v1/nutrients/analyze"
                },
                "timeout": 30,
                "retry_attempts": 3,
                "critical": True
            },
            "data-integration": {
                "base_url": "http://localhost:8003",
                "endpoints": {
                    "health": "/health",
                    "soil_data": "/api/v1/soil/characteristics",
                    "climate_data": "/api/v1/climate-zones/by-coordinates",
                    "weather_data": "/api/v1/weather/current",
                    "market_data": "/api/v1/market/prices",
                    "fertilizer_prices": "/api/v1/market/fertilizer-prices"
                },
                "timeout": 30,
                "retry_attempts": 3,
                "critical": True
            },
            "ai-agent": {
                "base_url": "http://localhost:8002",
                "endpoints": {
                    "health": "/health",
                    "explain_recommendation": "/api/v1/ai/explain",
                    "context_management": "/api/v1/context/manage",
                    "conversation": "/api/v1/conversation",
                    "fertilizer_explanation": "/api/v1/ai/fertilizer/explain"
                },
                "timeout": 45,
                "retry_attempts": 2,
                "critical": False
            },
            "question-router": {
                "base_url": "http://localhost:8000",
                "endpoints": {
                    "health": "/health",
                    "route_question": "/api/v1/questions/route",
                    "intent_classification": "/api/v1/questions/classify",
                    "fertilizer_questions": "/api/v1/questions/fertilizer"
                },
                "timeout": 20,
                "retry_attempts": 3,
                "critical": True
            },
            "user-management": {
                "base_url": "http://localhost:8005",
                "endpoints": {
                    "health": "/health",
                    "user_profile": "/api/v1/users/profile",
                    "farm_data": "/api/v1/farms",
                    "field_data": "/api/v1/fields"
                },
                "timeout": 25,
                "retry_attempts": 2,
                "critical": False
            },
            "image-analysis": {
                "base_url": "http://localhost:8004",
                "endpoints": {
                    "health": "/health",
                    "crop_analysis": "/api/v1/image/crop-analysis",
                    "deficiency_detection": "/api/v1/image/deficiency-detection"
                },
                "timeout": 60,
                "retry_attempts": 2,
                "critical": False
            }
        }
    
    def _initialize_service_clients(self):
        """Initialize service clients for all CAAIN services."""
        for service_name, config in self.integration_config.items():
            try:
                client = ServiceClient(config["base_url"], service_name)
                self.service_clients[service_name] = client
                self.service_status[service_name] = {
                    "status": "unknown",
                    "last_check": None,
                    "response_time": None,
                    "error_count": 0,
                    "critical": config.get("critical", False)
                }
                logger.info(f"Initialized client for {service_name} at {config['base_url']}")
            except Exception as e:
                logger.error(f"Failed to initialize client for {service_name}: {e}")
                self.service_status[service_name] = {
                    "status": "error",
                    "last_check": datetime.utcnow(),
                    "response_time": None,
                    "error_count": 1,
                    "critical": config.get("critical", False),
                    "error": str(e)
                }
    
    async def check_service_health(self, service_name: str) -> Dict[str, Any]:
        """Check health status of a specific service."""
        if service_name not in self.service_clients:
            return {"status": "not_found", "error": f"Service {service_name} not configured"}
        
        # Initialize service status if not exists
        if service_name not in self.service_status:
            self.service_status[service_name] = {
                "status": "unknown",
                "last_check": None,
                "response_time": None,
                "error_count": 0,
                "critical": False
            }
        
        start_time = datetime.utcnow()
        try:
            async with self.service_clients[service_name] as client:
                is_healthy = await client.health_check()
                response_time = (datetime.utcnow() - start_time).total_seconds()
                
                self.service_status[service_name].update({
                    "status": "healthy" if is_healthy else "unhealthy",
                    "last_check": datetime.utcnow(),
                    "response_time": response_time,
                    "error_count": 0
                })
                
                return {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "response_time": response_time,
                    "last_check": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            error_count = self.service_status[service_name].get("error_count", 0) + 1
            self.service_status[service_name].update({
                "status": "error",
                "last_check": datetime.utcnow(),
                "response_time": None,
                "error_count": error_count,
                "error": str(e)
            })
            
            logger.error(f"Health check failed for {service_name}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "error_count": error_count
            }
    
    async def check_all_services_health(self) -> Dict[str, Dict[str, Any]]:
        """Check health status of all CAAIN services."""
        tasks = []
        for service_name in self.service_clients.keys():
            tasks.append(self.check_service_health(service_name))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        health_report = {}
        for i, service_name in enumerate(self.service_clients.keys()):
            if isinstance(results[i], Exception):
                health_report[service_name] = {
                    "status": "error",
                    "error": str(results[i])
                }
            else:
                health_report[service_name] = results[i]
        
        return health_report
    
    async def get_soil_data(self, field_id: str, user_id: str) -> Dict[str, Any]:
        """Get soil data from data-integration service."""
        try:
            async with self.service_clients["data-integration"] as client:
                response = await client.get(
                    "/api/v1/soil/characteristics",
                    params={"field_id": field_id, "user_id": user_id}
                )
                return response
        except Exception as e:
            logger.error(f"Failed to get soil data: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def get_crop_recommendations(self, location_data: Dict[str, Any], soil_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get crop recommendations from recommendation-engine service."""
        try:
            async with self.service_clients["recommendation-engine"] as client:
                response = await client.post(
                    "/api/v1/recommendations/crop-varieties",
                    data={
                        "location": location_data,
                        "soil_data": soil_data
                    }
                )
                return response
        except Exception as e:
            logger.error(f"Failed to get crop recommendations: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def get_fertilizer_prices(self, fertilizer_types: List[str], region: str = None) -> Dict[str, Any]:
        """Get current fertilizer prices from data-integration service."""
        try:
            async with self.service_clients["data-integration"] as client:
                params = {"fertilizer_types": fertilizer_types}
                if region:
                    params["region"] = region
                
                response = await client.get(
                    "/api/v1/market/fertilizer-prices",
                    params=params
                )
                return response
        except Exception as e:
            logger.error(f"Failed to get fertilizer prices: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def get_weather_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get current weather data from data-integration service."""
        try:
            async with self.service_clients["data-integration"] as client:
                response = await client.get(
                    "/api/v1/weather/current",
                    params={"latitude": latitude, "longitude": longitude}
                )
                return response
        except Exception as e:
            logger.error(f"Failed to get weather data: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def explain_fertilizer_recommendation(self, recommendation_data: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI explanation for fertilizer recommendation."""
        try:
            async with self.service_clients["ai-agent"] as client:
                response = await client.post(
                    "/api/v1/ai/fertilizer/explain",
                    data={
                        "recommendation": recommendation_data,
                        "context": user_context
                    }
                )
                return response
        except Exception as e:
            logger.error(f"Failed to get AI explanation: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def sync_fertilizer_data(self, field_id: str, user_id: str) -> Dict[str, Any]:
        """Synchronize fertilizer application data across services."""
        sync_key = f"fertilizer_sync_{field_id}_{user_id}"
        
        # Check if sync is needed
        if sync_key in self.data_sync_cache:
            last_sync = self.last_sync_times.get(sync_key)
            if last_sync and (datetime.utcnow() - last_sync).total_seconds() < 300:  # 5 minutes
                return self.data_sync_cache[sync_key]
        
        try:
            # Gather data from multiple services
            soil_data = await self.get_soil_data(field_id, user_id)
            weather_data = await self.get_weather_data(40.0, -95.0)  # Default coordinates
            
            sync_data = {
                "field_id": field_id,
                "user_id": user_id,
                "soil_data": soil_data,
                "weather_data": weather_data,
                "sync_timestamp": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
            # Cache the result
            self.data_sync_cache[sync_key] = sync_data
            self.last_sync_times[sync_key] = datetime.utcnow()
            
            return sync_data
            
        except Exception as e:
            logger.error(f"Failed to sync fertilizer data: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def validate_fertilizer_recommendation(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Validate fertilizer recommendation against multiple data sources."""
        validation_results = {
            "recommendation_id": recommendation.get("id"),
            "validations": {},
            "overall_status": "valid",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Validate against soil data
            if "field_id" in recommendation:
                soil_data = await self.get_soil_data(
                    recommendation["field_id"], 
                    recommendation.get("user_id", "")
                )
                validation_results["validations"]["soil_data"] = {
                    "status": "valid" if "error" not in soil_data else "invalid",
                    "data": soil_data
                }
            
            # Validate against weather data
            if "location" in recommendation:
                location = recommendation["location"]
                weather_data = await self.get_weather_data(
                    location.get("latitude", 40.0),
                    location.get("longitude", -95.0)
                )
                validation_results["validations"]["weather_data"] = {
                    "status": "valid" if "error" not in weather_data else "invalid",
                    "data": weather_data
                }
            
            # Check overall validation status
            invalid_count = sum(1 for v in validation_results["validations"].values() 
                              if v["status"] == "invalid")
            if invalid_count > 0:
                validation_results["overall_status"] = "invalid"
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Failed to validate recommendation: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_service_status_summary(self) -> Dict[str, Any]:
        """Get summary of all service statuses."""
        healthy_count = sum(1 for status in self.service_status.values() 
                           if status["status"] == "healthy")
        total_count = len(self.service_status)
        critical_services_down = [
            name for name, status in self.service_status.items()
            if status.get("critical", False) and status["status"] != "healthy"
        ]
        
        return {
            "total_services": total_count,
            "healthy_services": healthy_count,
            "unhealthy_services": total_count - healthy_count,
            "critical_services_down": critical_services_down,
            "overall_status": "healthy" if len(critical_services_down) == 0 else "degraded",
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def cleanup(self):
        """Cleanup resources and close connections."""
        for client in self.service_clients.values():
            try:
                if hasattr(client, '_session') and client._session:
                    await client._session.close()
            except Exception as e:
                logger.warning(f"Error closing client session: {e}")
        
        logger.info("CAAIN Fertilizer Integration Service cleanup completed")