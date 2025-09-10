/**
 * OpenRouter Configuration for AFAS
 * 
 * This configuration manages LLM integration through OpenRouter,
 * providing unified access to multiple LLM providers.
 */

const dotenv = require('dotenv');
dotenv.config();

// Validate required environment variables
const requiredEnvVars = ['OPENROUTER_API_KEY'];
for (const envVar of requiredEnvVars) {
  if (!process.env[envVar]) {
    throw new Error(`Missing required environment variable: ${envVar}`);
  }
}

const openRouterConfig = {
  // Base configuration
  apiKey: process.env.OPENROUTER_API_KEY,
  baseURL: process.env.OPENROUTER_BASE_URL || 'https://openrouter.ai/api/v1',
  
  // Default model settings
  defaultModel: process.env.OPENROUTER_DEFAULT_MODEL || 'anthropic/claude-3-sonnet',
  
  // Model preferences for different use cases
  models: {
    // Agricultural explanations - prioritize reasoning and accuracy
    explanation: process.env.OPENROUTER_EXPLANATION_MODEL || 'anthropic/claude-3-sonnet',
    
    // Question classification - fast and accurate
    classification: process.env.OPENROUTER_CLASSIFICATION_MODEL || 'openai/gpt-4-turbo',
    
    // Conversational responses - balanced performance
    conversation: process.env.OPENROUTER_CONVERSATION_MODEL || 'anthropic/claude-3-sonnet',
    
    // High-volume tasks - cost-effective
    bulk: process.env.OPENROUTER_BULK_MODEL || 'openai/gpt-3.5-turbo',
    
    // Fallback model - reliable and available
    fallback: process.env.OPENROUTER_FALLBACK_MODEL || 'meta-llama/llama-3-8b-instruct'
  },
  
  // Request configuration
  requestConfig: {
    timeout: 30000, // 30 seconds
    maxRetries: 3,
    retryDelay: 1000, // 1 second
  },
  
  // Rate limiting (per minute)
  rateLimits: {
    'anthropic/claude-3-sonnet': 50,
    'openai/gpt-4-turbo': 100,
    'openai/gpt-3.5-turbo': 200,
    'meta-llama/llama-3-8b-instruct': 150
  },
  
  // Cost tracking (approximate costs per 1K tokens)
  costs: {
    'anthropic/claude-3-sonnet': { input: 0.003, output: 0.015 },
    'openai/gpt-4-turbo': { input: 0.01, output: 0.03 },
    'openai/gpt-3.5-turbo': { input: 0.0005, output: 0.0015 },
    'meta-llama/llama-3-8b-instruct': { input: 0.0002, output: 0.0002 }
  },
  
  // Agricultural-specific prompt templates
  prompts: {
    systemPrompt: `You are an expert agricultural advisor with deep knowledge of farming practices, soil science, crop management, and sustainable agriculture. 

Your responses should:
- Be accurate and based on scientific evidence
- Use clear, farmer-friendly language
- Include specific, actionable recommendations
- Consider regional variations and local conditions
- Emphasize safety and environmental responsibility
- Acknowledge uncertainty when appropriate

Always cite relevant agricultural sources and extension guidelines when making recommendations.`,
    
    explanationPrompt: `Explain the following agricultural recommendation in clear, practical terms that a farmer can understand and implement:

Recommendation: {recommendation}
Context: {context}
Confidence: {confidence}

Provide:
1. Clear explanation of the recommendation
2. Why this recommendation is appropriate
3. Specific implementation steps
4. Potential risks or considerations
5. Expected outcomes and timeline`,
    
    classificationPrompt: `Classify the following farmer question into one of the 20 AFAS question categories:

Question: {question}

Categories:
1. Crop Selection
2. Soil Fertility
3. Crop Rotation
4. Nutrient Deficiency Detection
5. Fertilizer Type Selection
6. Fertilizer Application Method
7. Fertilizer Timing
8. Environmental Impact
9. Cover Crops
10. Soil pH Management
11. Micronutrients
12. Precision Agriculture ROI
13. Drought Management
14. Early Deficiency Detection
15. Tillage Practices
16. Cost-Effective Fertilizer Strategy
17. Weather Impact Analysis
18. Testing Integration
19. Sustainable Yield Optimization
20. Government Programs

Return only the category number and name.`
  }
};

// Validation function
function validateConfig() {
  const errors = [];
  
  if (!openRouterConfig.apiKey) {
    errors.push('OpenRouter API key is required');
  }
  
  if (!openRouterConfig.apiKey.startsWith('sk-or-')) {
    errors.push('OpenRouter API key format appears invalid');
  }
  
  if (errors.length > 0) {
    throw new Error(`OpenRouter configuration errors: ${errors.join(', ')}`);
  }
  
  return true;
}

// Initialize and validate configuration
validateConfig();

module.exports = openRouterConfig;