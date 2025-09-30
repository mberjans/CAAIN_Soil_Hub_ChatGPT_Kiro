"""
CAAIN Soil Hub Integration Service for Drought Management

Comprehensive integration service for connecting the drought-management service
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

logger = logging.getLogger(__name__)


class CAAINDroughtIntegrationService:
    """
    Comprehensive integration service for CAAIN Soil Hub drought management.
    
    Features:
    - Service discovery and health monitoring
    - Cross-service data synchronization
    - API compatibility management
    - Data consistency validation
    - Error handling and fallback mechanisms
    - Performance monitoring and optimization
    - Drought-specific integration workflows
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize the CAAIN drought integration service."""
        self.database_url = database_url
        self.service_clients: Dict[str, ServiceClient] = {}
        self.service_status: Dict[str, Dict[str, Any]] = {}
        self.integration_config = self._load_integration_config()
        self.data_sync_cache: Dict[str, Any] = {}
        self.last_sync_times: Dict[str, datetime] = {}
        
        # Initialize service clients
        self._initialize_service_clients()
        
        logger.info("CAAIN Drought Integration Service initialized")
    
    def _load_integration_config(self) -> Dict[str, Any]:
        """Load integration configuration for all CAAIN services."""
        return {
            "services": {
                "recommendation-engine": {
                    "url": "http://localhost:8001",
                    "port": 8001,
                    "critical": True,
                    "endpoints": {
                        "health": "/health",
                        "crop_recommendations": "/api/v1/recommendations/crop-varieties",
                        "soil_analysis": "/api/v1/recommendations/soil-analysis",
                        "fertilizer_recommendations": "/api/v1/recommendations/fertilizer"
                    },
                    "integration_features": [
                        "crop_recommendations",
                        "soil_analysis", 
                        "fertilizer_recommendations",
                        "drought_resilient_crops"
                    ]
                },
                "data-integration": {
                    "url": "http://localhost:8003",
                    "port": 8003,
                    "critical": True,
                    "endpoints": {
                        "health": "/health",
                        "soil_data": "/api/v1/soil/data",
                        "climate_zones": "/api/v1/climate-zones/by-coordinates",
                        "weather_data": "/api/v1/weather/current",
                        "market_data": "/api/v1/market/prices"
                    },
                    "integration_features": [
                        "soil_data",
                        "climate_zones",
                        "weather_data",
                        "market_data"
                    ]
                },
                "ai-agent": {
                    "url": "http://localhost:8002",
                    "port": 8002,
                    "critical": True,
                    "endpoints": {
                        "health": "/health",
                        "explain_recommendation": "/api/v1/ai/explain",
                        "context_management": "/api/v1/context/manage"
                    },
                    "integration_features": [
                        "ai_explanations",
                        "context_management",
                        "drought_recommendation_explanations"
                    ]
                },
                "user-management": {
                    "url": "http://localhost:8005",
                    "port": 8005,
                    "critical": True,
                    "endpoints": {
                        "health": "/health",
                        "user_profile": "/api/v1/users/profile",
                        "farm_locations": "/api/v1/users/locations"
                    },
                    "integration_features": [
                        "user_profiles",
                        "farm_locations",
                        "user_preferences"
                    ]
                },
                "frontend": {
                    "url": "http://localhost:3000",
                    "port": 3000,
                    "critical": False,
                    "endpoints": {
                        "health": "/health",
                        "drought_management": "/drought-management"
                    },
                    "integration_features": [
                        "ui_integration",
                        "user_interface"
                    ]
                },
                "question-router": {
                    "url": "http://localhost:8000",
                    "port": 8000,
                    "critical": True,
                    "endpoints": {
                        "health": "/health",
                        "route_question": "/api/v1/questions/route"
                    },
                    "integration_features": [
                        "question_routing",
                        "drought_questions"
                    ]
                },
                "crop-taxonomy": {
                    "url": "http://localhost:8004",
                    "port": 8004,
                    "critical": True,
                    "endpoints": {
                        "health": "/health",
                        "crop_varieties": "/api/v1/crops/varieties",
                        "drought_resilient_crops": "/api/v1/crops/drought-resilient"
                    },
                    "integration_features": [
                        "crop_varieties",
                        "drought_resilient_crops",
                        "crop_characteristics"
                    ]
                },
                "cover-crop-selection": {
                    "url": "http://localhost:8006",
                    "port": 8006,
                    "critical": False,
                    "endpoints": {
                        "health": "/health",
                        "cover_crop_recommendations": "/api/v1/cover-crops/recommendations"
                    },
                    "integration_features": [
                        "cover_crop_recommendations",
                        "moisture_conservation_covers"
                    ]
                }
            },
            "sync_intervals": {
                "critical_services": 300,  # 5 minutes
                "non_critical_services": 900,  # 15 minutes
                "data_cache": 1800  # 30 minutes
            },
            "timeout_settings": {
                "health_check": 10,
                "api_call": 30,
                "data_sync": 60
            }
        }
    
    def _initialize_service_clients(self):
        """Initialize service clients for all CAAIN services."""
        for service_name, config in self.integration_config["services"].items():
            try:
                self.service_clients[service_name] = ServiceClient(
                    config["url"], 
                    service_name
                )
                self.service_status[service_name] = {
                    "status": "unknown",
                    "last_check": None,
                    "response_time": None,
                    "error_count": 0,
                    "critical": config.get("critical", False)
                }
                logger.info(f"Initialized client for {service_name} at {config['url']}")
            except Exception as e:
                logger.error(f"Failed to initialize client for {service_name}: {str(e)}")
                self.service_status[service_name] = {
                    "status": "error",
                    "last_check": datetime.utcnow(),
                    "response_time": None,
                    "error_count": 1,
                    "critical": config.get("critical", False),
                    "error": str(e)
                }
    
    async def initialize(self):
        """Initialize the integration service."""
        logger.info("Initializing CAAIN Drought Integration Service...")
        
        # Perform initial health checks
        await self.check_all_services_health()
        
        # Start background sync tasks
        asyncio.create_task(self._background_health_monitoring())
        asyncio.create_task(self._background_data_sync())
        
        logger.info("CAAIN Drought Integration Service initialized successfully")
    
    async def check_all_services_health(self) -> Dict[str, Dict[str, Any]]:
        """Check health status of all CAAIN services."""
        health_results = {}
        
        for service_name, client in self.service_clients.items():
            try:
                start_time = datetime.utcnow()
                
                async with client as c:
                    health_response = await c.get("/health")
                
                response_time = (datetime.utcnow() - start_time).total_seconds()
                
                health_results[service_name] = {
                    "status": "healthy" if health_response.get("status") in ["healthy", "ok"] else "unhealthy",
                    "response_time": response_time,
                    "last_check": datetime.utcnow(),
                    "details": health_response
                }
                
                # Update service status
                self.service_status[service_name].update({
                    "status": health_results[service_name]["status"],
                    "last_check": health_results[service_name]["last_check"],
                    "response_time": health_results[service_name]["response_time"],
                    "error_count": 0
                })
                
                logger.info(f"Health check for {service_name}: {health_results[service_name]['status']}")
                
            except Exception as e:
                health_results[service_name] = {
                    "status": "unhealthy",
                    "response_time": None,
                    "last_check": datetime.utcnow(),
                    "error": str(e)
                }
                
                # Update service status with error
                self.service_status[service_name].update({
                    "status": "unhealthy",
                    "last_check": health_results[service_name]["last_check"],
                    "response_time": None,
                    "error_count": self.service_status[service_name]["error_count"] + 1,
                    "error": str(e)
                })
                
                logger.error(f"Health check failed for {service_name}: {str(e)}")
        
        return health_results
    
    async def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get detailed status of a specific service."""
        if service_name not in self.service_status:
            raise ValueError(f"Unknown service: {service_name}")
        
        return self.service_status[service_name].copy()
    
    async def get_all_services_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all services."""
        return {name: status.copy() for name, status in self.service_status.items()}
    
    async def sync_soil_data(self, field_id: UUID) -> Dict[str, Any]:
        """Sync soil data from data-integration service."""
        try:
            client = self.service_clients["data-integration"]
            async with client as c:
                response = await c.get(f"/api/v1/soil/data/{field_id}")
            
            # Cache the data
            cache_key = f"soil_data_{field_id}"
            self.data_sync_cache[cache_key] = {
                "data": response,
                "timestamp": datetime.utcnow()
            }
            
            logger.info(f"Synced soil data for field {field_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to sync soil data for field {field_id}: {str(e)}")
            # Return cached data if available
            cache_key = f"soil_data_{field_id}"
            if cache_key in self.data_sync_cache:
                return self.data_sync_cache[cache_key]["data"]
            raise
    
    async def sync_weather_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Sync weather data from data-integration service."""
        try:
            client = self.service_clients["data-integration"]
            async with client as c:
                response = await c.get("/api/v1/weather/current", params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "include_agricultural": True
                })
            
            # Cache the data
            cache_key = f"weather_data_{latitude}_{longitude}"
            self.data_sync_cache[cache_key] = {
                "data": response,
                "timestamp": datetime.utcnow()
            }
            
            logger.info(f"Synced weather data for {latitude}, {longitude}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to sync weather data for {latitude}, {longitude}: {str(e)}")
            # Return cached data if available
            cache_key = f"weather_data_{latitude}_{longitude}"
            if cache_key in self.data_sync_cache:
                return self.data_sync_cache[cache_key]["data"]
            raise
    
    async def get_drought_resilient_crops(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get drought-resilient crop recommendations from crop-taxonomy service."""
        try:
            client = self.service_clients["crop-taxonomy"]
            async with client as c:
                response = await c.post("/api/v1/crops/drought-resilient", data=location_data)
            
            logger.info("Retrieved drought-resilient crop recommendations")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get drought-resilient crops: {str(e)}")
            raise
    
    async def get_cover_crop_recommendations(self, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get cover crop recommendations for moisture conservation."""
        try:
            client = self.service_clients["cover-crop-selection"]
            async with client as c:
                response = await c.post("/api/v1/cover-crops/recommendations", data=field_data)
            
            logger.info("Retrieved cover crop recommendations for moisture conservation")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get cover crop recommendations: {str(e)}")
            raise
    
    async def explain_drought_recommendation(self, recommendation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI explanation for drought management recommendations."""
        try:
            client = self.service_clients["ai-agent"]
            async with client as c:
                response = await c.post("/api/v1/ai/explain", data={
                    "type": "drought_management",
                    "data": recommendation_data
                })
            
            logger.info("Retrieved AI explanation for drought recommendation")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get AI explanation: {str(e)}")
            raise
    
    async def route_drought_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route drought-related questions through question-router."""
        try:
            client = self.service_clients["question-router"]
            async with client as c:
                response = await c.post("/api/v1/questions/route", data=question_data)
            
            logger.info("Routed drought question through question-router")
            return response
            
        except Exception as e:
            logger.error(f"Failed to route drought question: {str(e)}")
            raise
    
    async def _background_health_monitoring(self):
        """Background task for continuous health monitoring."""
        while True:
            try:
                await self.check_all_services_health()
                
                # Check critical services more frequently
                critical_services = [
                    name for name, status in self.service_status.items() 
                    if status.get("critical", False)
                ]
                
                if any(self.service_status[name]["status"] != "healthy" for name in critical_services):
                    logger.warning("Critical services are unhealthy")
                
                # Wait before next check
                await asyncio.sleep(self.integration_config["sync_intervals"]["critical_services"])
                
            except Exception as e:
                logger.error(f"Error in background health monitoring: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def _background_data_sync(self):
        """Background task for data synchronization."""
        while True:
            try:
                # Sync critical data periodically
                await self._sync_critical_data()
                
                # Wait before next sync
                await asyncio.sleep(self.integration_config["sync_intervals"]["data_cache"])
                
            except Exception as e:
                logger.error(f"Error in background data sync: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def _sync_critical_data(self):
        """Sync critical data from all services."""
        # This would sync commonly used data to improve performance
        # Implementation depends on specific data requirements
        pass
    
    async def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up CAAIN Drought Integration Service...")
        
        # Close all service clients
        for client in self.service_clients.values():
            if hasattr(client, 'cleanup'):
                await client.cleanup()
        
        logger.info("CAAIN Drought Integration Service cleanup completed")


# Global instance
caain_integration_service: Optional[CAAINDroughtIntegrationService] = None


async def get_caain_integration_service() -> CAAINDroughtIntegrationService:
    """Get the global CAAIN integration service instance."""
    global caain_integration_service
    if caain_integration_service is None:
        caain_integration_service = CAAINDroughtIntegrationService()
        await caain_integration_service.initialize()
    return caain_integration_service