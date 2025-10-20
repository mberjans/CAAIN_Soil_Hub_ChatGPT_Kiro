# Fertilizer Database Quick Start Guide

## Installation

The fertilizer database system is part of the fertilizer-strategy service. No additional dependencies are required beyond what's in `requirements.txt`.

## Quick Start

### 1. Import the Service

```python
from src.services.fertilizer_database_service import FertilizerDatabaseService
from src.models.fertilizer_database_models import (
    FertilizerProductCreate, FertilizerSearchFilters,
    FertilizerTypeEnum, NutrientReleasePattern
)
```

### 2. Create a Service Instance

```python
service = FertilizerDatabaseService()
```

### 3. Create a Fertilizer Product

```python
# Create a simple nitrogen fertilizer
urea = FertilizerProductCreate(
    product_name="Urea 46-0-0",
    manufacturer="Acme Fertilizers",
    fertilizer_type=FertilizerTypeEnum.SYNTHETIC_GRANULAR,
    nitrogen_percent=46.0,
    phosphorus_percent=0.0,
    potassium_percent=0.0,
    application_methods=["broadcast", "banded"],
    recommended_crops=["corn", "wheat", "rice"]
)

product = await service.create_fertilizer(urea)
print(f"Created product: {product.product_name} with ID: {product.product_id}")
```

### 4. Search for Fertilizers

```python
# Find high-nitrogen fertilizers suitable for corn
filters = FertilizerSearchFilters(
    min_nitrogen=40.0,
    crop_type="corn",
    limit=10
)

results = await service.search_fertilizers(filters)
print(f"Found {results.total_count} products")

for product in results.products:
    print(f"- {product.product_name} ({product.get_npk_ratio()})")
```

### 5. Get Product Classifications

```python
# Get all classifications for a product
classifications = await service.get_product_classifications(product)

print(f"Nutrient-based: {classifications['nutrient_based']}")
print(f"Source-based: {classifications['source_based']}")
print(f"Release-based: {classifications['release_based']}")
print(f"NPK Ratio: {classifications['npk_ratio']}")
```

### 6. Check Compatibility

```python
# Check if two products can be mixed
compat = await service.check_compatibility(product_id_1, product_id_2)

if compat:
    print(f"Compatibility: {compat.compatibility_level}")
    print(f"Notes: {compat.notes}")
else:
    print("No compatibility data available")
```

## Common Use Cases

### Use Case 1: Find Organic Fertilizers for Vegetables

```python
filters = FertilizerSearchFilters(
    organic_only=True,
    crop_type="vegetables",
    min_sustainability_rating=8.0
)

results = await service.search_fertilizers(filters)
```

### Use Case 2: Find Balanced Fertilizers

```python
# Find balanced NPK fertilizers (equal ratios)
filters = FertilizerSearchFilters(
    min_nitrogen=10.0,
    max_nitrogen=20.0,
    min_phosphorus=10.0,
    max_phosphorus=20.0,
    min_potassium=10.0,
    max_potassium=20.0
)

results = await service.search_fertilizers(filters)

# Filter for truly balanced
balanced = []
for product in results.products:
    if product.get_nutrient_analysis().is_balanced(tolerance=2.0):
        balanced.append(product)
```

### Use Case 3: Import Seed Data

```python
from src.data.fertilizer_seed_data import get_fertilizer_seed_data

# Get all seed data
seed_data = get_fertilizer_seed_data()

# Import first 10 products
results = await service.bulk_import_fertilizers(seed_data[:10])

print(f"Imported {results['successful']} products")
print(f"Failed: {results['failed']}")
```

### Use Case 4: Analyze Nutrient Content

```python
product = await service.get_fertilizer(product_id)

# Get detailed nutrient analysis
analysis = await service.analyze_nutrient_content(product)

print(f"NPK Ratio: {analysis['npk_ratio']}")
print(f"Total Nutrients: {analysis['total_primary_nutrients']}%")
print(f"Is Balanced: {analysis['is_balanced']}")
print(f"Classification: {analysis['nutrient_classification']}")
print(f"Has Micronutrients: {analysis['has_micronutrients']}")
```

### Use Case 5: Update Product Information

```python
from src.models.fertilizer_database_models import FertilizerProductUpdate

# Update pricing and availability
update = FertilizerProductUpdate(
    average_cost_per_unit=475.0,
    availability_score=9.0,
    manufacturer="Updated Supplier Co."
)

updated = await service.update_fertilizer(product_id, update)
```

## Classification System

### Nutrient-Based Classifications
- `nitrogen_only` - Only contains nitrogen
- `phosphorus_only` - Only contains phosphorus
- `potassium_only` - Only contains potassium
- `high_nitrogen` - Nitrogen is the dominant nutrient
- `high_phosphorus` - Phosphorus is the dominant nutrient
- `high_potassium` - Potassium is the dominant nutrient
- `balanced` - NPK in equal proportions (within tolerance)
- `micronutrient_focused` - Primary focus on micronutrients
- `secondary_nutrient_focused` - High in S, Ca, or Mg
- `specialty` - Other specialized products

### Source-Based Classifications
- `organic_animal` - From animal sources (manure, bone meal, etc.)
- `organic_plant` - From plant sources (kelp, alfalfa, etc.)
- `organic_liquid` - Liquid organic fertilizers
- `synthetic_granular` - Granular synthetic fertilizers
- `synthetic_liquid` - Liquid synthetic fertilizers
- `synthetic_controlled_release` - Coated or slow-release synthetic
- `mineral_based` - Mineral-derived fertilizers

### Release-Based Classifications
- `immediate_release` - Nutrients available immediately
- `slow_release` - Gradual release over weeks/months
- `controlled_release` - Release triggered by temperature/moisture
- `stabilized` - Stabilized to prevent losses

### Application-Based Classifications
- `broadcast_application` - Suitable for broadcasting
- `banded_application` - Suitable for band application
- `foliar_application` - Can be applied to leaves
- `fertigation_application` - Can be used in irrigation
- `injection_application` - Injectable into soil
- `starter_application` - Suitable for seed placement
- `topdress_application` - For side-dress/top-dress

## Search Filters Reference

```python
FertilizerSearchFilters(
    fertilizer_types: List[FertilizerTypeEnum] = None,  # Filter by type
    min_nitrogen: float = None,                          # Min N%
    max_nitrogen: float = None,                          # Max N%
    min_phosphorus: float = None,                        # Min P%
    max_phosphorus: float = None,                        # Max P%
    min_potassium: float = None,                         # Min K%
    max_potassium: float = None,                         # Max K%
    organic_only: bool = None,                           # Only organic certified
    crop_type: str = None,                               # Recommended for crop
    application_method: str = None,                      # Has application method
    release_pattern: NutrientReleasePattern = None,      # Release pattern
    min_sustainability_rating: float = None,             # Min sustainability (0-10)
    manufacturer: str = None,                            # Manufacturer name
    is_active: bool = True,                              # Active products only
    limit: int = 100,                                    # Results per page
    offset: int = 0                                      # Pagination offset
)
```

## Fertilizer Types Reference

```python
FertilizerTypeEnum.ORGANIC_SOLID           # Solid organic fertilizers
FertilizerTypeEnum.ORGANIC_LIQUID          # Liquid organic fertilizers
FertilizerTypeEnum.SYNTHETIC_GRANULAR      # Granular synthetic fertilizers
FertilizerTypeEnum.SYNTHETIC_LIQUID        # Liquid synthetic fertilizers
FertilizerTypeEnum.SLOW_RELEASE_COATED     # Polymer-coated slow release
FertilizerTypeEnum.SLOW_RELEASE_MATRIX     # Matrix slow release (e.g., IBDU)
FertilizerTypeEnum.SPECIALTY_MICRONUTRIENT # Micronutrient products
FertilizerTypeEnum.BIO_STIMULANT          # Bio-stimulants and inoculants
FertilizerTypeEnum.CUSTOM_BLEND           # Custom blends
```

## Testing

Run the comprehensive test suite:

```bash
cd /path/to/fertilizer-strategy
source venv/bin/activate
python -m pytest src/tests/test_fertilizer_database_service.py -v
```

Expected output:
```
37 passed in 0.24s
```

## Database Setup

The system works with or without a database:

### With PostgreSQL Database

1. Set DATABASE_URL in `.env`:
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fertilizer_strategy
```

2. Run the schema migration:
```bash
psql -U user -d fertilizer_strategy -f src/database/fertilizer_database_schema.sql
```

### Without Database (In-Memory Mode)

The service automatically falls back to in-memory storage if no database is available. This is perfect for:
- Testing
- Development
- Prototyping

## Troubleshooting

### Database Connection Issues

If you see "Database not initialized" warnings, the service is using in-memory storage. To fix:

1. Check your DATABASE_URL environment variable
2. Ensure PostgreSQL is running
3. Verify database credentials
4. Run the schema migration script

### Import Errors

Make sure you're importing from the correct paths:

```python
# Correct
from src.services.fertilizer_database_service import FertilizerDatabaseService

# Not
from fertilizer_database_service import FertilizerDatabaseService
```

### Async/Await Issues

All service methods are async and must be awaited:

```python
# Correct
product = await service.get_fertilizer(product_id)

# Wrong
product = service.get_fertilizer(product_id)  # Returns coroutine, not product
```

## Best Practices

1. **Use Type Hints**: Take advantage of the comprehensive type system
2. **Validate Input**: Pydantic models handle validation automatically
3. **Handle None**: Many fields are optional, always check for None
4. **Use Search Filters**: More efficient than getting all and filtering in Python
5. **Batch Operations**: Use `bulk_import_fertilizers` for multiple products
6. **Check Compatibility**: Always verify before recommending tank mixes
7. **Cache Results**: Store frequently accessed products in memory

## Additional Resources

- Full implementation summary: `FERTILIZER_DATABASE_IMPLEMENTATION_SUMMARY.md`
- Database schema: `src/database/fertilizer_database_schema.sql`
- Seed data: `src/data/fertilizer_seed_data.py`
- Test suite: `src/tests/test_fertilizer_database_service.py`

## Support

For issues or questions:
1. Check the test suite for examples
2. Review the implementation summary
3. Examine the seed data for realistic examples
4. Contact the development team

---
**Version:** 1.0
**Last Updated:** 2025-10-20
