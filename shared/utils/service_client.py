"""
Service Client Utility

Provides HTTP client functionality for inter-service communication
with proper error handling, retries, and logging.
"""

import aiohttp
import logging
import asyncio
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class ServiceClientError(Exception):
    """Base exception for service client errors."""
    pass


class ServiceUnavailableError(ServiceClientError):
    """Raised when a service is unavailable."""
    pass


class ServiceTimeoutError(ServiceClientError):
    """Raised when a service call times out."""
    pass


class ServiceClient:
    """HTTP client for inter-service communication."""
    
    def __init__(
        self,
        base_url: str,
        service_name: str,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize service client.
        
        Args:
            base_url: Base URL of the target service
            service_name: Name of the target service (for logging)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.service_name = service_name
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure HTTP session is created."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': f'AFAS-ServiceClient/{self.service_name}'
                }
            )
    
    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def get(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make GET request to service.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Response JSON data
            
        Raises:
            ServiceClientError: On client errors
            ServiceUnavailableError: When service is unavailable
            ServiceTimeoutError: On timeout
        """
        return await self._make_request('GET', endpoint, params=params, headers=headers)
    
    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make POST request to service.
        
        Args:
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Response JSON data
            
        Raises:
            ServiceClientError: On client errors
            ServiceUnavailableError: When service is unavailable
            ServiceTimeoutError: On timeout
        """
        return await self._make_request('POST', endpoint, data=data, params=params, headers=headers)
    
    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make PUT request to service.
        
        Args:
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Response JSON data
        """
        return await self._make_request('PUT', endpoint, data=data, params=params, headers=headers)
    
    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make DELETE request to service.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Response JSON data
        """
        return await self._make_request('DELETE', endpoint, params=params, headers=headers)
    
    async def health_check(self) -> bool:
        """
        Check if service is healthy.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            response = await self.get('/health')
            return response.get('status') in ['healthy', 'ok']
        except Exception as e:
            logger.warning(f"Health check failed for {self.service_name}: {str(e)}")
            return False
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body data
            params: Query parameters  
            headers: Additional headers
            
        Returns:
            Response JSON data
            
        Raises:
            ServiceClientError: On client errors
            ServiceUnavailableError: When service is unavailable
            ServiceTimeoutError: On timeout
        """
        await self._ensure_session()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = headers or {}
        
        # Add request ID for tracing
        request_id = f"{self.service_name}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        request_headers['X-Request-ID'] = request_id
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"Making {method} request to {url} (attempt {attempt + 1}/{self.max_retries + 1})")
                
                async with self._session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=request_headers
                ) as response:
                    
                    # Log response details
                    logger.debug(f"Response from {self.service_name}: {response.status}")
                    
                    # Handle different status codes
                    if response.status == 200:
                        try:
                            response_data = await response.json()
                            logger.debug(f"Successful request to {self.service_name}: {endpoint}")
                            return response_data
                        except json.JSONDecodeError as e:
                            raise ServiceClientError(f"Invalid JSON response from {self.service_name}: {str(e)}")
                    
                    elif response.status == 404:
                        raise ServiceClientError(f"Endpoint not found on {self.service_name}: {endpoint}")
                    
                    elif response.status == 400:
                        try:
                            error_data = await response.json()
                            error_msg = error_data.get('detail', 'Bad request')
                        except:
                            error_msg = await response.text()
                        raise ServiceClientError(f"Bad request to {self.service_name}: {error_msg}")
                    
                    elif response.status == 500:
                        try:
                            error_data = await response.json()
                            error_msg = error_data.get('detail', 'Internal server error')
                        except:
                            error_msg = await response.text()
                        raise ServiceUnavailableError(f"Server error from {self.service_name}: {error_msg}")
                    
                    elif response.status == 503:
                        raise ServiceUnavailableError(f"Service {self.service_name} temporarily unavailable")
                    
                    else:
                        try:
                            error_data = await response.json()
                            error_msg = error_data.get('detail', f'HTTP {response.status}')
                        except:
                            error_msg = f'HTTP {response.status}'
                        raise ServiceClientError(f"Request failed to {self.service_name}: {error_msg}")
            
            except asyncio.TimeoutError as e:
                last_exception = ServiceTimeoutError(f"Request timeout to {self.service_name}")
                logger.warning(f"Timeout on attempt {attempt + 1} to {self.service_name}: {endpoint}")
            
            except aiohttp.ClientConnectorError as e:
                last_exception = ServiceUnavailableError(f"Cannot connect to {self.service_name}: {str(e)}")
                logger.warning(f"Connection error on attempt {attempt + 1} to {self.service_name}: {str(e)}")
            
            except aiohttp.ClientError as e:
                last_exception = ServiceClientError(f"Client error calling {self.service_name}: {str(e)}")
                logger.warning(f"Client error on attempt {attempt + 1} to {self.service_name}: {str(e)}")
            
            except (ServiceClientError, ServiceUnavailableError, ServiceTimeoutError):
                # Re-raise service-specific errors immediately
                raise
            
            except Exception as e:
                last_exception = ServiceClientError(f"Unexpected error calling {self.service_name}: {str(e)}")
                logger.error(f"Unexpected error on attempt {attempt + 1} to {self.service_name}: {str(e)}")
            
            # Wait before retry (except on last attempt)
            if attempt < self.max_retries:
                await asyncio.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
        
        # All retries exhausted
        if last_exception:
            raise last_exception
        else:
            raise ServiceClientError(f"All retry attempts failed for {self.service_name}")


class CoverCropServiceClient(ServiceClient):
    """Specialized client for cover-crop-selection service."""
    
    def __init__(self, base_url: str = "http://localhost:8006"):
        """Initialize cover crop service client."""
        super().__init__(base_url, "cover-crop-selection")
    
    async def select_cover_crops(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get cover crop recommendations.
        
        Args:
            request_data: Cover crop selection request
            
        Returns:
            Cover crop recommendations
        """
        return await self.post("/api/v1/cover-crops/select", data=request_data)
    
    async def get_species_lookup(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get cover crop species lookup.
        
        Args:
            filters: Optional filters for species lookup
            
        Returns:
            Species lookup results
        """
        params = filters or {}
        return await self.get("/api/v1/cover-crops/species", params=params)
    
    async def get_seasonal_recommendations(
        self,
        latitude: float,
        longitude: float,
        target_season: str,
        field_size_acres: float
    ) -> Dict[str, Any]:
        """
        Get seasonal cover crop recommendations.
        
        Args:
            latitude: Field latitude
            longitude: Field longitude
            target_season: Target growing season
            field_size_acres: Field size in acres
            
        Returns:
            Seasonal recommendations
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "target_season": target_season,
            "field_size_acres": field_size_acres
        }
        return await self.post("/api/v1/cover-crops/seasonal", params=params)
    
    async def get_goal_based_recommendations(
        self,
        request_data: Dict[str, Any],
        objectives_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get goal-based cover crop recommendations.
        
        Args:
            request_data: Cover crop selection request
            objectives_data: Goal-based objectives
            
        Returns:
            Goal-based recommendations
        """
        payload = {
            "request": request_data,
            "objectives": objectives_data
        }
        return await self.post("/api/v1/cover-crops/goal-based-recommendations", data=payload)


class ServiceRegistry:
    """Registry for managing service clients."""
    
    def __init__(self):
        """Initialize service registry."""
        self._clients: Dict[str, ServiceClient] = {}
        self._default_config = self._load_default_config()
    
    def _load_default_config(self) -> Dict[str, str]:
        """Load default service configuration."""
        return {
            "cover-crop-selection": "http://localhost:8006",
            "recommendation-engine": "http://localhost:8001",
            "ai-agent": "http://localhost:8002", 
            "data-integration": "http://localhost:8003",
            "question-router": "http://localhost:8000",
            "user-management": "http://localhost:8005",
            "image-analysis": "http://localhost:8004"
        }
    
    def get_client(self, service_name: str, base_url: Optional[str] = None) -> ServiceClient:
        """
        Get or create service client.
        
        Args:
            service_name: Name of the service
            base_url: Optional custom base URL
            
        Returns:
            Service client instance
        """
        client_key = f"{service_name}_{base_url or 'default'}"
        
        if client_key not in self._clients:
            url = base_url or self._default_config.get(service_name)
            if not url:
                raise ValueError(f"No configuration found for service: {service_name}")
            
            # Create specialized clients for known services
            if service_name == "cover-crop-selection":
                self._clients[client_key] = CoverCropServiceClient(url)
            else:
                self._clients[client_key] = ServiceClient(url, service_name)
        
        return self._clients[client_key]
    
    async def close_all(self):
        """Close all service clients."""
        for client in self._clients.values():
            await client.close()
        self._clients.clear()


# Global service registry instance
service_registry = ServiceRegistry()


# Convenience functions for common operations
async def get_cover_crop_client() -> CoverCropServiceClient:
    """Get cover crop service client."""
    return service_registry.get_client("cover-crop-selection")


async def call_service(
    service_name: str,
    endpoint: str,
    method: str = "GET",
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    base_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function for making service calls.
    
    Args:
        service_name: Name of the target service
        endpoint: API endpoint
        method: HTTP method
        data: Request body data
        params: Query parameters
        base_url: Optional custom base URL
        
    Returns:
        Response data
    """
    client = service_registry.get_client(service_name, base_url)
    
    method_func = getattr(client, method.lower())
    if method.upper() in ['GET', 'DELETE']:
        return await method_func(endpoint, params=params)
    else:
        return await method_func(endpoint, data=data, params=params)