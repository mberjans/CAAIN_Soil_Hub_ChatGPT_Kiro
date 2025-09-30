# Authentication API Reference

## Overview

The Authentication API provides secure access to the crop variety recommendations system using API keys and JWT tokens. This document covers authentication methods, token management, and security best practices.

## Authentication Methods

### 1. API Key Authentication

API keys provide simple, stateless authentication for server-to-server communication.

#### Headers

```http
Authorization: Bearer <your-api-key>
Content-Type: application/json
```

#### Example Request

```bash
curl -X POST "http://localhost:8001/api/v1/varieties/recommend" \
  -H "Authorization: Bearer sk-1234567890abcdef" \
  -H "Content-Type: application/json" \
  -d '{
    "crop_id": "corn",
    "farm_data": {
      "location": {
        "latitude": 40.7128,
        "longitude": -74.0060
      }
    }
  }'
```

### 2. JWT Token Authentication

JWT tokens provide more advanced authentication with expiration and refresh capabilities.

#### Headers

```http
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

#### Example Request

```bash
curl -X POST "http://localhost:8001/api/v1/varieties/recommend" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "crop_id": "corn",
    "farm_data": {
      "location": {
        "latitude": 40.7128,
        "longitude": -74.0060
      }
    }
  }'
```

## Authentication Endpoints

### 1. Generate API Key

**Endpoint:** `POST /auth/api-keys`

Generate a new API key for authentication.

#### Request Body

```json
{
  "name": "My Application API Key",
  "description": "API key for my farm management application",
  "permissions": [
    "varieties:read",
    "varieties:compare",
    "varieties:filter"
  ],
  "expires_at": "2024-12-31T23:59:59Z",
  "rate_limit": 1000
}
```

#### Response

```json
{
  "api_key": "sk-1234567890abcdef1234567890abcdef",
  "key_id": "key_12345",
  "name": "My Application API Key",
  "description": "API key for my farm management application",
  "permissions": [
    "varieties:read",
    "varieties:compare",
    "varieties:filter"
  ],
  "expires_at": "2024-12-31T23:59:59Z",
  "rate_limit": 1000,
  "created_at": "2024-01-15T10:30:00Z",
  "last_used": null
}
```

### 2. List API Keys

**Endpoint:** `GET /auth/api-keys`

List all API keys for the authenticated user.

#### Response

```json
{
  "api_keys": [
    {
      "key_id": "key_12345",
      "name": "My Application API Key",
      "description": "API key for my farm management application",
      "permissions": [
        "varieties:read",
        "varieties:compare",
        "varieties:filter"
      ],
      "expires_at": "2024-12-31T23:59:59Z",
      "rate_limit": 1000,
      "created_at": "2024-01-15T10:30:00Z",
      "last_used": "2024-01-15T14:22:00Z",
      "is_active": true
    }
  ],
  "total_keys": 1
}
```

### 3. Revoke API Key

**Endpoint:** `DELETE /auth/api-keys/{key_id}`

Revoke an API key to prevent further access.

#### Response

```json
{
  "message": "API key revoked successfully",
  "key_id": "key_12345",
  "revoked_at": "2024-01-15T15:30:00Z"
}
```

### 4. Login with Credentials

**Endpoint:** `POST /auth/login`

Authenticate with username and password to receive a JWT token.

#### Request Body

```json
{
  "username": "farmer@example.com",
  "password": "secure_password_123"
}
```

#### Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "user_id": "user_12345",
    "username": "farmer@example.com",
    "name": "John Farmer",
    "role": "farmer",
    "permissions": [
      "varieties:read",
      "varieties:compare",
      "varieties:filter",
      "recommendations:save"
    ]
  }
}
```

### 5. Refresh Token

**Endpoint:** `POST /auth/refresh`

Refresh an expired JWT token using a refresh token.

#### Request Body

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### 6. Logout

**Endpoint:** `POST /auth/logout`

Invalidate the current JWT token.

#### Request Body

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Response

```json
{
  "message": "Successfully logged out",
  "logged_out_at": "2024-01-15T16:30:00Z"
}
```

## Permissions

### Permission Types

| Permission | Description |
|------------|-------------|
| `varieties:read` | Read variety data and recommendations |
| `varieties:compare` | Compare varieties |
| `varieties:filter` | Filter varieties |
| `varieties:write` | Create and modify variety data |
| `recommendations:read` | Read recommendations |
| `recommendations:save` | Save recommendations |
| `recommendations:share` | Share recommendations |
| `analytics:read` | Read analytics data |
| `admin:all` | Full administrative access |

### Role-Based Permissions

#### Farmer Role
```json
{
  "role": "farmer",
  "permissions": [
    "varieties:read",
    "varieties:compare",
    "varieties:filter",
    "recommendations:read",
    "recommendations:save"
  ]
}
```

#### Consultant Role
```json
{
  "role": "consultant",
  "permissions": [
    "varieties:read",
    "varieties:compare",
    "varieties:filter",
    "recommendations:read",
    "recommendations:save",
    "recommendations:share",
    "analytics:read"
  ]
}
```

#### Admin Role
```json
{
  "role": "admin",
  "permissions": [
    "admin:all"
  ]
}
```

## Rate Limiting

### Rate Limit Tiers

| Tier | Requests per Minute | Burst Limit |
|------|-------------------|-------------|
| Free | 100 | 200 |
| Basic | 500 | 1000 |
| Professional | 2000 | 5000 |
| Enterprise | 10000 | 20000 |

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
X-RateLimit-Retry-After: 60
```

### Rate Limit Exceeded Response

```json
{
  "detail": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60,
  "limit": 1000,
  "remaining": 0,
  "reset_time": "2024-01-15T17:00:00Z"
}
```

## Security Best Practices

### 1. API Key Security

- Store API keys securely (environment variables, secure vaults)
- Never commit API keys to version control
- Rotate API keys regularly
- Use different keys for different environments
- Monitor API key usage

### 2. JWT Token Security

- Store JWT tokens securely
- Implement token refresh logic
- Handle token expiration gracefully
- Use HTTPS for all API calls
- Validate token signatures

### 3. Request Security

- Always use HTTPS
- Validate all input data
- Implement proper error handling
- Log authentication events
- Monitor for suspicious activity

## Error Responses

### 401 Unauthorized

```json
{
  "detail": "Authentication required",
  "error_code": "UNAUTHORIZED",
  "www_authenticate": "Bearer"
}
```

### 403 Forbidden

```json
{
  "detail": "Insufficient permissions",
  "error_code": "FORBIDDEN",
  "required_permission": "varieties:write",
  "user_permissions": ["varieties:read", "varieties:compare"]
}
```

### 429 Too Many Requests

```json
{
  "detail": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60,
  "limit": 1000,
  "remaining": 0
}
```

## SDK Examples

### Python

```python
import requests
from requests.auth import HTTPBearerAuth

# Using API Key
api_key = "sk-1234567890abcdef"
headers = {"Authorization": f"Bearer {api_key}"}

response = requests.post(
    "http://localhost:8001/api/v1/varieties/recommend",
    headers=headers,
    json={
        "crop_id": "corn",
        "farm_data": {
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }
    }
)

# Using JWT Token
jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
headers = {"Authorization": f"Bearer {jwt_token}"}

response = requests.post(
    "http://localhost:8001/api/v1/varieties/recommend",
    headers=headers,
    json={
        "crop_id": "corn",
        "farm_data": {
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }
    }
)
```

### JavaScript

```javascript
// Using API Key
const apiKey = 'sk-1234567890abcdef';
const headers = {
  'Authorization': `Bearer ${apiKey}`,
  'Content-Type': 'application/json'
};

const response = await fetch('http://localhost:8001/api/v1/varieties/recommend', {
  method: 'POST',
  headers: headers,
  body: JSON.stringify({
    crop_id: 'corn',
    farm_data: {
      location: {
        latitude: 40.7128,
        longitude: -74.0060
      }
    }
  })
});

// Using JWT Token
const jwtToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';
const headers = {
  'Authorization': `Bearer ${jwtToken}`,
  'Content-Type': 'application/json'
};

const response = await fetch('http://localhost:8001/api/v1/varieties/recommend', {
  method: 'POST',
  headers: headers,
  body: JSON.stringify({
    crop_id: 'corn',
    farm_data: {
      location: {
        latitude: 40.7128,
        longitude: -74.0060
      }
    }
  })
});
```

## Testing

### Test Environment

- **Base URL:** `http://localhost:8001/api/v1/auth`
- **Test API Key:** `test-api-key-12345`
- **Test JWT Token:** `test-jwt-token-67890`

### Sample Test Data

```json
{
  "test_credentials": {
    "username": "test@example.com",
    "password": "test_password_123"
  },
  "test_api_key": "test-api-key-12345",
  "test_permissions": [
    "varieties:read",
    "varieties:compare",
    "varieties:filter"
  ]
}
```

## Changelog

### Version 1.2.0 (Current)
- Added role-based permissions
- Enhanced rate limiting
- Improved security features

### Version 1.1.0
- Added JWT token support
- Enhanced API key management
- Improved error handling

### Version 1.0.0
- Initial release
- Basic API key authentication
- Core permission system