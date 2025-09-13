# AFAS Database Setup
# Autonomous Farm Advisory System
**Version:** 1.0  
**Date:** December 2024

## Overview

This directory contains the complete database schema design and setup for the Autonomous Farm Advisory System (AFAS). The system uses a multi-database architecture optimized for agricultural data management:

- **PostgreSQL**: Structured relational data (users, farms, soil tests, recommendations)
- **MongoDB**: Document storage (flexible schemas, external data cache, AI responses)
- **Redis**: Caching and session management (user sessions, API responses, real-time data)

## Quick Start

### 1. Automated Setup (Recommended)

```bash
# Run the automated setup script
./setup-databases.sh

# This will:
# - Install database software (if needed)
# - Start database services
# - Create databases and schemas
# - Generate environment configuration
# - Test all connections
```

### 2. Manual Setup

If you prefer manual setup or the automated script doesn't work for your system:

#### Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install databases manually:
# - PostgreSQL 15+ with PostGIS extension
# - MongoDB 7.0+
# - Redis 7.0+
```

#### Setup PostgreSQL
```bash
# Create database and user
createuser -s afas_user
createdb afas_db -O afas_user
psql -d afas_db -c "ALTER USER afas_user PASSWORD 'afas_password_2024';"

# Run schema
psql -h localhost -U afas_user -d afas_db -f postgresql/schema.sql
```

#### Setup MongoDB
```bash
# Run MongoDB schema
mongosh afas_db mongodb/schema.js
```

#### Setup Redis
```bash
# Copy configuration (optional)
cp redis/redis.conf /etc/redis/redis.conf

# Start Redis with configuration
redis-server redis/redis.conf
```

### 3. Test Setup

```bash
# Test all database connections
python test_databases.py

# Or test individual components
python -c "from python.database_config import get_database_manager; print(get_database_manager().test_all_connections())"
```

## Database Architecture

### PostgreSQL Schema

The PostgreSQL database contains structured agricultural data organized into logical groups:

#### Core Tables
- **users**: Farmer accounts and authentication
- **farms**: Farm profiles and locations
- **fields**: Individual field management
- **soil_tests**: Soil analysis results
- **crops**: Crop types and varieties
- **crop_history**: Rotation and yield tracking
- **fertilizer_products**: Fertilizer database
- **fertilizer_applications**: Application records
- **recommendations**: AI-generated advice
- **equipment**: Farm equipment inventory
- **weather_data**: Weather observations

#### Key Features
- **PostGIS Integration**: Geographic data for precision agriculture
- **JSONB Support**: Flexible data storage within structured tables
- **Full-text Search**: Efficient searching of agricultural content
- **Audit Trails**: Automatic timestamp tracking
- **Data Validation**: Comprehensive check constraints

### MongoDB Collections

MongoDB stores flexible document data and external API responses:

#### Collections
- **question_responses**: Complete Q&A interactions
- **external_data_cache**: Cached API responses
- **agricultural_knowledge**: Expert knowledge base
- **image_analysis**: Crop image analysis results
- **conversation_history**: AI conversation tracking
- **system_analytics**: Usage and performance metrics

#### Features
- **Schema Validation**: JSON schema enforcement
- **Flexible Documents**: Varying data structures
- **Text Search**: Full-text search capabilities
- **Geospatial Queries**: Location-based data retrieval
- **Aggregation Pipeline**: Complex data analysis

### Redis Data Structures

Redis provides high-performance caching and session management:

#### Database Allocation
- **DB 0**: User sessions and authentication
- **DB 1**: API response caching
- **DB 2**: Real-time data and notifications
- **DB 3**: Rate limiting and throttling
- **DB 4**: Background job queues
- **DB 5**: Agricultural data caching
- **DB 6**: Image analysis temporary data
- **DB 7**: Conversation state management

#### Key Patterns
- **Session Management**: User authentication and state
- **API Caching**: External data source responses
- **Rate Limiting**: Request throttling and quotas
- **Real-time Updates**: Live notifications and progress
- **Temporary Storage**: Processing intermediate data

## Configuration

### Environment Variables

The setup script creates `.env.database` with all necessary configuration:

```bash
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=afas_db
POSTGRES_USER=afas_user
POSTGRES_PASSWORD=afas_password_2024

# MongoDB
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=afas_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Connection Pools
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
```

### Python Integration

Use the provided database manager for easy integration:

```python
from databases.python.database_config import get_database_manager
from databases.python.models import User, Farm, SoilTest

# Get database manager
db = get_database_manager()

# PostgreSQL operations
with db.postgres.get_session() as session:
    user = session.query(User).filter(User.email == "farmer@example.com").first()

# MongoDB operations
collection = db.mongodb.get_collection('question_responses')
responses = collection.find({'user_id': user.user_id})

# Redis operations
cache = db.redis.get_cache_client()
cache.set('weather:data', weather_json, ex=3600)
```

## Data Models

### Agricultural Data Models

The system includes comprehensive agricultural data models:

#### Soil Management
```python
# Soil test with validation
soil_test = SoilTest(
    field_id=field.field_id,
    test_date=date.today(),
    ph=6.2,
    organic_matter_percent=3.8,
    phosphorus_ppm=25,
    potassium_ppm=180
)
```

#### Crop Management
```python
# Crop history tracking
crop_history = CropHistory(
    field_id=field.field_id,
    crop_year=2024,
    crop_id=corn.crop_id,
    actual_yield=185.5,
    planting_date=date(2024, 5, 1),
    harvest_date=date(2024, 10, 15)
)
```

#### Recommendation System
```python
# AI recommendation storage
recommendation = Recommendation(
    user_id=user.user_id,
    farm_id=farm.farm_id,
    question_id=1,  # Crop selection
    request_data={'soil_ph': 6.2, 'location': {...}},
    recommendations=[{...}],
    overall_confidence=0.87
)
```

## Performance Optimization

### Database Indexes

The schema includes comprehensive indexing:

#### PostgreSQL Indexes
- **Spatial Indexes**: PostGIS GIST indexes for location queries
- **Composite Indexes**: Multi-column indexes for common queries
- **Partial Indexes**: Conditional indexes for filtered queries
- **Text Search**: Full-text search indexes with trigram support

#### MongoDB Indexes
- **Compound Indexes**: Multi-field indexes for complex queries
- **Text Indexes**: Full-text search across multiple fields
- **Geospatial Indexes**: 2dsphere indexes for location queries
- **TTL Indexes**: Automatic document expiration

#### Redis Optimization
- **Connection Pooling**: Efficient connection management
- **Pipeline Operations**: Batch operations for better performance
- **Memory Optimization**: Appropriate data structure selection
- **Expiration Policies**: Automatic cleanup of stale data

### Query Optimization

#### Best Practices
- Use prepared statements for repeated queries
- Implement proper connection pooling
- Cache frequently accessed data in Redis
- Use database-specific optimizations (EXPLAIN, profiling)
- Monitor query performance and optimize slow queries

## Security

### Data Protection
- **Encryption at Rest**: Sensitive farm data encryption
- **Connection Security**: TLS/SSL for all connections
- **Access Control**: Role-based permissions
- **Input Validation**: Comprehensive data validation
- **Audit Logging**: Security event tracking

### Authentication
- **Password Hashing**: Secure password storage
- **Session Management**: Secure session handling
- **Token Validation**: JWT token verification
- **Rate Limiting**: Brute force protection

## Monitoring and Maintenance

### Health Checks
```python
# Test all database connections
results = db.test_all_connections()
print(f"PostgreSQL: {'✅' if results['postgresql'] else '❌'}")
print(f"MongoDB: {'✅' if results['mongodb'] else '❌'}")
print(f"Redis: {'✅' if results['redis'] else '❌'}")
```

### Backup Strategies
- **PostgreSQL**: Regular pg_dump backups
- **MongoDB**: mongodump with compression
- **Redis**: RDB snapshots and AOF logs

### Performance Monitoring
- **Connection Pool Metrics**: Monitor pool utilization
- **Query Performance**: Track slow queries
- **Cache Hit Rates**: Monitor Redis cache effectiveness
- **Storage Usage**: Track database growth

## Troubleshooting

### Common Issues

#### Connection Problems
```bash
# Test individual connections
psql -h localhost -U afas_user -d afas_db -c "SELECT version();"
mongosh --host localhost:27017 --eval "db.adminCommand('ping')"
redis-cli -h localhost -p 6379 ping
```

#### Permission Issues
```bash
# Fix PostgreSQL permissions
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE afas_db TO afas_user;"

# Fix file permissions
chmod 600 .env.database
```

#### Performance Issues
```sql
-- Check PostgreSQL performance
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 10;
```

### Log Locations
- **PostgreSQL**: Check PostgreSQL log directory
- **MongoDB**: `/var/log/mongodb/mongod.log`
- **Redis**: `redis-server.log` (in Redis directory)

## Development

### Adding New Models

1. **Define SQLAlchemy Model**:
```python
class NewModel(Base):
    __tablename__ = 'new_table'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # ... other fields
```

2. **Create Migration**:
```bash
alembic revision --autogenerate -m "Add new model"
alembic upgrade head
```

3. **Update MongoDB Schema** (if needed):
```javascript
db.createCollection("new_collection", {
    validator: { /* validation rules */ }
});
```

### Testing

Run the comprehensive test suite:
```bash
# Full test suite
python test_databases.py

# Individual tests
python -m pytest tests/test_postgresql.py
python -m pytest tests/test_mongodb.py
python -m pytest tests/test_redis.py
```

## Support

### Documentation
- **PostgreSQL**: https://www.postgresql.org/docs/
- **MongoDB**: https://docs.mongodb.com/
- **Redis**: https://redis.io/documentation
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **PostGIS**: https://postgis.net/documentation/

### Getting Help
1. Check the test output for specific error messages
2. Review the logs in each database system
3. Verify environment configuration
4. Ensure all dependencies are installed
5. Check network connectivity and firewall settings

---

**Happy Farming! 🌾**

The AFAS database system is designed to grow with your agricultural data needs while maintaining performance, security, and reliability.