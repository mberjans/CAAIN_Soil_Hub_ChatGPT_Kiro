# AFAS Redis Schema Design
# Autonomous Farm Advisory System
# Version: 1.0
# Date: December 2024

## Overview
Redis is used for caching, session management, and real-time data storage in the AFAS system. This document outlines the key patterns and data structures used.

## Database Allocation
- **Database 0**: User sessions and authentication
- **Database 1**: API response caching
- **Database 2**: Real-time data and temporary storage
- **Database 3**: Rate limiting and throttling
- **Database 4**: Background job queues
- **Database 5**: Agricultural data caching
- **Database 6**: Image analysis temporary data
- **Database 7**: Conversation state management

## Key Naming Conventions

### General Pattern
```
{service}:{data_type}:{identifier}:{optional_suffix}
```

### Examples
```
user:session:uuid-here
api:cache:weather:lat_lon_date
farm:profile:farm-uuid
recommendation:temp:request-uuid
```

## Data Structures and Use Cases

### 1. User Sessions (Database 0)
```redis
# User session data
HSET user:session:{session_id}
  user_id "uuid-here"
  email "farmer@example.com"
  role "farmer"
  farm_ids "farm1,farm2,farm3"
  created_at "2024-12-09T10:30:00Z"
  last_activity "2024-12-09T11:45:00Z"
  ip_address "192.168.1.100"
  user_agent "Mozilla/5.0..."

# Session expiration (24 hours)
EXPIRE user:session:{session_id} 86400

# Active sessions by user
SADD user:active_sessions:{user_id} {session_id}
EXPIRE user:active_sessions:{user_id} 86400

# Authentication tokens
HSET auth:token:{token_hash}
  user_id "uuid-here"
  session_id "session-uuid"
  expires_at "2024-12-10T10:30:00Z"
  
EXPIRE auth:token:{token_hash} 86400
```

### 2. API Response Caching (Database 1)
```redis
# Weather data cache
HSET api:cache:weather:{lat}_{lon}_{date}
  temperature_f "32"
  humidity "75"
  wind_speed "8"
  precipitation "0.0"
  forecast "[{...}]"
  cached_at "2024-12-09T10:30:00Z"

# Cache for 1 hour
EXPIRE api:cache:weather:{lat}_{lon}_{date} 3600

# Soil database cache
HSET api:cache:soil:{lat}_{lon}
  soil_series "Webster"
  drainage_class "somewhat_poorly_drained"
  typical_ph "6.2-7.8"
  organic_matter "3.5-4.5"
  
EXPIRE api:cache:soil:{lat}_{lon} 86400

# Crop variety cache
HSET api:cache:varieties:{crop_name}_{region}
  varieties "[{variety_data...}]"
  last_updated "2024-12-09T10:30:00Z"
  
EXPIRE api:cache:varieties:{crop_name}_{region} 7200

# Market price cache
HSET api:cache:prices:{commodity}_{date}
  price_per_bushel "4.25"
  currency "USD"
  market "CBOT"
  
EXPIRE api:cache:prices:{commodity}_{date} 1800
```

### 3. Real-time Data (Database 2)
```redis
# Current recommendation processing
HSET recommendation:processing:{request_id}
  status "processing"
  progress "45"
  stage "analyzing_soil_data"
  started_at "2024-12-09T10:30:00Z"
  estimated_completion "2024-12-09T10:32:00Z"

EXPIRE recommendation:processing:{request_id} 300

# Image analysis progress
HSET image:analysis:{analysis_id}
  status "analyzing"
  progress "75"
  stage "deficiency_detection"
  model_version "v2.1"
  
EXPIRE image:analysis:{analysis_id} 600

# Real-time notifications
LPUSH user:notifications:{user_id}
  '{"type":"recommendation_ready","message":"Your crop selection recommendation is ready","timestamp":"2024-12-09T10:32:00Z"}'
  
LTRIM user:notifications:{user_id} 0 99  # Keep last 100 notifications
EXPIRE user:notifications:{user_id} 604800  # 7 days

# WebSocket connection tracking
SADD websocket:connections:{user_id} {connection_id}
EXPIRE websocket:connections:{user_id} 3600
```

### 4. Rate Limiting (Database 3)
```redis
# API rate limiting by user
INCR rate_limit:api:{user_id}:{hour}
EXPIRE rate_limit:api:{user_id}:{hour} 3600

# Rate limiting by IP
INCR rate_limit:ip:{ip_address}:{minute}
EXPIRE rate_limit:ip:{ip_address}:{minute} 60

# Recommendation request limits
INCR rate_limit:recommendations:{user_id}:{hour}
EXPIRE rate_limit:recommendations:{user_id}:{hour} 3600

# Image analysis limits
INCR rate_limit:images:{user_id}:{day}
EXPIRE rate_limit:images:{user_id}:{day} 86400

# Seasonal rate limiting (higher limits during planting season)
HSET rate_limit:seasonal:config
  current_season "planting"
  recommendations_per_hour "100"
  images_per_hour "50"
  updated_at "2024-03-01T00:00:00Z"
```

### 5. Background Jobs (Database 4)
```redis
# Job queue for data processing
LPUSH queue:data_processing
  '{"job_id":"uuid","type":"soil_analysis","data":{...},"priority":1}'

# Job status tracking
HSET job:status:{job_id}
  status "completed"
  result "success"
  started_at "2024-12-09T10:30:00Z"
  completed_at "2024-12-09T10:32:00Z"
  error_message ""

EXPIRE job:status:{job_id} 86400

# Scheduled tasks
ZADD scheduled:tasks
  1702123800 '{"task":"weather_update","params":{"region":"midwest"}}'
  1702127400 '{"task":"price_update","params":{"commodities":["corn","soybean"]}}'

# Failed job retry queue
LPUSH queue:retry
  '{"job_id":"uuid","attempt":2,"max_attempts":3,"data":{...}}'
```

### 6. Agricultural Data Caching (Database 5)
```redis
# Farm profile cache
HSET farm:profile:{farm_id}
  farm_name "Johnson Family Farm"
  size_acres "320"
  primary_crops "corn,soybean"
  location_lat "42.0308"
  location_lon "-93.6319"
  irrigation "false"
  organic_certified "false"

EXPIRE farm:profile:{farm_id} 3600

# Soil test cache
HSET soil:test:{field_id}:latest
  ph "6.2"
  organic_matter "3.8"
  phosphorus "25"
  potassium "180"
  test_date "2024-03-15"
  lab_name "Iowa State Soil Lab"

EXPIRE soil:test:{field_id}:latest 86400

# Crop history cache
HSET crop:history:{field_id}:{year}
  crop "corn"
  variety "Pioneer P1197AM"
  yield "185"
  planting_date "2024-05-01"
  harvest_date "2024-10-15"

EXPIRE crop:history:{field_id}:{year} 86400

# Recommendation cache by question type
HSET recommendation:cache:{farm_id}:{question_type}
  recommendations "[{...}]"
  confidence "0.87"
  generated_at "2024-12-09T10:30:00Z"
  expires_at "2024-12-09T16:30:00Z"

EXPIRE recommendation:cache:{farm_id}:{question_type} 21600  # 6 hours
```

### 7. Image Analysis Temporary Data (Database 6)
```redis
# Uploaded image metadata
HSET image:upload:{upload_id}
  filename "crop_deficiency_001.jpg"
  file_size "2048576"
  upload_time "2024-12-09T10:30:00Z"
  user_id "uuid-here"
  farm_id "farm-uuid"
  processing_status "uploaded"

EXPIRE image:upload:{upload_id} 3600

# Image processing queue
LPUSH image:processing:queue
  '{"upload_id":"uuid","priority":"normal","model":"deficiency_v2"}'

# Analysis results cache
HSET image:results:{analysis_id}
  deficiencies "[{nutrient:nitrogen,severity:moderate,confidence:0.85}]"
  recommendations "[{action:apply_nitrogen,timing:immediate}]"
  confidence_overall "0.82"
  processing_time_ms "8500"

EXPIRE image:results:{analysis_id} 86400
```

### 8. Conversation State (Database 7)
```redis
# AI conversation context
HSET conversation:context:{session_id}
  user_id "uuid-here"
  farm_id "farm-uuid"
  current_topic "crop_selection"
  conversation_stage "gathering_requirements"
  last_question "What is your target yield for corn?"
  context_data '{"soil_ph":6.2,"farm_size":320}'

EXPIRE conversation:context:{session_id} 1800  # 30 minutes

# Conversation history (recent messages)
LPUSH conversation:history:{session_id}
  '{"role":"user","content":"What corn variety should I plant?","timestamp":"2024-12-09T10:30:00Z"}'
  '{"role":"assistant","content":"I need some information about your farm...","timestamp":"2024-12-09T10:30:15Z"}'

LTRIM conversation:history:{session_id} 0 49  # Keep last 50 messages
EXPIRE conversation:history:{session_id} 1800

# LLM usage tracking
HINCRBY llm:usage:{user_id}:{date} tokens_used 1250
HINCRBY llm:usage:{user_id}:{date} requests_made 1
EXPIRE llm:usage:{user_id}:{date} 86400
```

## Performance Optimization Patterns

### 1. Pipeline Operations
```redis
# Batch operations for better performance
MULTI
HSET farm:profile:{farm_id} farm_name "Johnson Farm"
HSET farm:profile:{farm_id} size_acres "320"
EXPIRE farm:profile:{farm_id} 3600
EXEC
```

### 2. Lua Scripts for Atomic Operations
```lua
-- Rate limiting with sliding window
local key = KEYS[1]
local window = tonumber(ARGV[1])
local limit = tonumber(ARGV[2])
local current_time = tonumber(ARGV[3])

-- Remove expired entries
redis.call('ZREMRANGEBYSCORE', key, 0, current_time - window)

-- Count current requests
local current_requests = redis.call('ZCARD', key)

if current_requests < limit then
    -- Add current request
    redis.call('ZADD', key, current_time, current_time)
    redis.call('EXPIRE', key, window)
    return {1, limit - current_requests - 1}
else
    return {0, 0}
end
```

### 3. Memory Optimization
```redis
# Use appropriate data structures
# For small sets, use strings with delimiters
SET user:farm_ids:{user_id} "farm1,farm2,farm3"

# For larger sets, use Redis sets
SADD user:farm_ids:{user_id} farm1 farm2 farm3

# Use hash fields for related data
HMSET farm:summary:{farm_id}
  name "Johnson Farm"
  acres "320"
  crops "corn,soybean"
  last_updated "2024-12-09"
```

## Monitoring and Maintenance

### Key Metrics to Monitor
```redis
# Memory usage
INFO memory

# Hit/miss ratios
INFO stats

# Slow queries
SLOWLOG GET 10

# Connected clients
INFO clients

# Keyspace information
INFO keyspace
```

### Cleanup Patterns
```redis
# Clean expired sessions daily
EVAL "
local keys = redis.call('KEYS', 'user:session:*')
local expired = 0
for i=1,#keys do
    if redis.call('TTL', keys[i]) == -1 then
        redis.call('DEL', keys[i])
        expired = expired + 1
    end
end
return expired
" 0

# Monitor cache hit rates
EVAL "
local total = redis.call('GET', 'stats:cache:total') or 0
local hits = redis.call('GET', 'stats:cache:hits') or 0
return {hits, total, hits/total}
" 0
```

## Security Considerations

### 1. Key Patterns
- Use unpredictable UUIDs in keys
- Avoid exposing sensitive data in key names
- Implement proper access controls

### 2. Data Sanitization
- Validate all data before storing
- Use appropriate data types
- Implement size limits

### 3. Connection Security
- Use password authentication
- Implement TLS for production
- Restrict network access

This Redis schema provides efficient caching, session management, and real-time data handling for the AFAS system while maintaining good performance and security practices.