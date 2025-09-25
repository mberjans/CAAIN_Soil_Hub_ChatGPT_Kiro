# AI Coding Agent Integration Guide

## Overview

This guide provides comprehensive instructions for AI coding agents to effectively implement the Autonomous Farm Advisory System using the existing documentation and codebase.

## Prerequisites for AI Agents

### Required Context Documents
1. **docs/plan.md**: Overall implementation strategy and sprint planning
2. **docs/tickets.md**: Detailed technical specifications for each ticket
3. **docs/checklist.md**: Granular task breakdown with ticket mapping
4. **services/ai-agent/**: Existing AI service implementation for reference

### Existing Codebase Foundation
- ✅ **AI Agent Service**: Fully implemented with OpenRouter LLM integration
- ✅ **Context Management**: Advanced conversation and agricultural context handling
- ✅ **Service Architecture**: Python/FastAPI microservices structure
- ✅ **Development Environment**: Native setup with CI/CD pipeline

## AI Agent Workflow

### Phase 1: Pre-Implementation Analysis

#### 1.1 Task Selection and Prioritization
```markdown
1. **Review Sprint Plan**: Check current phase in docs/plan.md
2. **Select Ticket**: Choose from priority tickets in current sprint
3. **Analyze Dependencies**: Review ticket dependencies in docs/tickets.md
4. **Check Prerequisites**: Verify required services are implemented
```

#### 1.2 Context Gathering
```markdown
1. **Read Ticket Specification**: Full technical requirements from docs/tickets.md
2. **Review Related Tasks**: Check all tasks for selected ticket in docs/checklist.md
3. **Analyze Existing Code**: Study similar implementations in services/
4. **Identify Integration Points**: Map connections to existing services
```

#### 1.3 Implementation Planning
```markdown
1. **Service Location**: Determine if extending existing service or creating new
2. **API Design**: Plan endpoints following existing patterns
3. **Data Models**: Design Pydantic models following established conventions
4. **Testing Strategy**: Plan unit, integration, and agricultural validation tests
```

### Phase 2: Implementation Execution

#### 2.1 Code Generation Standards
```python
# Service Structure Pattern (follow services/ai-agent/ structure)
services/{service-name}/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # FastAPI routes
│   ├── models/
│   │   ├── __init__.py
│   │   └── {domain}_models.py # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   └── {domain}_service.py # Business logic
│   └── config.py              # Configuration
├── tests/
│   ├── unit/
│   ├── integration/
│   └── agricultural/          # Domain-specific tests
├── requirements.txt
├── Dockerfile
└── README.md
```

#### 2.2 API Endpoint Patterns
```python
# Follow existing patterns from services/ai-agent/src/api/routes.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/v1/{domain}", tags=["{domain}"])

@router.post("/{endpoint}")
async def create_resource(
    request: ResourceCreateRequest,
    # Add authentication when available
) -> ResourceResponse:
    """
    Endpoint description following agricultural domain context.
    
    Args:
        request: Request model with validation
        
    Returns:
        Response model with agricultural data
        
    Raises:
        HTTPException: For validation or processing errors
    """
    try:
        # Implementation following existing service patterns
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 2.3 Database Integration Patterns
```python
# Follow existing database patterns
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field
from datetime import datetime

# SQLAlchemy Model
class FarmData(Base):
    __tablename__ = "farm_data"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models
class FarmDataCreate(BaseModel):
    user_id: str = Field(..., description="User identifier")
    # Add agricultural-specific fields with descriptions

class FarmDataResponse(BaseModel):
    id: str
    user_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### Phase 3: Integration and Testing

#### 3.1 Service Integration
```python
# Integration with existing services (reference services/ai-agent/)
from services.ai_agent.src.services.llm_service import create_llm_service
from services.ai_agent.src.services.context_manager import ContextManager

class NewDomainService:
    def __init__(self, llm_service=None, context_manager=None):
        self.llm_service = llm_service or create_llm_service()
        self.context_manager = context_manager or ContextManager()
    
    async def process_agricultural_request(self, request_data):
        # Use existing AI capabilities for explanations
        context = await self.context_manager.get_agricultural_context(
            user_id=request_data.user_id
        )
        
        # Generate AI explanation using existing service
        explanation = await self.llm_service.explain_recommendation(
            recommendation=result,
            agricultural_context=context
        )
        
        return result
```

#### 3.2 Testing Requirements
```python
# Test structure following services/ai-agent/tests/
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

class TestNewDomainService:
    @pytest.fixture
    def service(self):
        return NewDomainService()
    
    @pytest.mark.asyncio
    async def test_agricultural_processing(self, service):
        """Test agricultural domain logic with realistic data."""
        # Use agricultural test data
        test_data = {
            "soil_ph": 6.2,
            "crop_type": "corn",
            "location": {"lat": 41.8781, "lon": -87.6298}  # Chicago area
        }
        
        result = await service.process_request(test_data)
        
        # Validate agricultural accuracy
        assert result.recommendation is not None
        assert result.confidence_score >= 0.7
        assert "agricultural" in result.explanation.lower()

    def test_api_endpoint_integration(self):
        """Test API endpoints with realistic agricultural scenarios."""
        client = TestClient(app)
        
        response = client.post("/api/v1/domain/endpoint", json={
            "user_id": "farmer123",
            "farm_data": test_agricultural_data
        })
        
        assert response.status_code == 200
        assert "recommendation" in response.json()
```

## Quality Assurance for AI Agents

### Code Quality Standards
- **Test Coverage**: >80% with pytest
- **Type Hints**: Full type annotation with mypy validation
- **Documentation**: Comprehensive docstrings and README
- **Error Handling**: Robust exception handling with agricultural context
- **Logging**: Structured logging for debugging and monitoring

### Agricultural Domain Validation
- **Expert Review**: Flag complex agricultural logic for human expert review
- **Data Validation**: Validate agricultural data ranges and relationships
- **Safety Checks**: Implement safety warnings for critical recommendations
- **Regional Adaptation**: Consider location-specific agricultural practices

### Integration Validation
- **Service Dependencies**: Verify integration with existing services
- **API Compatibility**: Ensure API contracts match existing patterns
- **Database Consistency**: Validate database schema compatibility
- **Performance**: Meet <3 second response time requirements

## Human Handoff Points

### When to Request Human Review
1. **Complex Agricultural Logic**: Crop rotation algorithms, soil chemistry calculations
2. **Safety-Critical Recommendations**: Pesticide applications, soil amendments
3. **Regional Expertise**: Location-specific farming practices
4. **Performance Issues**: Response times >3 seconds
5. **Integration Failures**: Service communication problems

### Handoff Documentation
```markdown
## Implementation Summary
- **Ticket**: TICKET-XXX
- **Tasks Completed**: List of completed task IDs
- **Code Changes**: Summary of files modified/created
- **Testing Status**: Test coverage and validation results
- **Integration Points**: Services and APIs integrated
- **Outstanding Issues**: Any unresolved problems
- **Human Review Needed**: Specific areas requiring expert review
```

## Success Criteria

### Implementation Complete When:
- ✅ All ticket acceptance criteria met
- ✅ >80% test coverage achieved
- ✅ Agricultural validation tests pass
- ✅ Integration with existing services verified
- ✅ API documentation generated
- ✅ Performance requirements met (<3s response time)
- ✅ Code follows established patterns and conventions

### Ready for Production When:
- ✅ Human expert review completed (for agricultural logic)
- ✅ Security review passed
- ✅ Load testing completed
- ✅ Monitoring and logging configured
- ✅ Documentation updated
- ✅ Deployment configuration ready

This guide ensures AI coding agents can effectively contribute to the AFAS implementation while maintaining code quality, agricultural accuracy, and system integration standards.
