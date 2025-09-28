"""
OpenRouter LLM Client for AFAS AI Agent Service

Provides unified access to multiple LLM providers (GPT-4, Claude, Llama, etc.)
through the OpenRouter API with agricultural-specific optimizations.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime, timedelta
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import BaseModel, Field
import tiktoken

logger = logging.getLogger(__name__)


class LLMRequest(BaseModel):
    """Request model for LLM interactions."""
    
    messages: List[Dict[str, str]]
    model: Optional[str] = None
    use_case: str = "conversation"
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: bool = False
    agricultural_context: Optional[Dict[str, Any]] = None


class LLMResponse(BaseModel):
    """Response model for LLM interactions."""
    
    content: str
    model: str
    usage: Dict[str, int]
    cost_estimate: float
    response_time: float
    confidence_score: Optional[float] = None
    agricultural_metadata: Optional[Dict[str, Any]] = None


class OpenRouterClient:
    """
    OpenRouter client with agricultural-specific features and optimizations.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://afas.agricultural-advisor.com",
                "X-Title": "AFAS Agricultural Advisory System"
            }
        )
        
        # Model configurations
        self.model_configs = {
            "explanation": {
                "model": "anthropic/claude-3-sonnet",
                "temperature": 0.3,
                "max_tokens": 2000,
                "top_p": 0.9,
            },
            "classification": {
                "model": "openai/gpt-4-turbo",
                "temperature": 0.1,
                "max_tokens": 100,
                "top_p": 0.8,
            },
            "conversation": {
                "model": "anthropic/claude-3-sonnet",
                "temperature": 0.4,
                "max_tokens": 1500,
                "top_p": 0.9,
            },
            "bulk": {
                "model": "openai/gpt-3.5-turbo",
                "temperature": 0.2,
                "max_tokens": 1000,
                "top_p": 0.8,
            },
            "variety_explanation": {
                "model": "anthropic/claude-3-sonnet",
                "temperature": 0.25,
                "max_tokens": 2200,
                "top_p": 0.9,
            },
            "fallback": {
                "model": "meta-llama/llama-3-8b-instruct",
                "temperature": 0.3,
                "max_tokens": 1500,
                "top_p": 0.9,
            }
        }
        
        # Rate limiting
        self.rate_limits = {}
        self.request_counts = {}
        
        # Cost tracking
        self.costs = {
            "anthropic/claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "openai/gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "openai/gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "meta-llama/llama-3-8b-instruct": {"input": 0.0002, "output": 0.0002}
        }
        
        # Agricultural system prompt
        self.agricultural_system_prompt = """You are an expert agricultural advisor with deep knowledge of farming practices, soil science, crop management, and sustainable agriculture.

Your responses should:
- Be accurate and based on scientific evidence
- Use clear, farmer-friendly language
- Include specific, actionable recommendations
- Consider regional variations and local conditions
- Emphasize safety and environmental responsibility
- Acknowledge uncertainty when appropriate

Always cite relevant agricultural sources and extension guidelines when making recommendations."""

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def get_model_config(self, use_case: str) -> Dict[str, Any]:
        """Get model configuration for specific use case."""
        if use_case not in self.model_configs:
            logger.warning(f"Unknown use case '{use_case}', using conversation")
            use_case = "conversation"
        
        return self.model_configs[use_case].copy()

    def estimate_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """Estimate token count for text."""
        try:
            # Use tiktoken for OpenAI models, rough estimation for others
            if "gpt" in model.lower():
                encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
                return len(encoding.encode(text))
            else:
                # Rough estimation: ~4 characters per token
                return len(text) // 4
        except Exception:
            # Fallback estimation
            return len(text) // 4

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate estimated cost for model usage."""
        if model not in self.costs:
            return 0.0
        
        cost_config = self.costs[model]
        input_cost = (input_tokens / 1000) * cost_config["input"]
        output_cost = (output_tokens / 1000) * cost_config["output"]
        
        return input_cost + output_cost

    async def check_rate_limit(self, model: str) -> bool:
        """Check if request is within rate limits."""
        current_time = time.time()
        minute_window = int(current_time // 60)
        
        if model not in self.request_counts:
            self.request_counts[model] = {}
        
        # Clean old entries
        self.request_counts[model] = {
            k: v for k, v in self.request_counts[model].items()
            if k >= minute_window - 1
        }
        
        current_count = self.request_counts[model].get(minute_window, 0)
        rate_limit = self.rate_limits.get(model, 50)  # Default 50 requests per minute
        
        if current_count >= rate_limit:
            return False
        
        self.request_counts[model][minute_window] = current_count + 1
        return True

    def prepare_messages(self, request: LLMRequest) -> List[Dict[str, str]]:
        """Prepare messages with agricultural system prompt."""
        messages = []
        
        # Add system prompt if not already present
        if not request.messages or request.messages[0].get("role") != "system":
            messages.append({
                "role": "system",
                "content": self.agricultural_system_prompt
            })
        
        # Add agricultural context if provided
        if request.agricultural_context:
            context_message = self._format_agricultural_context(request.agricultural_context)
            messages.append({
                "role": "system",
                "content": context_message
            })
        
        messages.extend(request.messages)
        return messages

    def _format_agricultural_context(self, context: Dict[str, Any]) -> str:
        """Format agricultural context for the LLM."""
        context_parts = []
        
        if "farm_location" in context:
            context_parts.append(f"Farm Location: {context['farm_location']}")
        
        if "soil_data" in context:
            soil = context["soil_data"]
            context_parts.append(f"Soil Data: pH {soil.get('ph', 'N/A')}, "
                               f"OM {soil.get('organic_matter_percent', 'N/A')}%, "
                               f"P {soil.get('phosphorus_ppm', 'N/A')} ppm, "
                               f"K {soil.get('potassium_ppm', 'N/A')} ppm")
        
        if "crop_info" in context:
            crop = context["crop_info"]
            context_parts.append(f"Crop: {crop.get('type', 'N/A')}, "
                               f"Growth Stage: {crop.get('growth_stage', 'N/A')}")
        
        if "season" in context:
            context_parts.append(f"Season: {context['season']}")
        
        if context_parts:
            return "Agricultural Context:\n" + "\n".join(context_parts)
        
        return ""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError))
    )
    async def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to OpenRouter API with retries."""
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning(f"Rate limit exceeded for model {payload.get('model')}")
                raise
            elif e.response.status_code >= 500:
                logger.error(f"Server error: {e.response.status_code}")
                raise
            else:
                logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
                raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """
        Generate completion using OpenRouter API.
        
        Args:
            request: LLM request with messages and configuration
            
        Returns:
            LLM response with content and metadata
        """
        start_time = time.time()
        
        # Get model configuration
        config = self.get_model_config(request.use_case)
        model = request.model or config["model"]
        
        # Check rate limits
        if not await self.check_rate_limit(model):
            logger.warning(f"Rate limit exceeded for model {model}, using fallback")
            model = self.model_configs["fallback"]["model"]
            config = self.model_configs["fallback"]
        
        # Prepare messages
        messages = self.prepare_messages(request)
        
        # Prepare payload
        payload = {
            "model": model,
            "messages": messages,
            "temperature": request.temperature or config["temperature"],
            "max_tokens": request.max_tokens or config["max_tokens"],
            "top_p": config.get("top_p", 0.9),
            "stream": request.stream
        }
        
        try:
            # Make request
            response_data = await self._make_request(payload)
            
            # Extract response
            choice = response_data["choices"][0]
            content = choice["message"]["content"]
            usage = response_data.get("usage", {})
            
            # Calculate metrics
            response_time = time.time() - start_time
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            cost_estimate = self.calculate_cost(model, input_tokens, output_tokens)
            
            # Calculate confidence score based on agricultural context
            confidence_score = self._calculate_confidence_score(
                request, content, model, response_time
            )
            
            # Extract agricultural metadata
            agricultural_metadata = self._extract_agricultural_metadata(
                request, content
            )
            
            logger.info(f"LLM completion successful: model={model}, "
                       f"tokens={input_tokens + output_tokens}, "
                       f"cost=${cost_estimate:.4f}, time={response_time:.2f}s")
            
            return LLMResponse(
                content=content,
                model=model,
                usage=usage,
                cost_estimate=cost_estimate,
                response_time=response_time,
                confidence_score=confidence_score,
                agricultural_metadata=agricultural_metadata
            )
            
        except Exception as e:
            logger.error(f"LLM completion failed: {e}")
            
            # Try fallback model if primary failed
            if model != self.model_configs["fallback"]["model"]:
                logger.info("Attempting fallback model")
                fallback_request = request.copy()
                fallback_request.model = self.model_configs["fallback"]["model"]
                fallback_request.use_case = "fallback"
                return await self.complete(fallback_request)
            
            raise

    async def stream_complete(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """
        Generate streaming completion using OpenRouter API.
        
        Args:
            request: LLM request with messages and configuration
            
        Yields:
            Content chunks as they arrive
        """
        # Get model configuration
        config = self.get_model_config(request.use_case)
        model = request.model or config["model"]
        
        # Prepare messages
        messages = self.prepare_messages(request)
        
        # Prepare payload
        payload = {
            "model": model,
            "messages": messages,
            "temperature": request.temperature or config["temperature"],
            "max_tokens": request.max_tokens or config["max_tokens"],
            "top_p": config.get("top_p", 0.9),
            "stream": True
        }
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        
                        if data == "[DONE]":
                            break
                        
                        try:
                            chunk = json.loads(data)
                            if "choices" in chunk and chunk["choices"]:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"Streaming completion failed: {e}")
            raise

    def _calculate_confidence_score(
        self, 
        request: LLMRequest, 
        content: str, 
        model: str, 
        response_time: float
    ) -> float:
        """Calculate confidence score based on various factors."""
        confidence = 0.8  # Base confidence
        
        # Model reliability factor
        model_reliability = {
            "anthropic/claude-3-sonnet": 0.95,
            "openai/gpt-4-turbo": 0.9,
            "openai/gpt-3.5-turbo": 0.8,
            "meta-llama/llama-3-8b-instruct": 0.75
        }
        confidence *= model_reliability.get(model, 0.7)
        
        # Agricultural context factor
        if request.agricultural_context:
            context_completeness = len(request.agricultural_context) / 5  # Assume 5 key fields
            confidence *= min(1.0, 0.8 + context_completeness * 0.2)
        else:
            confidence *= 0.7  # Reduce confidence without context
        
        # Response quality indicators
        if len(content) < 50:
            confidence *= 0.8  # Very short responses are less reliable
        
        if "I don't know" in content.lower() or "uncertain" in content.lower():
            confidence *= 0.9  # Acknowledge uncertainty appropriately
        
        # Response time factor (very fast or very slow responses may be less reliable)
        if response_time < 1.0:
            confidence *= 0.95  # Slightly reduce for very fast responses
        elif response_time > 20.0:
            confidence *= 0.9  # Reduce for very slow responses
        
        return min(1.0, max(0.0, confidence))

    def _extract_agricultural_metadata(
        self, 
        request: LLMRequest, 
        content: str
    ) -> Dict[str, Any]:
        """Extract agricultural metadata from response."""
        metadata = {}
        
        # Detect agricultural topics mentioned
        agricultural_topics = [
            "soil", "fertilizer", "crop", "nitrogen", "phosphorus", "potassium",
            "ph", "organic matter", "yield", "planting", "harvest", "irrigation",
            "pest", "disease", "rotation", "cover crop", "tillage"
        ]
        
        mentioned_topics = [
            topic for topic in agricultural_topics
            if topic in content.lower()
        ]
        metadata["topics_mentioned"] = mentioned_topics
        
        # Detect specific recommendations
        if any(word in content.lower() for word in ["recommend", "suggest", "should"]):
            metadata["contains_recommendations"] = True
        
        # Detect uncertainty indicators
        uncertainty_words = ["may", "might", "could", "possibly", "uncertain", "depends"]
        if any(word in content.lower() for word in uncertainty_words):
            metadata["expresses_uncertainty"] = True
        
        # Detect safety warnings
        safety_words = ["caution", "warning", "danger", "safety", "careful"]
        if any(word in content.lower() for word in safety_words):
            metadata["includes_safety_warnings"] = True
        
        return metadata

    async def classify_question(self, question: str) -> Dict[str, Any]:
        """
        Classify farmer question into AFAS categories.
        
        Args:
            question: Farmer's question text
            
        Returns:
            Classification result with category and confidence
        """
        classification_prompt = f"""Classify the following farmer question into one of the 20 AFAS question categories:

Question: {question}

Categories:
1. Crop Selection - What crops/varieties to grow
2. Soil Fertility - Improving soil health and fertility
3. Crop Rotation - Planning crop rotation sequences
4. Nutrient Deficiency Detection - Identifying nutrient problems
5. Fertilizer Type Selection - Choosing fertilizer types
6. Fertilizer Application Method - How to apply fertilizers
7. Fertilizer Timing - When to apply fertilizers
8. Environmental Impact - Reducing environmental impact
9. Cover Crops - Using cover crops effectively
10. Soil pH Management - Managing soil acidity/alkalinity
11. Micronutrients - Managing trace elements
12. Precision Agriculture ROI - Technology investment decisions
13. Drought Management - Water conservation strategies
14. Early Deficiency Detection - Spotting problems early
15. Tillage Practices - Soil cultivation methods
16. Cost-Effective Fertilizer Strategy - Economic optimization
17. Weather Impact Analysis - Weather-related decisions
18. Testing Integration - Using soil/tissue tests
19. Sustainable Yield Optimization - Balancing yield and sustainability
20. Government Programs - Subsidies and regulations

Return only the category number, name, and confidence score (0-1) in JSON format:
{{"category_number": X, "category_name": "...", "confidence": 0.XX}}"""

        request = LLMRequest(
            messages=[{"role": "user", "content": classification_prompt}],
            use_case="classification"
        )
        
        response = await self.complete(request)
        
        try:
            # Parse JSON response
            result = json.loads(response.content)
            return result
        except json.JSONDecodeError:
            # Fallback parsing
            logger.warning("Failed to parse classification JSON, using fallback")
            return {
                "category_number": 1,
                "category_name": "Crop Selection",
                "confidence": 0.5
            }

    async def explain_recommendation(
        self, 
        recommendation: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> str:
        """
        Generate explanation for agricultural recommendation.
        
        Args:
            recommendation: Recommendation data
            context: Agricultural context (soil, crop, location, etc.)
            
        Returns:
            Human-readable explanation
        """
        explanation_prompt = f"""Explain the following agricultural recommendation in clear, practical terms that a farmer can understand and implement:

Recommendation: {json.dumps(recommendation, indent=2)}
Context: {json.dumps(context, indent=2)}

Provide:
1. Clear explanation of the recommendation
2. Why this recommendation is appropriate for the given conditions
3. Specific implementation steps
4. Potential risks or considerations
5. Expected outcomes and timeline

Use farmer-friendly language and include specific, actionable advice."""

        request = LLMRequest(
            messages=[{"role": "user", "content": explanation_prompt}],
            use_case="explanation",
            agricultural_context=context
        )
        
        response = await self.complete(request)
        return response.content

    async def generate_variety_explanation(
        self,
        structured_payload: Dict[str, Any]
    ) -> str:
        """Generate variety-focused explanation using structured payload."""
        language_code = structured_payload.get("language", "en")
        tone = structured_payload.get("audience_level", "farmer_friendly")

        language_label = "English"
        if language_code == "es":
            language_label = "Spanish"
        elif language_code == "fr":
            language_label = "French"

        prompt_sections: List[str] = []
        prompt_sections.append("You are an expert crop variety advisor supporting farmers with clear, actionable recommendations.")
        prompt_sections.append(f"Respond in {language_label} language.")
        prompt_sections.append(f"Audience expertise level: {tone}.")
        prompt_sections.append("Create a comprehensive explanation covering: summary, fit with farm context, management guidance, risks, economics, and next steps.")
        prompt_sections.append("Ensure explanations remain accurate to the data, highlight important trade-offs, and keep language farmer-friendly.")

        yield_insights = structured_payload.get("yield_insights")
        if isinstance(yield_insights, list) and len(yield_insights) > 0:
            prompt_sections.append("Yield considerations to feature:")
            index = 0
            while index < len(yield_insights):
                insight = yield_insights[index]
                if isinstance(insight, str) and len(insight) > 0:
                    prompt_sections.append(f"- {insight}")
                index += 1

        disease_highlights = structured_payload.get("disease_highlights")
        if isinstance(disease_highlights, list) and len(disease_highlights) > 0:
            prompt_sections.append("Disease and pest highlights:")
            index = 0
            while index < len(disease_highlights):
                highlight = disease_highlights[index]
                if isinstance(highlight, str) and len(highlight) > 0:
                    prompt_sections.append(f"- {highlight}")
                index += 1

        climate_adaptation = structured_payload.get("climate_adaptation")
        if isinstance(climate_adaptation, list) and len(climate_adaptation) > 0:
            prompt_sections.append("Climate adaptation notes:")
            index = 0
            while index < len(climate_adaptation):
                adaptation = climate_adaptation[index]
                if isinstance(adaptation, str) and len(adaptation) > 0:
                    prompt_sections.append(f"- {adaptation}")
                index += 1

        economic_summary = structured_payload.get("economic_summary")
        if isinstance(economic_summary, list) and len(economic_summary) > 0:
            prompt_sections.append("Economic considerations:")
            index = 0
            while index < len(economic_summary):
                economic_point = economic_summary[index]
                if isinstance(economic_point, str) and len(economic_point) > 0:
                    prompt_sections.append(f"- {economic_point}")
                index += 1

        quality_metrics = structured_payload.get("quality_metrics")
        if isinstance(quality_metrics, dict):
            coherence = quality_metrics.get("coherence_score")
            coverage = quality_metrics.get("coverage_score")
            prompt_sections.append("Quality metrics for the explanation:")
            if isinstance(coherence, (int, float)):
                prompt_sections.append(f"- Coherence score: {round(float(coherence) * 100)}%")
            if isinstance(coverage, (int, float)):
                prompt_sections.append(f"- Coverage score: {round(float(coverage) * 100)}%")
            flags = quality_metrics.get("accuracy_flags")
            if isinstance(flags, list) and len(flags) > 0:
                prompt_sections.append("- Accuracy considerations:")
                index = 0
                while index < len(flags):
                    flag = flags[index]
                    if isinstance(flag, str) and len(flag) > 0:
                        prompt_sections.append(f"  * {flag}")
                    index += 1

        key_points = structured_payload.get("key_points")
        if isinstance(key_points, list) and len(key_points) > 0:
            prompt_sections.append("Key points to reinforce:")
            for point in key_points:
                prompt_sections.append(f"- {point}")

        prompt_sections.append("Structured data for reference:")
        json_payload = json.dumps(structured_payload, indent=2, default=str)
        prompt_sections.append(json_payload)
        prompt_sections.append("Use the structure above to craft the final explanation. Where appropriate, use brief headings and bullet lists. Provide implementation steps the farmer can take this season.")

        prompt_text = "\n".join(prompt_sections)

        request = LLMRequest(
            messages=[{"role": "user", "content": prompt_text}],
            use_case="variety_explanation",
            agricultural_context={"variety_payload": structured_payload}
        )

        response = await self.complete(request)
        return response.content

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from OpenRouter."""
        try:
            response = await self.client.get(f"{self.base_url}/models")
            response.raise_for_status()
            models_data = response.json()
            
            # Filter for models we support
            supported_models = []
            for model in models_data.get("data", []):
                model_id = model.get("id", "")
                if any(provider in model_id for provider in ["openai", "anthropic", "meta-llama"]):
                    supported_models.append({
                        "id": model_id,
                        "name": model.get("name", model_id),
                        "context_length": model.get("context_length", 4096),
                        "pricing": model.get("pricing", {}),
                        "top_provider": model.get("top_provider", {})
                    })
            
            return supported_models
            
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []

    async def health_check(self) -> Dict[str, Any]:
        """Check OpenRouter API health and connectivity."""
        try:
            models = await self.get_available_models()
            
            # Test a simple completion
            test_request = LLMRequest(
                messages=[{"role": "user", "content": "Hello"}],
                use_case="bulk"
            )
            
            start_time = time.time()
            response = await self.complete(test_request)
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "available_models": len(models),
                "test_response_time": response_time,
                "api_accessible": True
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "api_accessible": False
            }
