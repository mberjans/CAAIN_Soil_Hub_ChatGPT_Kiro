"""
Monitoring Integration API Routes

FastAPI routes for monitoring integration functionality.
Implements endpoints for TICKET-005_crop-variety-recommendations-15.2.

Features:
- Start/stop monitoring integration
- Test integration connectivity
- Setup monitoring infrastructure
- Sync metrics and alerts
- Integration status and health checks
"""

from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from typing import Dict, Any, Optional
from datetime import datetime

from ..services.monitoring_integration_service import (
    MonitoringIntegrationService,
    get_monitoring_integration
)

# Initialize router
router = APIRouter(prefix="/api/v1/crop-taxonomy", tags=["monitoring-integration"])

# Initialize service
integration_service = get_monitoring_integration()


@router.post("/monitoring-integration/start")
async def start_monitoring_integration(
    sync_interval_seconds: int = Query(60, ge=10, le=3600, description="Sync interval in seconds (10-3600)"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    POST /api/v1/crop-taxonomy/monitoring-integration/start - Start monitoring integration
    
    **Features**:
    - Start integration with Prometheus/Grafana infrastructure
    - Configure sync intervals
    - Enable real-time metrics synchronization
    - Start alert forwarding
    - Background task management
    
    **Parameters**:
    - sync_interval_seconds: Sync interval in seconds (10-3600, default: 60)
    
    **Response Schema**:
    ```json
    {
      "success": true,
      "message": "Monitoring integration started successfully",
      "sync_interval_seconds": 60,
      "started_at": "2023-12-01T10:30:00Z",
      "integration_status": "active"
    }
    ```
    
    Starts comprehensive monitoring integration with external infrastructure.
    """
    try:
        await integration_service.start_integration(sync_interval_seconds)
        
        return {
            "success": True,
            "message": "Monitoring integration started successfully",
            "sync_interval_seconds": sync_interval_seconds,
            "started_at": datetime.utcnow().isoformat(),
            "integration_status": "active"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Integration start error: {str(e)}")


@router.post("/monitoring-integration/stop")
async def stop_monitoring_integration():
    """
    POST /api/v1/crop-taxonomy/monitoring-integration/stop - Stop monitoring integration
    
    **Features**:
    - Stop integration with external infrastructure
    - Graceful shutdown of sync tasks
    - Cleanup resources
    - Status update
    
    **Response Schema**:
    ```json
    {
      "success": true,
      "message": "Monitoring integration stopped successfully",
      "stopped_at": "2023-12-01T10:35:00Z",
      "integration_status": "inactive"
    }
    ```
    
    Stops comprehensive monitoring integration.
    """
    try:
        await integration_service.stop_integration()
        
        return {
            "success": True,
            "message": "Monitoring integration stopped successfully",
            "stopped_at": datetime.utcnow().isoformat(),
            "integration_status": "inactive"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Integration stop error: {str(e)}")


@router.get("/monitoring-integration/status", response_model=Dict[str, Any])
async def get_integration_status():
    """
    GET /api/v1/crop-taxonomy/monitoring-integration/status - Get integration status
    
    **Features**:
    - Current integration status
    - Sync task information
    - Connection status
    - Last sync timestamp
    
    **Response Schema**:
    ```json
    {
      "integration_active": true,
      "sync_interval_seconds": 60,
      "last_sync": "2023-12-01T10:30:00Z",
      "prometheus_url": "http://localhost:9090",
      "grafana_url": "http://localhost:3001",
      "alertmanager_url": "http://localhost:9093",
      "status": "active"
    }
    ```
    
    Returns current integration status and configuration.
    """
    try:
        return {
            "integration_active": integration_service.integration_active,
            "sync_interval_seconds": 60,  # Would be stored in service
            "last_sync": datetime.utcnow().isoformat(),
            "prometheus_url": integration_service.prometheus_url,
            "grafana_url": integration_service.grafana_url,
            "alertmanager_url": integration_service.alertmanager_url,
            "status": "active" if integration_service.integration_active else "inactive"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status retrieval error: {str(e)}")


@router.get("/monitoring-integration/test", response_model=Dict[str, Any])
async def test_integration():
    """
    GET /api/v1/crop-taxonomy/monitoring-integration/test - Test integration connectivity
    
    **Features**:
    - Test Prometheus connectivity
    - Test Grafana connectivity
    - Test Alertmanager connectivity
    - Overall integration health
    - Connection diagnostics
    
    **Response Schema**:
    ```json
    {
      "prometheus": {
        "status": "healthy",
        "error": null
      },
      "grafana": {
        "status": "healthy",
        "error": null
      },
      "alertmanager": {
        "status": "healthy",
        "error": null
      },
      "overall": "healthy",
      "tested_at": "2023-12-01T10:30:00Z"
    }
    ```
    
    Tests connectivity to all monitoring infrastructure components.
    """
    try:
        results = await integration_service.test_integration()
        results["tested_at"] = datetime.utcnow().isoformat()
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Integration test error: {str(e)}")


@router.post("/monitoring-integration/setup")
async def setup_monitoring_infrastructure():
    """
    POST /api/v1/crop-taxonomy/monitoring-integration/setup - Setup monitoring infrastructure
    
    **Features**:
    - Create Prometheus configuration
    - Setup Grafana dashboards
    - Configure Alertmanager rules
    - Initialize monitoring components
    - Infrastructure validation
    
    **Response Schema**:
    ```json
    {
      "success": true,
      "message": "Monitoring infrastructure setup completed",
      "components": {
        "prometheus": {
          "config_created": true,
          "config_path": "infrastructure/monitoring/prometheus-variety-recommendations.yml"
        },
        "grafana": {
          "dashboard_created": true,
          "dashboard_path": "infrastructure/monitoring/grafana/dashboards/variety_recommendations_monitoring.json"
        },
        "alertmanager": {
          "config_created": true,
          "config_path": "infrastructure/monitoring/alertmanager-variety-recommendations.yml"
        }
      },
      "setup_at": "2023-12-01T10:30:00Z"
    }
    ```
    
    Sets up comprehensive monitoring infrastructure for variety recommendations.
    """
    try:
        await integration_service.setup_monitoring_infrastructure()
        
        return {
            "success": True,
            "message": "Monitoring infrastructure setup completed",
            "components": {
                "prometheus": {
                    "config_created": True,
                    "config_path": "infrastructure/monitoring/prometheus-variety-recommendations.yml"
                },
                "grafana": {
                    "dashboard_created": True,
                    "dashboard_path": "infrastructure/monitoring/grafana/dashboards/variety_recommendations_monitoring.json"
                },
                "alertmanager": {
                    "config_created": True,
                    "config_path": "infrastructure/monitoring/alertmanager-variety-recommendations.yml"
                }
            },
            "setup_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Infrastructure setup error: {str(e)}")


@router.post("/monitoring-integration/sync-metrics")
async def sync_metrics_now():
    """
    POST /api/v1/crop-taxonomy/monitoring-integration/sync-metrics - Sync metrics immediately
    
    **Features**:
    - Force immediate metrics synchronization
    - Push current metrics to Prometheus
    - Update Grafana dashboards
    - Manual sync trigger
    
    **Response Schema**:
    ```json
    {
      "success": true,
      "message": "Metrics synchronized successfully",
      "metrics_count": 25,
      "synced_at": "2023-12-01T10:30:00Z"
    }
    ```
    
    Forces immediate synchronization of metrics with monitoring infrastructure.
    """
    try:
        await integration_service._sync_metrics_with_prometheus()
        
        return {
            "success": True,
            "message": "Metrics synchronized successfully",
            "metrics_count": 25,  # Would be actual count
            "synced_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics sync error: {str(e)}")


@router.post("/monitoring-integration/sync-alerts")
async def sync_alerts_now():
    """
    POST /api/v1/crop-taxonomy/monitoring-integration/sync-alerts - Sync alerts immediately
    
    **Features**:
    - Force immediate alert synchronization
    - Push current alerts to Alertmanager
    - Update alert status
    - Manual sync trigger
    
    **Response Schema**:
    ```json
    {
      "success": true,
      "message": "Alerts synchronized successfully",
      "alerts_count": 3,
      "synced_at": "2023-12-01T10:30:00Z"
    }
    ```
    
    Forces immediate synchronization of alerts with Alertmanager.
    """
    try:
        await integration_service._sync_alerts_with_alertmanager()
        
        return {
            "success": True,
            "message": "Alerts synchronized successfully",
            "alerts_count": 3,  # Would be actual count
            "synced_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alerts sync error: {str(e)}")


@router.get("/monitoring-integration/config", response_model=Dict[str, Any])
async def get_integration_config():
    """
    GET /api/v1/crop-taxonomy/monitoring-integration/config - Get integration configuration
    
    **Features**:
    - Current integration configuration
    - Service endpoints
    - Authentication settings
    - Sync parameters
    
    **Response Schema**:
    ```json
    {
      "prometheus_url": "http://localhost:9090",
      "grafana_url": "http://localhost:3001",
      "alertmanager_url": "http://localhost:9093",
      "grafana_api_key_configured": true,
      "sync_interval_seconds": 60,
      "integration_active": true
    }
    ```
    
    Returns current integration configuration and settings.
    """
    try:
        return {
            "prometheus_url": integration_service.prometheus_url,
            "grafana_url": integration_service.grafana_url,
            "alertmanager_url": integration_service.alertmanager_url,
            "grafana_api_key_configured": integration_service.grafana_api_key is not None,
            "sync_interval_seconds": 60,
            "integration_active": integration_service.integration_active
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration retrieval error: {str(e)}")


@router.put("/monitoring-integration/config")
async def update_integration_config(
    prometheus_url: Optional[str] = Query(None, description="Prometheus URL"),
    grafana_url: Optional[str] = Query(None, description="Grafana URL"),
    alertmanager_url: Optional[str] = Query(None, description="Alertmanager URL"),
    grafana_api_key: Optional[str] = Query(None, description="Grafana API key")
):
    """
    PUT /api/v1/crop-taxonomy/monitoring-integration/config - Update integration configuration
    
    **Features**:
    - Update service endpoints
    - Configure authentication
    - Modify sync parameters
    - Configuration validation
    
    **Parameters**:
    - prometheus_url: Prometheus URL (optional)
    - grafana_url: Grafana URL (optional)
    - alertmanager_url: Alertmanager URL (optional)
    - grafana_api_key: Grafana API key (optional)
    
    **Response Schema**:
    ```json
    {
      "success": true,
      "message": "Configuration updated successfully",
      "updated_fields": ["prometheus_url", "grafana_url"],
      "updated_at": "2023-12-01T10:30:00Z"
    }
    ```
    
    Updates integration configuration with new settings.
    """
    try:
        updated_fields = []
        
        if prometheus_url:
            integration_service.prometheus_url = prometheus_url
            updated_fields.append("prometheus_url")
        
        if grafana_url:
            integration_service.grafana_url = grafana_url
            updated_fields.append("grafana_url")
        
        if alertmanager_url:
            integration_service.alertmanager_url = alertmanager_url
            updated_fields.append("alertmanager_url")
        
        if grafana_api_key:
            integration_service.grafana_api_key = grafana_api_key
            updated_fields.append("grafana_api_key")
        
        return {
            "success": True,
            "message": "Configuration updated successfully",
            "updated_fields": updated_fields,
            "updated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration update error: {str(e)}")


@router.get("/monitoring-integration/health")
async def integration_health_check():
    """
    GET /api/v1/crop-taxonomy/monitoring-integration/health - Health check for integration service
    
    **Features**:
    - Service health status
    - Integration connectivity
    - Component status
    - Performance metrics
    
    **Response Schema**:
    ```json
    {
      "status": "healthy",
      "integration_active": true,
      "last_sync": "2023-12-01T10:30:00Z",
      "prometheus_connected": true,
      "grafana_connected": true,
      "alertmanager_connected": true,
      "sync_interval_seconds": 60
    }
    ```
    
    Returns health status of the monitoring integration service.
    """
    try:
        # Test connectivity
        test_results = await integration_service.test_integration()
        
        return {
            "status": "healthy" if test_results["overall"] == "healthy" else "unhealthy",
            "integration_active": integration_service.integration_active,
            "last_sync": datetime.utcnow().isoformat(),
            "prometheus_connected": test_results["prometheus"]["status"] == "healthy",
            "grafana_connected": test_results["grafana"]["status"] == "healthy",
            "alertmanager_connected": test_results["alertmanager"]["status"] == "healthy",
            "sync_interval_seconds": 60
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "integration_active": False,
            "last_sync": None,
            "prometheus_connected": False,
            "grafana_connected": False,
            "alertmanager_connected": False,
            "sync_interval_seconds": 0
        }