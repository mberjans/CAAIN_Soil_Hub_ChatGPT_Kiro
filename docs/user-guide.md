# CAAIN Soil Hub - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Core Features](#core-features)
3. [API Usage](#api-usage)
4. [Best Practices](#best-practices)
5. [Troubleshooting](#troubleshooting)
6. [Support](#support)

## Getting Started

### Overview
The CAAIN Soil Hub Crop Taxonomy Service provides comprehensive agricultural intelligence for crop selection, variety recommendations, and regional adaptation analysis. This service is designed for farmers, agronomists, researchers, and agricultural professionals.

### Quick Start
1. **Access the Service**: Navigate to the service URL
2. **Explore the API**: Visit `/docs` for interactive API documentation
3. **Test Endpoints**: Use the health check endpoint `/api/v1/health`
4. **Get Recommendations**: Start with crop variety recommendations

### Authentication
Currently, the service operates in open mode for research and development. Production deployments will include authentication mechanisms.

## Core Features

### 1. Taxonomic Classification
Scientific crop classification following botanical and agricultural standards.

**Key Endpoints:**
- `GET /api/v1/taxonomy/crops` - List all crops
- `GET /api/v1/taxonomy/crops/{crop_id}` - Get specific crop details
- `POST /api/v1/taxonomy/crops/bulk` - Bulk crop processing

**Example Usage:**
```bash
# Get all crops
curl -X GET "https://api.caain-soil-hub.ca/api/v1/taxonomy/crops"

# Get specific crop
curl -X GET "https://api.caain-soil-hub.ca/api/v1/taxonomy/crops/1"
```

### 2. Advanced Search and Filtering
Multi-dimensional crop search with intelligent filtering and smart recommendations.

**Key Endpoints:**
- `POST /api/v1/search/crops` - Advanced crop search
- `GET /api/v1/search/suggestions` - Search suggestions
- `POST /api/v1/filtering/apply` - Apply filters

**Example Usage:**
```bash
# Search for crops suitable for specific conditions
curl -X POST "https://api.caain-soil-hub.ca/api/v1/search/crops" \
  -H "Content-Type: application/json" \
  -d '{
    "climate_zone": "6a",
    "soil_type": "clay_loam",
    "growing_season": 120,
    "preferences": ["high_yield", "disease_resistant"]
  }'
```

### 3. Variety Recommendations
Performance-based variety selection with regional adaptation analysis.

**Key Endpoints:**
- `POST /api/v1/varieties/recommend` - Get variety recommendations
- `GET /api/v1/varieties/{variety_id}` - Get variety details
- `POST /api/v1/varieties/compare` - Compare varieties

**Example Usage:**
```bash
# Get variety recommendations
curl -X POST "https://api.caain-soil-hub.ca/api/v1/varieties/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "crop_type": "corn",
    "location": {
      "latitude": 41.8781,
      "longitude": -87.6298
    },
    "soil_data": {
      "ph": 6.5,
      "organic_matter": 3.2,
      "soil_type": "clay_loam"
    },
    "preferences": {
      "yield_priority": "high",
      "disease_resistance": "important",
      "maturity_group": "medium"
    }
  }'
```

### 4. Regional Adaptation
Comprehensive regional suitability analysis and seasonal optimization.

**Key Endpoints:**
- `POST /api/v1/regional/adaptation` - Regional adaptation analysis
- `GET /api/v1/regional/climate-zones` - Get climate zones
- `POST /api/v1/regional/suitability` - Suitability assessment

**Example Usage:**
```bash
# Regional adaptation analysis
curl -X POST "https://api.caain-soil-hub.ca/api/v1/regional/adaptation" \
  -H "Content-Type: application/json" \
  -d '{
    "crop_id": 1,
    "location": {
      "latitude": 41.8781,
      "longitude": -87.6298
    },
    "analysis_type": "comprehensive"
  }'
```

## API Usage

### Request Format
All API requests should use JSON format with appropriate headers:

```bash
curl -X POST "https://api.caain-soil-hub.ca/api/v1/endpoint" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"key": "value"}'
```

### Response Format
All responses follow a consistent format:

```json
{
  "success": true,
  "data": {
    // Response data
  },
  "metadata": {
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0",
    "request_id": "uuid"
  },
  "errors": []
}
```

### Error Handling
The API returns appropriate HTTP status codes and error messages:

- `200 OK` - Successful request
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

**Error Response Format:**
```json
{
  "success": false,
  "data": null,
  "metadata": {
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0",
    "request_id": "uuid"
  },
  "errors": [
    {
      "code": "VALIDATION_ERROR",
      "message": "Invalid input data",
      "details": "Field 'latitude' must be between -90 and 90"
    }
  ]
}
```

### Rate Limiting
The API implements rate limiting to ensure fair usage:

- **Standard endpoints**: 60 requests per minute
- **Search endpoints**: 30 requests per minute
- **Bulk operations**: 10 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1640995200
```

## Best Practices

### 1. Data Quality
- Provide accurate location coordinates (latitude/longitude)
- Use standardized soil test results
- Include complete crop and variety information

### 2. Performance Optimization
- Use specific search criteria to reduce response time
- Cache results when appropriate
- Implement pagination for large result sets

### 3. Error Handling
- Always check response status codes
- Implement retry logic for transient errors
- Log errors for debugging purposes

### 4. Agricultural Accuracy
- Validate recommendations against local extension services
- Consider regional variations in crop performance
- Update soil and climate data regularly

## Troubleshooting

### Common Issues

#### 1. Service Unavailable
**Problem**: Service returns 503 or connection timeout
**Solution**: 
- Check service status at `/api/v1/health`
- Verify network connectivity
- Contact support if issue persists

#### 2. Invalid Location Data
**Problem**: Location-based queries return errors
**Solution**:
- Ensure coordinates are in decimal degrees format
- Verify latitude (-90 to 90) and longitude (-180 to 180) ranges
- Check for typos in location data

#### 3. No Recommendations Found
**Problem**: Variety recommendation queries return empty results
**Solution**:
- Broaden search criteria
- Check if crop is suitable for the specified location
- Verify soil and climate data accuracy

#### 4. Slow Response Times
**Problem**: API requests take longer than expected
**Solution**:
- Reduce search criteria complexity
- Use pagination for large result sets
- Check network connectivity

### Debugging Tips

1. **Enable Verbose Logging**: Include detailed request information
2. **Check Request Format**: Ensure JSON is properly formatted
3. **Validate Input Data**: Verify all required fields are present
4. **Monitor Rate Limits**: Check if you're hitting rate limits
5. **Test with Simple Queries**: Start with basic requests

### Getting Help

1. **Check Documentation**: Review API documentation at `/docs`
2. **Test Endpoints**: Use the interactive API explorer
3. **Contact Support**: Reach out to the development team
4. **Report Issues**: Submit bug reports with detailed information

## Support

### Contact Information
- **Email**: support@caain-soil-hub.ca
- **Website**: https://caain-soil-hub.ca
- **Documentation**: https://docs.caain-soil-hub.ca

### Support Hours
- **Monday - Friday**: 9:00 AM - 5:00 PM EST
- **Emergency Support**: Available for critical issues

### Reporting Issues
When reporting issues, please include:
1. **Request Details**: Method, URL, headers, body
2. **Response Information**: Status code, response body, timing
3. **Environment**: Browser, operating system, network
4. **Steps to Reproduce**: Detailed steps to recreate the issue
5. **Expected Behavior**: What should happen
6. **Actual Behavior**: What actually happens

### Feature Requests
We welcome feature requests and suggestions:
1. **Use Case**: Describe your specific use case
2. **Current Workaround**: How you currently handle this
3. **Proposed Solution**: Your suggested approach
4. **Priority**: How important this is to your work

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**License**: Agricultural Research License