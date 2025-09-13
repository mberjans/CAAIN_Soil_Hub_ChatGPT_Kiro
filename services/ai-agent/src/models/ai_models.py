"""
AI Agent Pydantic Models

Models for AI-powered explanations and natural language processing.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AIProvider(str, Enum):
    """Supported AI providers via OpenRouter."""
    OPENAI_GPT4 = "openai/gpt-4"
    OPENAI_GPT35 = "openai/gpt-3.5-turbo"
    ANTHROPIC_CLAUDE = "anthropic/claude-2"
    META_LLAMA = "meta-llama/llama-2-70b-chat"


class ExplanationRequest(BaseModel):
    """Request for AI-powered explanation of recommendations."""
    
    request_id: str = Field(..., description="Unique request identifier")
    recommendation_data: Dict[str, Any] = Field(..., description="Recommendation data to explain")
    user_context: Optional[Dict[str, Any]] = Field(None, description="User context and preferences")
    explanation_style: str = Field(default="farmer_friendly", description="Explanation style")
    max_length: int = Field(default=500, ge=100, le=2000, description="Maximum explanation length")
    include_sources: bool = Field(default=True, description="Include agricultural sources")
    
    @validator('explanation_style')
    def validate_explanation_style(cls, v):
        valid_styles = ["farmer_friendly", "technical", "beginner", "detailed"]
        if v not in valid_styles:
            raise ValueError(f"Style must be one of: {valid_styles}")
        return v


class ConversationContext(BaseModel):
    """Context for ongoing conversations."""
    
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Conversation session ID")
    conversation_history: List[Dict[str, str]] = Field(default_factory=list, description="Message history")
    farm_context: Optional[Dict[str, Any]] = Field(None, description="Farm-specific context")
    current_topic: Optional[str] = Field(None, description="Current conversation topic")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    @validator('conversation_history')
    def validate_conversation_history(cls, v):
        # Limit conversation history to prevent token overflow
        if len(v) > 20:
            return v[-20:]  # Keep last 20 messages
        return v


class AIAgentConfig(BaseModel):
    """Configuration for AI agent behavior."""
    
    provider: AIProvider = Field(default=AIProvider.OPENAI_GPT4, description="AI provider to use")
    temperature: float = Field(default=0.3, ge=0.0, le=1.0, description="Response creativity")
    max_tokens: int = Field(default=1000, ge=100, le=4000, description="Maximum response tokens")
    agricultural_focus: bool = Field(default=True, description="Focus on agricultural accuracy")
    conservative_mode: bool = Field(default=True, description="Use conservative recommendations")
    include_warnings: bool = Field(default=True, description="Include safety warnings")


class ExplanationResponse(BaseModel):
    """Response containing AI-generated explanation."""
    
    request_id: str = Field(..., description="Original request identifier")
    explanation: str = Field(..., description="AI-generated explanation")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Explanation confidence")
    key_points: List[str] = Field(..., description="Key points highlighted")
    follow_up_questions: List[str] = Field(default_factory=list, description="Suggested follow-up questions")
    agricultural_sources: List[str] = Field(default_factory=list, description="Referenced sources")
    warnings: Optional[List[str]] = Field(None, description="Important warnings")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }