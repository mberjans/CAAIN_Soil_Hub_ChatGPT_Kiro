# Enhanced Geocoding API Endpoints

## Overview

The Enhanced Geocoding API provides address-to-coordinates conversion and reverse geocoding with comprehensive agricultural context data integration. This service enhances standard geocoding results with USDA zones, climate zones, soil survey areas, and agricultural district information to support agricultural planning and decision-making.

## Base URL

```
http://localhost:8004/api/v1/validation
```

## Authentication

All endpoints require authentication. Include your API key in the request headers:

```
Authorization: Bearer <your-api-key>
```

## Endpoints

### 1. Geocode Address with Agricultural Context

Convert a street address to GPS coordinates with optional agricultural context enhancement.

**Endpoint:** `POST /geocode`

**Parameters:**
- `address` (string, required): Street address to geocode (e.g., "123 Main St, Ames, IA")
- `include_agricultural_context` (boolean, optional): Include agricultural context data (default: true)

**Request Example:**
```bash
curl -X POST "http://localhost:8004/api/v1/validation/geocode?address=123%20Main%20St%2C%20Ames%2C%20IA&include_agricultural_context=true" \
  -H "Authorization: Bearer <your-api-key>"
```

**Response Example:**
```json
{
  "latitude": 42.0308,
  "longitude": -93.6319,
  "address": "123 Main St, Ames, IA",
  "display_name": "123 Main St, Ames, Story County, Iowa, USA",
  "confidence": 0.95,
  "provider": "nominatim",
  "components": {
    "house_number": "123",
    "road": "Main St",
    "city": "Ames",
    "county": "Story",
    "state": "Iowa",
    "country": "USA"
  },
  "agricultural_context": {
    "usda_zone": "5a",
    "climate_zone": "Dfa",
    "soil_survey_area": "Story County",
    "agricultural_district": "Corn Belt",
    "county": "Story",
    "state": "Iowa",
    "elevation_meters": 300,
    "growing_season_days": 180,
    "frost_free_days": 160,
    "agricultural_suitability": "Good"
  }
}
```

**Agricultural Context Fields:**
- `usda_zone`: USDA Plant Hardiness Zone (e.g., "5a", "6b")
- `climate_zone`: Köppen climate classification (e.g., "Dfa", "Cfb")
- `soil_survey_area`: USDA Soil Survey Area name
- `agricultural_district`: Major agricultural region (e.g., "Corn Belt", "Wheat Belt")
- `county`: County name
- `state`: State or province
- `elevation_meters`: Elevation above sea level in meters
- `growing_season_days`: Typical growing season length in days
- `frost_free_days`: Average frost-free days per year
- `agricultural_suitability`: Agricultural suitability rating (Excellent, Good, Moderate, Challenging, Difficult)

### 2. Reverse Geocode with Agricultural Context

Convert GPS coordinates to a street address with optional agricultural context enhancement.

**Endpoint:** `POST /reverse-geocode`

**Parameters:**
- `latitude` (float, required): Latitude in decimal degrees (-90 to 90)
- `longitude` (float, required): Longitude in decimal degrees (-180 to 180)
- `include_agricultural_context` (boolean, optional): Include agricultural context data (default: true)

**Request Example:**
```bash
curl -X POST "http://localhost:8004/api/v1/validation/reverse-geocode?latitude=42.0308&longitude=-93.6319&include_agricultural_context=true" \
  -H "Authorization: Bearer <your-api-key>"
```

**Response Example:**
```json
{
  "address": "123 Main St, Ames, IA",
  "display_name": "123 Main St, Ames, Story County, Iowa, USA",
  "components": {
    "house_number": "123",
    "road": "Main St",
    "city": "Ames",
    "county": "Story",
    "state": "Iowa",
    "country": "USA"
  },
  "confidence": 0.95,
  "provider": "nominatim",
  "agricultural_context": {
    "usda_zone": "5a",
    "climate_zone": "Dfa",
    "soil_survey_area": "Story County",
    "agricultural_district": "Corn Belt",
    "county": "Story",
    "state": "Iowa",
    "elevation_meters": 300,
    "growing_season_days": 180,
    "frost_free_days": 160,
    "agricultural_suitability": "Good"
  }
}
```

### 3. Batch Geocode Addresses

Geocode multiple addresses concurrently with agricultural context enhancement.

**Endpoint:** `POST /batch-geocode`

**Request Body:**
```json
{
  "addresses": [
    "123 Main St, Ames, IA",
    "456 Oak Ave, Des Moines, IA",
    "789 Pine Rd, Cedar Rapids, IA"
  ],
  "include_agricultural_context": true
}
```

**Request Example:**
```bash
curl -X POST "http://localhost:8004/api/v1/validation/batch-geocode" \
  -H "Authorization: Bearer <your-api-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      "123 Main St, Ames, IA",
      "456 Oak Ave, Des Moines, IA",
      "789 Pine Rd, Cedar Rapids, IA"
    ],
    "include_agricultural_context": true
  }'
```

**Response Example:**
```json
{
  "results": [
    {
      "latitude": 42.0308,
      "longitude": -93.6319,
      "address": "123 Main St, Ames, IA",
      "display_name": "123 Main St, Ames, Story County, Iowa, USA",
      "confidence": 0.95,
      "provider": "nominatim",
      "components": {
        "house_number": "123",
        "road": "Main St",
        "city": "Ames",
        "county": "Story",
        "state": "Iowa",
        "country": "USA"
      },
      "agricultural_context": {
        "usda_zone": "5a",
        "climate_zone": "Dfa",
        "soil_survey_area": "Story County",
        "agricultural_district": "Corn Belt",
        "county": "Story",
        "state": "Iowa",
        "elevation_meters": 300,
        "growing_season_days": 180,
        "frost_free_days": 160,
        "agricultural_suitability": "Good"
      }
    },
    {
      "latitude": 41.5868,
      "longitude": -93.6250,
      "address": "456 Oak Ave, Des Moines, IA",
      "display_name": "456 Oak Ave, Des Moines, Polk County, Iowa, USA",
      "confidence": 0.92,
      "provider": "nominatim",
      "components": {
        "house_number": "456",
        "road": "Oak Ave",
        "city": "Des Moines",
        "county": "Polk",
        "state": "Iowa",
        "country": "USA"
      },
      "agricultural_context": {
        "usda_zone": "5a",
        "climate_zone": "Dfa",
        "soil_survey_area": "Polk County",
        "agricultural_district": "Corn Belt",
        "county": "Polk",
        "state": "Iowa",
        "elevation_meters": 280,
        "growing_season_days": 175,
        "frost_free_days": 155,
        "agricultural_suitability": "Good"
      }
    },
    {
      "latitude": 41.9778,
      "longitude": -91.6656,
      "address": "789 Pine Rd, Cedar Rapids, IA",
      "display_name": "789 Pine Rd, Cedar Rapids, Linn County, Iowa, USA",
      "confidence": 0.88,
      "provider": "nominatim",
      "components": {
        "house_number": "789",
        "road": "Pine Rd",
        "city": "Cedar Rapids",
        "county": "Linn",
        "state": "Iowa",
        "country": "USA"
      },
      "agricultural_context": {
        "usda_zone": "5a",
        "climate_zone": "Dfa",
        "soil_survey_area": "Linn County",
        "agricultural_district": "Corn Belt",
        "county": "Linn",
        "state": "Iowa",
        "elevation_meters": 260,
        "growing_season_days": 170,
        "frost_free_days": 150,
        "agricultural_suitability": "Good"
      }
    }
  ],
  "failed_addresses": [],
  "processing_time_ms": 1250.5,
  "success_count": 3,
  "failure_count": 0
}
```

**Batch Response Fields:**
- `results`: Array of successful geocoding results
- `failed_addresses`: Array of addresses that failed to geocode
- `processing_time_ms`: Total processing time in milliseconds
- `success_count`: Number of successfully geocoded addresses
- `failure_count`: Number of failed geocoding attempts

### 4. Address Suggestions (Autocomplete)

Get address autocomplete suggestions for user input.

**Endpoint:** `GET /address-suggestions`

**Parameters:**
- `query` (string, required): Partial address query (minimum 3 characters)
- `limit` (integer, optional): Maximum number of suggestions to return (default: 5, max: 10)

**Request Example:**
```bash
curl -X GET "http://localhost:8004/api/v1/validation/address-suggestions?query=Ames&limit=5" \
  -H "Authorization: Bearer <your-api-key>"
```

**Response Example:**
```json
{
  "suggestions": [
    {
      "display_name": "Ames, Story County, Iowa, USA",
      "address": "Ames, Iowa",
      "latitude": 42.0308,
      "longitude": -93.6319,
      "relevance": 1.0,
      "components": {
        "city": "Ames",
        "county": "Story",
        "state": "Iowa",
        "country": "USA"
      }
    },
    {
      "display_name": "Ames, Montgomery County, Texas, USA",
      "address": "Ames, Texas",
      "latitude": 30.0535,
      "longitude": -95.9903,
      "relevance": 0.9,
      "components": {
        "city": "Ames",
        "county": "Montgomery",
        "state": "Texas",
        "country": "USA"
      }
    }
  ],
  "query": "Ames",
  "total_suggestions": 2
}
```

## Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
  "detail": {
    "error": {
      "error_code": "INVALID_COORDINATES",
      "error_message": "Invalid latitude: 200.0. Must be between -90 and 90",
      "agricultural_context": "Valid coordinates are required for agricultural planning",
      "suggested_actions": [
        "Check coordinate values",
        "Ensure latitude is between -90 and 90",
        "Ensure longitude is between -180 and 180"
      ]
    }
  }
}
```

**422 Unprocessable Entity:**
```json
{
  "detail": {
    "error": {
      "error_code": "GEOCODING_FAILED",
      "error_message": "Unable to geocode address: Address not found",
      "agricultural_context": "Address geocoding helps ensure recommendations match your local conditions",
      "suggested_actions": [
        "Try a more specific address (include street number)",
        "Use GPS coordinates instead",
        "Select location using the interactive map"
      ]
    },
    "provider": "nominatim"
  }
}
```

**500 Internal Server Error:**
```json
{
  "detail": {
    "error": {
      "error_code": "GEOCODING_SERVICE_ERROR",
      "error_message": "Internal geocoding service error",
      "agricultural_context": "Unable to convert address to coordinates for location-based recommendations",
      "suggested_actions": [
        "Try again in a few moments",
        "Use GPS coordinates directly",
        "Contact support if the problem persists"
      ]
    }
  }
}
```

### Batch Geocoding Errors

**Empty Address List:**
```json
{
  "detail": {
    "error": {
      "error_code": "EMPTY_ADDRESS_LIST",
      "error_message": "Address list cannot be empty",
      "agricultural_context": "At least one address is required for batch geocoding",
      "suggested_actions": [
        "Provide at least one address",
        "Check address format",
        "Ensure addresses are valid"
      ]
    }
  }
}
```

**Too Many Addresses:**
```json
{
  "detail": {
    "error": {
      "error_code": "TOO_MANY_ADDRESSES",
      "error_message": "Maximum 100 addresses allowed per batch request",
      "agricultural_context": "Large batches may impact performance and agricultural data accuracy",
      "suggested_actions": [
        "Split into smaller batches",
        "Use individual geocoding for critical addresses",
        "Contact support for bulk processing"
      ]
    }
  }
}
```

## Performance Requirements

- **Single Address Geocoding**: < 1 second response time
- **Batch Geocoding**: < 3 seconds for up to 100 addresses
- **Address Suggestions**: < 500ms response time
- **Agricultural Context Enhancement**: < 2 seconds additional processing time

## Rate Limits

- **Single Address**: 100 requests per minute per API key
- **Batch Geocoding**: 10 requests per minute per API key
- **Address Suggestions**: 200 requests per minute per API key

## Caching

All geocoding results are cached for 24 hours to improve performance and reduce external API calls. Agricultural context data is cached separately with the same TTL.

## Agricultural Context Data Sources

The agricultural context enhancement integrates with multiple data sources:

1. **USDA Plant Hardiness Zones**: Official USDA hardiness zone data
2. **Köppen Climate Classification**: Global climate classification system
3. **USDA Soil Survey**: Soil survey area and soil type information
4. **Agricultural Districts**: Major agricultural regions (Corn Belt, Wheat Belt, etc.)

## Use Cases

### Farm Location Setup
```bash
# Geocode farm address with full agricultural context
curl -X POST "http://localhost:8004/api/v1/validation/geocode?address=1234%20Farm%20Rd%2C%20Ames%2C%20IA&include_agricultural_context=true"
```

### Field Boundary Management
```bash
# Reverse geocode field center coordinates
curl -X POST "http://localhost:8004/api/v1/validation/reverse-geocode?latitude=42.0308&longitude=-93.6319&include_agricultural_context=true"
```

### Bulk Farm Data Import
```bash
# Batch geocode multiple farm locations
curl -X POST "http://localhost:8004/api/v1/validation/batch-geocode" \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      "1234 Farm Rd, Ames, IA",
      "5678 Ranch Way, Des Moines, IA",
      "9012 Field St, Cedar Rapids, IA"
    ],
    "include_agricultural_context": true
  }'
```

### Address Autocomplete for Forms
```bash
# Get address suggestions for user input
curl -X GET "http://localhost:8004/api/v1/validation/address-suggestions?query=1234%20Farm&limit=5"
```

## Integration Examples

### JavaScript/Node.js
```javascript
const axios = require('axios');

async function geocodeWithAgriculturalContext(address) {
  try {
    const response = await axios.post(
      'http://localhost:8004/api/v1/validation/geocode',
      null,
      {
        params: {
          address: address,
          include_agricultural_context: true
        },
        headers: {
          'Authorization': 'Bearer <your-api-key>'
        }
      }
    );
    
    return response.data;
  } catch (error) {
    console.error('Geocoding error:', error.response.data);
    throw error;
  }
}

// Usage
geocodeWithAgriculturalContext('123 Main St, Ames, IA')
  .then(result => {
    console.log('Coordinates:', result.latitude, result.longitude);
    console.log('USDA Zone:', result.agricultural_context.usda_zone);
    console.log('Agricultural District:', result.agricultural_context.agricultural_district);
  })
  .catch(error => {
    console.error('Error:', error.message);
  });
```

### Python
```python
import requests

def geocode_with_agricultural_context(address, api_key):
    url = "http://localhost:8004/api/v1/validation/geocode"
    params = {
        "address": address,
        "include_agricultural_context": True
    }
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.post(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Geocoding error: {e}")
        raise

# Usage
result = geocode_with_agricultural_context("123 Main St, Ames, IA", "your-api-key")
print(f"Coordinates: {result['latitude']}, {result['longitude']}")
print(f"USDA Zone: {result['agricultural_context']['usda_zone']}")
print(f"Agricultural District: {result['agricultural_context']['agricultural_district']}")
```

## Support

For technical support or questions about the Enhanced Geocoding API:

- **Documentation**: [API Documentation](https://docs.afas.com/api/geocoding)
- **Support Email**: api-support@afas.com
- **Status Page**: [API Status](https://status.afas.com)

## Changelog

### Version 1.1.0 (Current)
- Added agricultural context enhancement
- Added batch geocoding support
- Improved caching and performance
- Enhanced error handling with agricultural context

### Version 1.0.0
- Initial release with basic geocoding functionality
- Address suggestions (autocomplete)
- Basic error handling