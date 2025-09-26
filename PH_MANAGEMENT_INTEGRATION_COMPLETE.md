# pH Management System Integration Guide

## Overview

This document describes the complete system integration for the CAAIN Soil Hub pH management system, connecting frontend UI with backend services.

## Architecture

### Service Communication Flow

```
Frontend (Port 3000)
    ↓ HTTP API Calls
Recommendation Engine (Port 8001)
    ↓ Data Processing
pH Management Service
    ↓ Database Operations
PostgreSQL/MongoDB
```

### Integrated Components

1. **Frontend Service** (`services/frontend/src/main.py`)
   - Serves pH management UI at `/ph-management`
   - Provides API proxy endpoints under `/api/ph/`
   - Handles form submissions and user interactions

2. **Recommendation Engine** (`services/recommendation-engine/src/`)
   - Includes pH management routes at `/api/v1/ph/`
   - Processes pH analysis and lime calculations
   - Manages monitoring and dashboard data

3. **pH Management Service** (`services/recommendation-engine/src/services/soil_ph_management_service.py`)
   - Core business logic for pH analysis
   - Lime requirement calculations
   - Crop pH requirements database

## API Endpoints

### Frontend Proxy Endpoints

All endpoints accept form data and proxy requests to the recommendation engine:

- `POST /api/ph/analyze` - Analyze soil pH levels
- `POST /api/ph/lime-calculator` - Calculate lime requirements
- `GET /api/ph/crop-requirements` - Get crop-specific pH requirements
- `POST /api/ph/monitor` - Setup pH monitoring
- `GET /api/ph/dashboard` - Get farm pH dashboard
- `GET /api/ph/trends` - Get pH trend analysis

### Backend Service Endpoints

Direct backend endpoints in recommendation engine:

- `POST /api/v1/ph/analyze` - Core pH analysis service
- `POST /api/v1/ph/lime-calculator` - Lime calculation service
- `GET /api/v1/ph/crop-requirements` - Crop requirements service
- `POST /api/v1/ph/monitor` - Monitoring setup service
- `GET /api/v1/ph/dashboard` - Dashboard data service
- `GET /api/v1/ph/trends` - Trend analysis service

## Service Configuration

### Environment Variables

Required environment variables for service communication:

```bash
# Service URLs
QUESTION_ROUTER_URL=http://localhost:8000
RECOMMENDATION_ENGINE_URL=http://localhost:8001
AI_AGENT_URL=http://localhost:8002
DATA_INTEGRATION_URL=http://localhost:8003
IMAGE_ANALYSIS_URL=http://localhost:8004
USER_MANAGEMENT_URL=http://localhost:8005
FRONTEND_URL=http://localhost:3000

# Service Ports
FRONTEND_PORT=3000
RECOMMENDATION_ENGINE_PORT=8001

# pH Management
PH_MANAGEMENT_ENABLED=true
PH_SERVICE_TIMEOUT=30
```

### CORS Configuration

Both frontend and backend services are configured with CORS middleware to allow cross-service communication:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Service Startup

### Automated Startup

Use the integrated startup script:

```bash
./start-all.sh
```

This script now includes the frontend service and will start all services in the correct order:

1. Question Router (Port 8000)
2. Recommendation Engine (Port 8001) - includes pH management
3. AI Agent (Port 8002)
4. Data Integration (Port 8003)
5. Image Analysis (Port 8004)
6. User Management (Port 8005)
7. Frontend (Port 3000)

### Manual Startup

If starting services manually:

```bash
# Start Recommendation Engine (includes pH management)
cd services/recommendation-engine
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload

# Start Frontend
cd ../frontend  
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 3000 --reload
```

## Data Flow Integration

### pH Analysis Workflow

1. **User Input**: Farmer enters soil data in pH management UI
2. **Frontend Processing**: Form data validated and formatted
3. **API Proxy**: Frontend sends request to `/api/ph/analyze`
4. **Service Communication**: Frontend proxies to recommendation engine
5. **pH Analysis**: Backend processes soil data using pH management service
6. **Response**: Results returned through frontend to UI
7. **Display**: Results rendered in user-friendly format

### Lime Calculator Workflow

1. **Input**: Current pH, target pH, soil characteristics
2. **Calculation**: Backend calculates lime requirements
3. **Recommendations**: Multiple lime type options with costs
4. **Display**: Results shown with application instructions

### Monitoring Setup Workflow

1. **Configuration**: User sets monitoring frequency and thresholds
2. **Storage**: Monitoring plan saved to database
3. **Scheduling**: Future tests scheduled based on frequency
4. **Alerts**: Thresholds configured for automated notifications

## Error Handling

### Service Communication Errors

- **Connection Timeouts**: 30-second timeout for all API calls
- **Service Unavailable**: Graceful degradation with error messages
- **Data Validation**: Input validation on both frontend and backend

### Error Response Format

```json
{
    "success": false,
    "error": "Service temporarily unavailable",
    "details": "Connection to recommendation engine failed",
    "retry_after": 30
}
```

## Monitoring and Health Checks

### Service Health Endpoints

- Frontend: `http://localhost:3000/health`
- Recommendation Engine: `http://localhost:8001/health`

### Integration Status

The frontend health check now includes pH management status:

```json
{
    "service": "frontend",
    "status": "healthy", 
    "ph_management": {
        "status": "integrated",
        "endpoints": [
            "/api/ph/analyze",
            "/api/ph/lime-calculator",
            "/api/ph/crop-requirements",
            "/api/ph/monitor",
            "/api/ph/dashboard",
            "/api/ph/trends"
        ]
    }
}
```

## Testing Integration

### Integration Test Suite

Run the complete integration test:

```bash
python test_ph_management_integration.py
```

This tests:
- Service availability
- End-to-end API communication
- Data flow between services
- Error handling
- Complete user workflows

### Manual Testing

1. **Access pH Management**: `http://localhost:3000/ph-management`
2. **Test Analysis**: Enter soil data and submit analysis
3. **Test Calculator**: Use lime calculator with different scenarios
4. **Check Dashboard**: View farm pH dashboard
5. **Verify Monitoring**: Setup and check monitoring configuration

## Security Considerations

### API Security

- Input validation on all endpoints
- SQL injection protection through parameterized queries
- Rate limiting (implement in production)
- Authentication integration (future enhancement)

### Data Privacy

- Soil test data handled securely
- Farm information protected
- Monitoring data encrypted in transit

## Performance Optimization

### Response Times

- API calls optimized with 30-second timeout
- Caching implemented for crop requirements
- Database queries optimized with indexes

### Scalability

- Stateless service design
- Horizontal scaling ready
- Load balancer compatible

## Troubleshooting

### Common Issues

1. **Service Connection Errors**
   ```bash
   # Check if services are running
   curl http://localhost:3000/health
   curl http://localhost:8001/health
   ```

2. **pH Routes Not Found**
   ```bash
   # Verify pH routes are included
   curl http://localhost:8001/api/v1/ph/crop-requirements?crop_types=corn
   ```

3. **Frontend API Errors**
   ```bash
   # Test direct backend connection
   curl -X POST http://localhost:8001/api/v1/ph/analyze \
     -H "Content-Type: application/json" \
     -d '{"farm_id":"test","field_id":"test","crop_type":"corn","soil_test_data":{"ph":6.0}}'
   ```

### Service Logs

Check logs for integration issues:

```bash
# Frontend logs
tail -f services/frontend/logs/app.log

# Recommendation engine logs  
tail -f services/recommendation-engine/logs/app.log
```

## Future Enhancements

### Planned Improvements

1. **Authentication Integration**
   - User-based pH data access
   - Farm-specific data isolation
   - Role-based permissions

2. **Real-time Updates**
   - WebSocket integration for live data
   - Push notifications for alerts
   - Real-time dashboard updates

3. **Mobile Integration**
   - Responsive design improvements
   - Mobile app API compatibility
   - Offline data collection

4. **Advanced Analytics**
   - Machine learning pH predictions
   - Historical trend analysis
   - Comparative farm analytics

## Summary

The pH management system is now fully integrated across all services:

✅ **Frontend Service**: Included in startup script, serves pH management UI
✅ **API Integration**: Complete proxy layer for all pH management endpoints  
✅ **Service Communication**: Proper CORS and networking configuration
✅ **Error Handling**: Comprehensive error handling across service boundaries
✅ **Health Monitoring**: Integration status included in health checks
✅ **Testing**: Complete integration test suite implemented
✅ **Documentation**: Full integration documentation provided

The system now provides seamless end-to-end pH management functionality from the user interface through to the backend processing services.