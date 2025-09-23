# Farm Location Input Database Schema

This document describes the database schema and models for the Farm Location Input feature of the Autonomous Farm Advisory System (AFAS).

## Overview

The Farm Location Input feature allows farmers to specify their farm and field locations through multiple methods:
- GPS coordinates input
- Address input with geocoding
- Interactive map selection
- Current location detection

## Database Tables

### farm_locations

Stores farm location data for the location input feature.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique location identifier |
| user_id | UUID | NOT NULL, FK to users | User who owns this location |
| name | VARCHAR(100) | NOT NULL | Location name |
| latitude | DECIMAL(10,8) | NOT NULL, -90 to 90 | Latitude in decimal degrees |
| longitude | DECIMAL(11,8) | NOT NULL, -180 to 180 | Longitude in decimal degrees |
| address | TEXT | | Street address |
| county | VARCHAR(100) | | County name |
| state | VARCHAR(50) | | State name |
| climate_zone | VARCHAR(20) | | Climate zone |
| source | VARCHAR(20) | NOT NULL | How location was input (gps, address, map, current) |
| verified | BOOLEAN | DEFAULT FALSE | Whether location has been verified |
| accuracy_meters | INTEGER | | GPS accuracy in meters |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `idx_farm_locations_user_id` on `user_id`
- `idx_farm_locations_coordinates` on `latitude, longitude`
- `idx_farm_locations_state_county` on `state, county`
- `idx_farm_locations_source` on `source`
- `idx_farm_locations_verified` on `verified`

### farm_fields

Stores individual fields within a farm location.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique field identifier |
| location_id | UUID | NOT NULL, FK to farm_locations | Associated farm location |
| field_name | VARCHAR(100) | NOT NULL | Field name |
| field_type | VARCHAR(20) | DEFAULT 'crop' | Type of field (crop, pasture, other) |
| size_acres | DECIMAL(10,2) | | Field size in acres |
| soil_type | VARCHAR(50) | | Soil type |
| notes | TEXT | | Additional notes |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `idx_farm_fields_location_id` on `location_id`
- `idx_farm_fields_type` on `field_type`

### geocoding_cache

Caches geocoding API results to improve performance and reduce API calls.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique cache entry identifier |
| query_hash | VARCHAR(64) | UNIQUE, NOT NULL | SHA-256 hash of the geocoding query |
| query_text | TEXT | NOT NULL | Original query text |
| result_json | JSONB | NOT NULL | Geocoding result as JSON |
| provider | VARCHAR(50) | NOT NULL | Geocoding provider used |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Creation timestamp |
| expires_at | TIMESTAMP WITH TIME ZONE | NOT NULL | Expiration timestamp |

**Indexes:**
- `idx_geocoding_cache_hash` on `query_hash`
- `idx_geocoding_cache_expires` on `expires_at`
- `idx_geocoding_cache_provider` on `provider`

## Pydantic Models

### Core Models

#### FarmLocationBase
Base model for farm location data with validation:
- Validates latitude/longitude ranges
- Sanitizes input to prevent XSS attacks
- Enforces required fields

#### FarmLocationCreate
Model for creating new farm locations:
```python
{
    "name": "North Field",
    "latitude": 42.0308,
    "longitude": -93.6319,
    "address": "123 Farm Road, Ames, IA",
    "source": "gps"
}
```

#### FarmLocation
Complete farm location model with all fields including timestamps and computed fields.

#### FarmFieldBase
Base model for farm field data with validation:
- Validates field names and types
- Ensures positive acreage values
- Sanitizes text inputs

#### FarmFieldCreate
Model for creating new farm fields:
```python
{
    "location_id": "uuid-string",
    "field_name": "Corn Field A",
    "field_type": "crop",
    "size_acres": 80.5,
    "soil_type": "silt loam"
}
```

### Validation Models

#### ValidationResult
Result of location validation:
```python
{
    "valid": true,
    "warnings": ["Location may be in non-agricultural area"],
    "errors": [],
    "geographic_info": {
        "county": "Story County",
        "state": "Iowa",
        "climate_zone": "5a",
        "is_agricultural": true
    }
}
```

#### GeocodingRequest/Result
Models for geocoding operations:
```python
# Request
{
    "address": "123 Main St, Ames, IA"
}

# Result
{
    "latitude": 42.0308,
    "longitude": -93.6319,
    "address": "123 Main St, Ames, IA 50010",
    "confidence": 0.95,
    "provider": "nominatim"
}
```

## Security Features

### Input Validation
- All text inputs are sanitized to prevent XSS attacks
- Coordinate ranges are strictly validated
- Field lengths are enforced to prevent buffer overflow attacks

### Data Protection
- Location data is considered sensitive and should be encrypted at rest
- Access controls ensure users can only access their own location data
- Audit logging tracks all location data access

### Privacy Considerations
- Exact coordinates can reveal sensitive farm information
- Consider rounding coordinates for privacy when sharing data
- Implement data retention policies for location data

## Migration Scripts

### Creating Tables
```bash
python databases/migrations/run_migration.py --database-url "postgresql://user:pass@host/db" --action create
```

### Checking Tables
```bash
python databases/migrations/run_migration.py --database-url "postgresql://user:pass@host/db" --action check
```

### Validating Schema
```bash
python databases/migrations/run_migration.py --database-url "postgresql://user:pass@host/db" --action validate
```

### Rolling Back (WARNING: Deletes all data)
```bash
python databases/migrations/run_migration.py --database-url "postgresql://user:pass@host/db" --action rollback
```

## Testing

Run the test suite to validate models and schema:
```bash
python databases/test_location_models.py
```

Or with pytest:
```bash
pytest databases/test_location_models.py -v
```

## Usage Examples

### Creating a Farm Location
```python
from databases.python.location_models import FarmLocationCreate

location = FarmLocationCreate(
    name="Main Farm",
    latitude=42.0308,
    longitude=-93.6319,
    address="123 Farm Road, Ames, IA",
    source="gps"
)
```

### Adding Fields to a Location
```python
from databases.python.location_models import FarmFieldCreate

field = FarmFieldCreate(
    location_id="location-uuid",
    field_name="North Corn Field",
    field_type="crop",
    size_acres=160.0,
    soil_type="silt loam"
)
```

### Validating Location Data
```python
from databases.python.location_models import LocationValidationRequest

validation_request = LocationValidationRequest(
    latitude=42.0308,
    longitude=-93.6319
)
```

## Performance Considerations

### Indexing Strategy
- Coordinate-based queries are optimized with composite indexes
- User-based queries use single-column indexes
- Geographic queries can be enhanced with PostGIS spatial indexes

### Caching Strategy
- Geocoding results are cached to reduce API calls
- Cache expiration prevents stale data
- Query hashing ensures cache consistency

### Query Optimization
- Use prepared statements for repeated queries
- Limit result sets with pagination
- Consider read replicas for heavy read workloads

## Agricultural Context

### Location Accuracy Requirements
- GPS accuracy within 10 meters is preferred for field-level recommendations
- County-level accuracy is sufficient for general climate recommendations
- State-level accuracy is minimum for basic crop suitability

### Agricultural Area Validation
- Locations should be validated against known agricultural regions
- Non-agricultural areas should trigger warnings
- Ocean or urban coordinates should be flagged as potentially invalid

### Regional Considerations
- Climate zones affect crop recommendations
- County boundaries determine local regulations
- State boundaries affect agricultural extension resources

## Future Enhancements

### Planned Features
- Field boundary polygon support using PostGIS
- Integration with USDA soil survey data
- Automatic climate zone detection
- Precision agriculture zone management

### Scalability Improvements
- Partitioning by geographic region
- Spatial indexing with PostGIS
- Caching layer for frequently accessed locations
- API rate limiting for geocoding services

## Troubleshooting

### Common Issues
1. **Invalid coordinates**: Check latitude/longitude ranges
2. **Geocoding failures**: Verify address format and API availability
3. **Permission errors**: Ensure user has access to location data
4. **Cache misses**: Check cache expiration and query hashing

### Debugging Tips
- Enable SQL query logging for performance analysis
- Monitor geocoding API usage and rate limits
- Validate input data before database operations
- Use database constraints to catch data integrity issues