"""
CAAIN Soil Hub Integration Service

Comprehensive integration service for connecting the crop-taxonomy service
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


class CAAINIntegrationService:
    """
    Comprehensive integration service for CAAIN Soil Hub services.
    
    Features:
    - Service discovery and health monitoring
    - Cross-service data synchronization
    - API compatibility management
    - Data consistency validation
    - Error handling and fallback mechanisms
    - Performance monitoring and optimization
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize the CAAIN integration service."""
        self.database_url = database_url
        self.service_clients: Dict[str, ServiceClient] = {}
        self.service_status: Dict[str, Dict[str, Any]] = {}
        self.integration_config = self._load_integration_config()
        self.data_sync_cache: Dict[str, Any] = {}
        self.last_sync_times: Dict[str, datetime] = {}
        
        # Initialize service clients
        self._initialize_service_clients()
        
        logger.info("CAAIN Integration Service initialized")
    
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
                    "ph_management": "/api/v1/ph/analyze"
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
                    "market_data": "/api/v1/market/prices"
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
                    "conversation": "/api/v1/conversation"
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
                    "intent_classification": "/api/v1/questions/classify"
                },
                "timeout": 20,
                "retry_attempts": 3,
                "critical": True
            },
            "cover-crop-selection": {
                "base_url": "http://localhost:8006",
                "endpoints": {
                    "health": "/health",
                    "select_cover_crops": "/api/v1/cover-crops/select",
                    "seasonal_recommendations": "/api/v1/cover-crops/seasonal"
                },
                "timeout": 30,
                "retry_attempts": 2,
                "critical": False
            },
            "user-management": {
                "base_url": "http://localhost:8005",
                "endpoints": {
                    "health": "/health",
                    "user_profile": "/api/v1/users/profile",
                    "farm_locations": "/api/v1/users/farms"
                },
                "timeout": 20,
                "retry_attempts": 3,
                "critical": False
            },
            "image-analysis": {
                "base_url": "http://localhost:8004",
                "endpoints": {
                    "health": "/health",
                    "analyze_image": "/api/v1/image/analyze",
                    "deficiency_detection": "/api/v1/image/deficiency"
                },
                "timeout": 60,
                "retry_attempts": 2,
                "critical": False
            }
        }
    
    def _initialize_service_clients(self):
        """Initialize service clients for all configured services."""
        for service_name, config in self.integration_config.items():
            try:
                client = ServiceClient(
                    base_url=config["base_url"],
                    service_name=service_name
                )
                self.service_clients[service_name] = client
                self.service_status[service_name] = {
                    "status": "unknown",
                    "last_check": None,
                    "response_time": None,
                    "error_count": 0,
                    "critical": config.get("critical", False)
                }
                logger.info(f"Service client initialized for {service_name}")
            except Exception as e:
                logger.error(f"Failed to initialize client for {service_name}: {e}")
                self.service_status[service_name] = {
                    "status": "error",
                    "last_check": datetime.now(),
                    "response_time": None,
                    "error_count": 1,
                    "critical": config.get("critical", False),
                    "error": str(e)
                }
    
    async def health_check_all_services(self) -> Dict[str, Dict[str, Any]]:
        """
        Perform health checks on all integrated services.
        
        Returns:
            Dictionary with health status for each service
        """
        health_results = {}
        
        for service_name, client in self.service_clients.items():
            try:
                start_time = datetime.now()
                
                async with client as session:
                    is_healthy = await session.health_check()
                
                response_time = (datetime.now() - start_time).total_seconds()
                
                self.service_status[service_name].update({
                    "status": "healthy" if is_healthy else "unhealthy",
                    "last_check": datetime.now(),
                    "response_time": response_time,
                    "error_count": 0
                })
                
                health_results[service_name] = {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "response_time": response_time,
                    "last_check": datetime.now().isoformat(),
                    "critical": self.service_status[service_name]["critical"]
                }
                
                logger.info(f"Health check for {service_name}: {'healthy' if is_healthy else 'unhealthy'} ({response_time:.2f}s)")
                
            except Exception as e:
                error_count = self.service_status[service_name].get("error_count", 0) + 1
                self.service_status[service_name].update({
                    "status": "error",
                    "last_check": datetime.now(),
                    "response_time": None,
                    "error_count": error_count,
                    "error": str(e)
                })
                
                health_results[service_name] = {
                    "status": "error",
                    "error": str(e),
                    "last_check": datetime.now().isoformat(),
                    "critical": self.service_status[service_name]["critical"]
                }
                
                logger.error(f"Health check failed for {service_name}: {e}")
        
        return health_results
    
    async def get_service_data(
        self, 
        service_name: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get data from a specific service endpoint.
        
        Args:
            service_name: Name of the target service
            endpoint: API endpoint to call
            params: Query parameters
            data: Request body data
            
        Returns:
            Response data from the service
            
        Raises:
            ServiceClientError: If the service call fails
        """
        if service_name not in self.service_clients:
            raise ServiceClientError(f"Service {service_name} not configured")
        
        client = self.service_clients[service_name]
        
        try:
            async with client as session:
                if data:
                    response = await session.post(endpoint, data=data)
                else:
                    response = await session.get(endpoint, params=params)
                
                # Update service status on successful call
                self.service_status[service_name]["error_count"] = 0
                
                return response
                
        except Exception as e:
            # Update error count
            self.service_status[service_name]["error_count"] += 1
            logger.error(f"Service call failed for {service_name}/{endpoint}: {e}")
            raise ServiceClientError(f"Failed to call {service_name}/{endpoint}: {e}")
    
    async def sync_crop_data_with_recommendation_engine(
        self, 
        crop_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synchronize crop variety data with the recommendation engine.
        
        Args:
            crop_data: Crop variety data to synchronize
            
        Returns:
            Synchronization result
        """
        try:
            response = await self.get_service_data(
                service_name="recommendation-engine",
                endpoint="/api/v1/recommendations/crop-varieties/sync",
                data=crop_data
            )
            
            # Cache the sync result
            sync_key = f"crop_sync_{crop_data.get('variety_id', 'unknown')}"
            self.data_sync_cache[sync_key] = {
                "data": crop_data,
                "response": response,
                "timestamp": datetime.now()
            }
            
            return response
            
        except ServiceClientError as e:
            logger.error(f"Failed to sync crop data with recommendation engine: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_soil_data_for_location(
        self, 
        latitude: float, 
        longitude: float
    ) -> Dict[str, Any]:
        """
        Get soil data for a specific location from data-integration service.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Soil characteristics data
        """
        try:
            response = await self.get_service_data(
                service_name="data-integration",
                endpoint="/api/v1/soil/characteristics",
                data={"latitude": latitude, "longitude": longitude}
            )
            
            return response
            
        except ServiceClientError as e:
            logger.error(f"Failed to get soil data for location {latitude}, {longitude}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_climate_data_for_location(
        self, 
        latitude: float, 
        longitude: float
    ) -> Dict[str, Any]:
        """
        Get climate zone data for a specific location.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Climate zone data
        """
        try:
            response = await self.get_service_data(
                service_name="data-integration",
                endpoint="/api/v1/climate-zones/by-coordinates",
                params={"latitude": latitude, "longitude": longitude}
            )
            
            return response
            
        except ServiceClientError as e:
            logger.error(f"Failed to get climate data for location {latitude}, {longitude}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_ai_explanation_for_recommendation(
        self, 
        recommendation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get AI-powered explanation for a variety recommendation.
        
        Args:
            recommendation_data: Recommendation data to explain
            
        Returns:
            AI explanation
        """
        try:
            response = await self.get_service_data(
                service_name="ai-agent",
                endpoint="/api/v1/ai/explain",
                data={
                    "type": "variety_recommendation",
                    "data": recommendation_data
                }
            )
            
            return response
            
        except ServiceClientError as e:
            logger.error(f"Failed to get AI explanation: {e}")
            return {"status": "error", "error": str(e)}
    
    async def validate_data_consistency(
        self, 
        data_type: str, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate data consistency across services.
        
        Args:
            data_type: Type of data to validate
            data: Data to validate
            
        Returns:
            Validation result
        """
        validation_results = {
            "data_type": data_type,
            "timestamp": datetime.now().isoformat(),
            "validations": {},
            "overall_status": "valid"
        }
        
        # Validate against different services based on data type
        if data_type == "crop_variety":
            # Validate against recommendation engine
            try:
                rec_validation = await self.get_service_data(
                    service_name="recommendation-engine",
                    endpoint="/api/v1/validation/crop-variety",
                    data=data
                )
                validation_results["validations"]["recommendation_engine"] = rec_validation
            except ServiceClientError as e:
                validation_results["validations"]["recommendation_engine"] = {"status": "error", "error": str(e)}
        
        elif data_type == "soil_data":
            # Validate against data integration service
            try:
                soil_validation = await self.get_service_data(
                    service_name="data-integration",
                    endpoint="/api/v1/validation/soil-data",
                    data=data
                )
                validation_results["validations"]["data_integration"] = soil_validation
            except ServiceClientError as e:
                validation_results["validations"]["data_integration"] = {"status": "error", "error": str(e)}
        
        # Determine overall status
        error_count = sum(1 for v in validation_results["validations"].values() 
                         if v.get("status") == "error")
        if error_count > 0:
            validation_results["overall_status"] = "invalid"
        
        return validation_results
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """
        Get comprehensive integration status for all services.
        
        Returns:
            Integration status summary
        """
        # Perform health checks
        health_results = await self.health_check_all_services()
        
        # Calculate overall status
        critical_services = [name for name, status in self.service_status.items() 
                           if status.get("critical", False)]
        critical_healthy = all(health_results.get(name, {}).get("status") == "healthy" 
                             for name in critical_services)
        
        total_services = len(self.service_clients)
        healthy_services = sum(1 for status in health_results.values() 
                             if status.get("status") == "healthy")
        
        return {
            "overall_status": "healthy" if critical_healthy else "degraded",
            "total_services": total_services,
            "healthy_services": healthy_services,
            "critical_services_healthy": critical_healthy,
            "service_details": health_results,
            "last_updated": datetime.now().isoformat(),
            "integration_features": {
                "service_discovery": True,
                "health_monitoring": True,
                "data_synchronization": True,
                "cross_service_validation": True,
                "error_handling": True,
                "performance_monitoring": True
            }
        }
    
    async def close(self):
        """Close all service clients."""
        for client in self.service_clients.values():
            if hasattr(client, 'close'):
                await client.close()
        logger.info("All service clients closed")


# Global integration service instance
_integration_service: Optional[CAAINIntegrationService] = None


def get_integration_service() -> CAAINIntegrationService:
    """Get the global integration service instance."""
    global _integration_service
    if _integration_service is None:
        _integration_service = CAAINIntegrationService()
    return _integration_service


async def cleanup_integration_service():
    """Cleanup the global integration service."""
    global _integration_service
    if _integration_service:
        await _integration_service.close()
        _integration_service = None