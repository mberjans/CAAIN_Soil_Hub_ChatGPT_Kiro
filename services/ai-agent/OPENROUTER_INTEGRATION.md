# OpenRouter LLM Integration for AFAS AI Agent Service

This document describes the OpenRouter LLM integration implementation for the AFAS AI Agent Service, providing unified access to multiple LLM providers (GPT-4, Claude, Llama, etc.) with agricultural-specific optimizations.

## Overview

The OpenRouter integration provides:

- **Unified API Access**: Single interface to multiple LLM providers
- **Agricultural Context Awareness**: Specialized prompts and context management for farming scenarios
- **Intelligent Model Selection**: Automatic model selection based on use case and requirements
- **Cost Optimization**: Smart model routing to balance performance and cost
- **Streaming Support**: Real-time response streaming for better user experience
- **Conversation Management**: Persistent conversation context with agricultural metadata
- **Fallback Mechanisms**: Automatic fallback to alternative models on failures

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AFAS AI Agent Service                    │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Routes  │  LLM Service  │  Conversation Manager    │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                  OpenRouter Client                          │
├─────────────────────────────────────────────────────────────┤
│  Model Selection │  Rate Limiting │  Cost Tracking         │
│  Context Mgmt    │  Retry Logic   │  Agricultural Prompts  │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    OpenRouter API                           │
├─────────────────────────────────────────────────────────────┤
│  GPT-4 Turbo     │  Claude 3      │  Llama 3              │
│  GPT-3.5 Turbo   │  Claude Sonnet │  Other Models         │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. OpenRouter Client (`openrouter_client.py`)

Core client for interacting with the OpenRouter API:

```python
from src.services.openrouter_client import OpenRouterClient, LLMRequest

async with OpenRouterClient(api_key="sk-or-...") as client:
    request = LLMRequest(
        messages=[{"role": "user", "content": "What crops should I plant?"}],
        use_case="conversation",
        agricultural_context={"location": "Iowa", "soil_ph": 6.2}
    )
    
    response = await client.complete(request)
    print(response.content)
```

**Features:**
- Automatic model selection based on use case
- Agricultural context integration
- Rate limiting and cost tracking
- Retry logic with exponential backoff
- Streaming response support
- Confidence score calculation

### 2. LLM Service (`llm_service.py`)

High-level service for managing LLM interactions:

```python
from src.services.llm_service import LLMService, create_llm_service

llm_service = create_llm_service()

# Generate conversational response
response = await llm_service.generate_response(
    user_id="farmer123",
    session_id="session456",
    message="How much nitrogen should I apply to corn?",
    agricultural_context={
        "soil_data": {"ph": 6.2, "organic_matter_percent": 3.5},
        "crop": "corn",
        "yield_goal": 180
    }
)
```

**Features:**
- Conversation context management
- Response caching
- Agricultural explanation generation
- Structured recommendation support
- Health monitoring

### 3. API Routes (`api/routes.py`)

RESTful API endpoints for LLM interactions:

- `POST /api/v1/classify-question` - Question classification
- `POST /api/v1/chat` - Conversational AI
- `POST /api/v1/chat/stream` - Streaming responses
- `POST /api/v1/explain` - Agricultural explanations
- `POST /api/v1/recommend` - Structured recommendations
- `GET /api/v1/models` - Available models
- `GET /api/v1/health` - Health check

## Model Configuration

The integration supports different models optimized for specific use cases:

### Use Case Mapping

| Use Case | Model | Temperature | Max Tokens | Purpose |
|----------|-------|-------------|------------|---------|
| `explanation` | Claude 3 Sonnet | 0.3 | 2000 | Detailed agricultural explanations |
| `classification` | GPT-4 Turbo | 0.1 | 100 | Fast question categorization |
| `conversation` | Claude 3 Sonnet | 0.4 | 1500 | Natural conversations |
| `bulk` | GPT-3.5 Turbo | 0.2 | 1000 | Cost-effective processing |
| `fallback` | Llama 3 8B | 0.3 | 1500 | Reliable backup option |

### Model Selection Logic

```python
# Automatic selection based on use case
config = client.get_model_config("explanation")
# Returns: {"model": "anthropic/claude-3-sonnet", "temperature": 0.3, ...}

# Override with specific model
request = LLMRequest(
    messages=[...],
    model="openai/gpt-4-turbo",  # Override default
    use_case="explanation"
)
```

## Agricultural Context Integration

The integration includes specialized agricultural context handling:

### Context Types

```python
agricultural_context = {
    "farm_location": "Central Iowa",
    "soil_data": {
        "ph": 6.2,
        "organic_matter_percent": 3.5,
        "phosphorus_ppm": 25,
        "potassium_ppm": 180,
        "test_date": "2024-03-15"
    },
    "crop_info": {
        "type": "corn",
        "variety": "Pioneer P1197AM",
        "growth_stage": "V6",
        "yield_goal": 180
    },
    "season": "spring_2024",
    "management_history": {
        "previous_crop": "soybean",
        "tillage_system": "no_till",
        "cover_crops": True
    }
}
```

### Agricultural System Prompt

All requests include a specialized system prompt:

```
You are an expert agricultural advisor with deep knowledge of farming practices, 
soil science, crop management, and sustainable agriculture.

Your responses should:
- Be accurate and based on scientific evidence
- Use clear, farmer-friendly language
- Include specific, actionable recommendations
- Consider regional variations and local conditions
- Emphasize safety and environmental responsibility
- Acknowledge uncertainty when appropriate

Always cite relevant agricultural sources and extension guidelines when making recommendations.
```

## Configuration

### Environment Variables

```bash
# Required
OPENROUTER_API_KEY=sk-or-your-api-key-here

# Optional Configuration
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
MAX_CONVERSATION_LENGTH=20
CONTEXT_WINDOW_TOKENS=4000
ENABLE_STREAMING=true
CACHE_RESPONSES=true
CACHE_TTL_SECONDS=3600

# Model Overrides
OPENROUTER_EXPLANATION_MODEL=anthropic/claude-3-sonnet
OPENROUTER_CLASSIFICATION_MODEL=openai/gpt-4-turbo
OPENROUTER_CONVERSATION_MODEL=anthropic/claude-3-sonnet
OPENROUTER_BULK_MODEL=openai/gpt-3.5-turbo
OPENROUTER_FALLBACK_MODEL=meta-llama/llama-3-8b-instruct
```

### Configuration Class

```python
from src.config import AIAgentConfig

config = AIAgentConfig()
print(f"Using model: {config.explanation_model}")
print(f"Cache enabled: {config.cache_responses}")
```

## Usage Examples

### 1. Question Classification

```python
# Classify farmer question
result = await client.classify_question(
    "What fertilizer should I use for my corn crop?"
)

# Result:
{
    "category_number": 5,
    "category_name": "Fertilizer Type Selection",
    "confidence": 0.92
}
```

### 2. Agricultural Explanation

```python
# Explain recommendation
recommendation = {
    "type": "nitrogen_rate",
    "rate_lbs_per_acre": 150,
    "application_timing": ["pre_plant", "side_dress"]
}

context = {
    "soil_data": {"ph": 6.2, "organic_matter_percent": 3.5},
    "crop": "corn",
    "yield_goal": 180
}

explanation = await client.explain_recommendation(recommendation, context)
```

### 3. Streaming Conversation

```python
# Stream response for long explanations
request = LLMRequest(
    messages=[{
        "role": "user",
        "content": "Explain soil testing and fertilizer recommendations"
    }],
    use_case="explanation",
    stream=True
)

async for chunk in client.stream_complete(request):
    print(chunk, end="", flush=True)
```

### 4. Conversation Management

```python
# Maintain conversation context
llm_service = create_llm_service()

# First message
response1 = await llm_service.generate_response(
    user_id="farmer123",
    session_id="session456",
    message="I have 320 acres in Iowa. What crops should I consider?"
)

# Follow-up message (uses conversation history)
response2 = await llm_service.generate_response(
    user_id="farmer123",
    session_id="session456",
    message="What about fertilizer for corn?"
)
```

## Cost Management

### Cost Tracking

```python
# Automatic cost calculation
response = await client.complete(request)
print(f"Cost: ${response.cost_estimate:.4f}")

# Model-specific costs (per 1K tokens)
costs = {
    "anthropic/claude-3-sonnet": {"input": 0.003, "output": 0.015},
    "openai/gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "openai/gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "meta-llama/llama-3-8b-instruct": {"input": 0.0002, "output": 0.0002}
}
```

### Cost Optimization Strategies

1. **Use Case Routing**: Automatically select cost-effective models
2. **Response Caching**: Cache responses to avoid duplicate requests
3. **Token Estimation**: Estimate costs before making requests
4. **Bulk Processing**: Use cheaper models for high-volume tasks

## Rate Limiting

### Automatic Rate Limiting

```python
# Built-in rate limiting per model
rate_limits = {
    "anthropic/claude-3-sonnet": 50,      # requests per minute
    "openai/gpt-4-turbo": 100,
    "openai/gpt-3.5-turbo": 200,
    "meta-llama/llama-3-8b-instruct": 150
}

# Automatic fallback on rate limit
if not await client.check_rate_limit(model):
    # Automatically switches to fallback model
    pass
```

## Error Handling

### Retry Logic

```python
# Automatic retries with exponential backoff
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError))
)
async def _make_request(self, payload):
    # Request implementation with automatic retries
    pass
```

### Fallback Mechanisms

1. **Model Fallback**: Switch to backup model on primary failure
2. **Graceful Degradation**: Return cached or simplified responses
3. **Error Context**: Provide meaningful error messages with agricultural context

## Monitoring and Health Checks

### Health Check Endpoint

```python
# GET /api/v1/health
{
    "service": "llm_service",
    "status": "healthy",
    "active_conversations": 15,
    "cached_responses": 42,
    "openrouter_status": {
        "status": "healthy",
        "available_models": 25,
        "test_response_time": 1.2,
        "api_accessible": true
    }
}
```

### Metrics Collection

- Response times per model
- Cost tracking per user/session
- Error rates and types
- Cache hit rates
- Conversation lengths

## Testing

### Unit Tests

```bash
# Run unit tests
pytest services/ai-agent/tests/test_openrouter_integration.py -v

# Run with coverage
pytest services/ai-agent/tests/ --cov=src --cov-report=html
```

### Integration Tests

```bash
# Set API key for integration tests
export OPENROUTER_API_KEY=sk-or-your-api-key-here

# Run integration tests
pytest services/ai-agent/tests/test_openrouter_integration.py::TestOpenRouterIntegration -v
```

### Demo Script

```bash
# Run interactive demo
cd services/ai-agent
python demo_openrouter.py
```

## Deployment

### Docker Configuration

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
COPY .env .env

EXPOSE 8002

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8002"]
```

### Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your OpenRouter API key

# Run service
uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload
```

## Security Considerations

1. **API Key Management**: Store API keys securely in environment variables
2. **Rate Limiting**: Implement per-user rate limiting
3. **Input Validation**: Validate all agricultural data inputs
4. **Response Filtering**: Filter potentially harmful content
5. **Audit Logging**: Log all LLM interactions for audit purposes

## Performance Optimization

1. **Response Caching**: Cache frequent agricultural queries
2. **Connection Pooling**: Reuse HTTP connections
3. **Async Processing**: Use async/await for concurrent requests
4. **Model Selection**: Choose optimal models for each use case
5. **Token Management**: Optimize prompt length and response size

## Troubleshooting

### Common Issues

1. **API Key Invalid**: Check OpenRouter API key format and validity
2. **Rate Limiting**: Monitor rate limits and implement backoff
3. **Model Unavailable**: Use fallback models when primary unavailable
4. **High Costs**: Monitor usage and optimize model selection
5. **Slow Responses**: Check network connectivity and model performance

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with debug output
uvicorn src.main:app --log-level debug
```

## Future Enhancements

1. **Fine-tuned Models**: Train agricultural-specific models
2. **Multi-modal Support**: Add image and document processing
3. **Advanced Caching**: Implement semantic caching
4. **Cost Analytics**: Detailed cost analysis and optimization
5. **A/B Testing**: Compare model performance for agricultural tasks

## Support

For issues and questions:

1. Check the [API documentation](http://localhost:8002/docs)
2. Review the [demo script](demo_openrouter.py)
3. Run health checks: `GET /api/v1/health`
4. Check logs for error details
5. Consult OpenRouter documentation for API-specific issues