# Frontend Integration Guide

## Overview

This guide covers integrating the crop variety recommendations system with frontend applications, including web interfaces, mobile apps, and third-party integrations.

## Frontend Architecture

### Component Structure

```
Frontend Application
├── Components/
│   ├── VarietySelection/
│   │   ├── VarietyList.tsx
│   │   ├── VarietyCard.tsx
│   │   ├── VarietyFilters.tsx
│   │   └── VarietyComparison.tsx
│   ├── RecommendationEngine/
│   │   ├── RecommendationForm.tsx
│   │   ├── RecommendationResults.tsx
│   │   └── RecommendationExplanation.tsx
│   └── Shared/
│       ├── LoadingSpinner.tsx
│       ├── ErrorBoundary.tsx
│       └── DataTable.tsx
├── Services/
│   ├── api.ts
│   ├── varietyService.ts
│   └── recommendationService.ts
├── Hooks/
│   ├── useVarietyRecommendations.ts
│   ├── useVarietyComparison.ts
│   └── useVarietyFilters.ts
└── Utils/
    ├── formatters.ts
    ├── validators.ts
    └── constants.ts
```

## API Integration

### 1. API Service Layer

```typescript
// services/api.ts
import axios, { AxiosInstance, AxiosResponse } from 'axios';

class ApiService {
  private api: AxiosInstance;

  constructor(baseURL: string, apiKey: string) {
    this.api = axios.create({
      baseURL,
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      (error) => {
        if (error.response?.status === 401) {
          // Handle authentication error
          this.handleAuthError();
        }
        return Promise.reject(error);
      }
    );
  }

  private handleAuthError(): void {
    // Redirect to login or refresh token
    window.location.href = '/login';
  }

  async get<T>(url: string, params?: any): Promise<T> {
    const response = await this.api.get<T>(url, { params });
    return response.data;
  }

  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.api.post<T>(url, data);
    return response.data;
  }

  async put<T>(url: string, data?: any): Promise<T> {
    const response = await this.api.put<T>(url, data);
    return response.data;
  }

  async delete<T>(url: string): Promise<T> {
    const response = await this.api.delete<T>(url);
    return response.data;
  }
}

export default ApiService;
```

### 2. Variety Service

```typescript
// services/varietyService.ts
import ApiService from './api';
import { VarietyRecommendation, VarietyComparison, VarietyFilter } from '../types';

class VarietyService {
  private api: ApiService;

  constructor(apiService: ApiService) {
    this.api = apiService;
  }

  async getVarietyRecommendations(request: VarietyRecommendationRequest): Promise<VarietyRecommendation[]> {
    try {
      const response = await this.api.post<VarietyRecommendation[]>(
        '/api/v1/varieties/recommend',
        request
      );
      return response;
    } catch (error) {
      console.error('Error getting variety recommendations:', error);
      throw new Error('Failed to get variety recommendations');
    }
  }

  async compareVarieties(request: VarietyComparisonRequest): Promise<VarietyComparison> {
    try {
      const response = await this.api.post<VarietyComparison>(
        '/api/v1/varieties/compare',
        request
      );
      return response;
    } catch (error) {
      console.error('Error comparing varieties:', error);
      throw new Error('Failed to compare varieties');
    }
  }

  async filterVarieties(request: VarietyFilterRequest): Promise<VarietyRecommendation[]> {
    try {
      const response = await this.api.post<VarietyRecommendation[]>(
        '/api/v1/varieties/filter/advanced',
        request
      );
      return response;
    } catch (error) {
      console.error('Error filtering varieties:', error);
      throw new Error('Failed to filter varieties');
    }
  }

  async getVarietyDetails(varietyId: string): Promise<VarietyRecommendation> {
    try {
      const response = await this.api.get<VarietyRecommendation>(
        `/api/v1/varieties/${varietyId}/details`
      );
      return response;
    } catch (error) {
      console.error('Error getting variety details:', error);
      throw new Error('Failed to get variety details');
    }
  }

  async saveRecommendation(recommendation: VarietyRecommendation): Promise<void> {
    try {
      await this.api.post('/api/v1/recommendations/save', recommendation);
    } catch (error) {
      console.error('Error saving recommendation:', error);
      throw new Error('Failed to save recommendation');
    }
  }
}

export default VarietyService;
```

## React Components

### 1. Variety Selection Component

```typescript
// components/VarietySelection/VarietySelection.tsx
import React, { useState, useEffect } from 'react';
import { VarietyRecommendation, VarietyRecommendationRequest } from '../../types';
import VarietyService from '../../services/varietyService';
import VarietyList from './VarietyList';
import VarietyFilters from './VarietyFilters';
import LoadingSpinner from '../Shared/LoadingSpinner';
import ErrorBoundary from '../Shared/ErrorBoundary';

interface VarietySelectionProps {
  varietyService: VarietyService;
  farmData: FarmData;
  onVarietySelect: (variety: VarietyRecommendation) => void;
}

const VarietySelection: React.FC<VarietySelectionProps> = ({
  varietyService,
  farmData,
  onVarietySelect
}) => {
  const [varieties, setVarieties] = useState<VarietyRecommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<VarietyFilter>({});

  useEffect(() => {
    loadVarieties();
  }, [farmData, filters]);

  const loadVarieties = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const request: VarietyRecommendationRequest = {
        crop_id: farmData.crop_type,
        farm_data: {
          location: farmData.location,
          soil_data: farmData.soil_data,
          field_size_acres: farmData.field_size_acres,
          irrigation_available: farmData.irrigation_available
        },
        user_preferences: farmData.user_preferences,
        max_recommendations: 20
      };

      const recommendations = await varietyService.getVarietyRecommendations(request);
      setVarieties(recommendations);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters: VarietyFilter) => {
    setFilters(newFilters);
  };

  const handleVarietySelect = (variety: VarietyRecommendation) => {
    onVarietySelect(variety);
  };

  if (loading) {
    return <LoadingSpinner message="Loading variety recommendations..." />;
  }

  if (error) {
    return (
      <div className="error-container">
        <h3>Error Loading Varieties</h3>
        <p>{error}</p>
        <button onClick={loadVarieties} className="retry-button">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="variety-selection">
        <div className="variety-selection-header">
          <h2>Variety Recommendations</h2>
          <p>Based on your farm conditions and preferences</p>
        </div>
        
        <VarietyFilters
          filters={filters}
          onFilterChange={handleFilterChange}
          cropType={farmData.crop_type}
        />
        
        <VarietyList
          varieties={varieties}
          onVarietySelect={handleVarietySelect}
          farmData={farmData}
        />
      </div>
    </ErrorBoundary>
  );
};

export default VarietySelection;
```

### 2. Variety List Component

```typescript
// components/VarietySelection/VarietyList.tsx
import React from 'react';
import { VarietyRecommendation } from '../../types';
import VarietyCard from './VarietyCard';

interface VarietyListProps {
  varieties: VarietyRecommendation[];
  onVarietySelect: (variety: VarietyRecommendation) => void;
  farmData: FarmData;
}

const VarietyList: React.FC<VarietyListProps> = ({
  varieties,
  onVarietySelect,
  farmData
}) => {
  const handleVarietySelect = (variety: VarietyRecommendation) => {
    onVarietySelect(variety);
  };

  if (varieties.length === 0) {
    return (
      <div className="no-varieties">
        <h3>No Varieties Found</h3>
        <p>No varieties match your current criteria. Try adjusting your filters.</p>
      </div>
    );
  }

  return (
    <div className="variety-list">
      <div className="variety-list-header">
        <h3>Recommended Varieties ({varieties.length})</h3>
        <p>Sorted by suitability for your farm</p>
      </div>
      
      <div className="variety-grid">
        {varieties.map((variety) => (
          <VarietyCard
            key={variety.id}
            variety={variety}
            onSelect={handleVarietySelect}
            farmData={farmData}
          />
        ))}
      </div>
    </div>
  );
};

export default VarietyList;
```

### 3. Variety Card Component

```typescript
// components/VarietySelection/VarietyCard.tsx
import React from 'react';
import { VarietyRecommendation } from '../../types';

interface VarietyCardProps {
  variety: VarietyRecommendation;
  onSelect: (variety: VarietyRecommendation) => void;
  farmData: FarmData;
}

const VarietyCard: React.FC<VarietyCardProps> = ({
  variety,
  onSelect,
  farmData
}) => {
  const handleSelect = () => {
    onSelect(variety);
  };

  const getSuitabilityColor = (suitability: string) => {
    switch (suitability.toLowerCase()) {
      case 'excellent':
        return 'green';
      case 'very good':
        return 'blue';
      case 'good':
        return 'yellow';
      case 'fair':
        return 'orange';
      default:
        return 'gray';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'green';
    if (confidence >= 0.6) return 'yellow';
    return 'red';
  };

  return (
    <div className="variety-card" onClick={handleSelect}>
      <div className="variety-card-header">
        <h4>{variety.name}</h4>
        <span className="company">{variety.company}</span>
      </div>
      
      <div className="variety-card-body">
        <p className="description">{variety.description}</p>
        
        <div className="variety-metrics">
          <div className="metric">
            <span className="metric-label">Yield Potential:</span>
            <span className="metric-value">{variety.yield_potential}</span>
          </div>
          
          <div className="metric">
            <span className="metric-label">Maturity:</span>
            <span className="metric-value">{variety.maturity_days} days</span>
          </div>
          
          <div className="metric">
            <span className="metric-label">Disease Resistance:</span>
            <span className="metric-value">{variety.disease_resistance}</span>
          </div>
        </div>
        
        <div className="variety-traits">
          {variety.traits.map((trait, index) => (
            <span key={index} className="trait-badge">
              {trait.name}
            </span>
          ))}
        </div>
      </div>
      
      <div className="variety-card-footer">
        <div className="suitability-indicator">
          <span 
            className="suitability-badge"
            style={{ backgroundColor: getSuitabilityColor(variety.suitability) }}
          >
            {variety.suitability}
          </span>
        </div>
        
        <div className="confidence-indicator">
          <span 
            className="confidence-badge"
            style={{ backgroundColor: getConfidenceColor(variety.confidence) }}
          >
            {Math.round(variety.confidence * 100)}% confidence
          </span>
        </div>
      </div>
    </div>
  );
};

export default VarietyCard;
```

### 4. Variety Filters Component

```typescript
// components/VarietySelection/VarietyFilters.tsx
import React, { useState } from 'react';
import { VarietyFilter } from '../../types';

interface VarietyFiltersProps {
  filters: VarietyFilter;
  onFilterChange: (filters: VarietyFilter) => void;
  cropType: string;
}

const VarietyFilters: React.FC<VarietyFiltersProps> = ({
  filters,
  onFilterChange,
  cropType
}) => {
  const [localFilters, setLocalFilters] = useState<VarietyFilter>(filters);

  const handleFilterChange = (key: string, value: any) => {
    const newFilters = { ...localFilters, [key]: value };
    setLocalFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleReset = () => {
    setLocalFilters({});
    onFilterChange({});
  };

  return (
    <div className="variety-filters">
      <div className="filters-header">
        <h3>Filter Varieties</h3>
        <button onClick={handleReset} className="reset-button">
          Reset Filters
        </button>
      </div>
      
      <div className="filters-grid">
        <div className="filter-group">
          <label htmlFor="maturity-range">Maturity Range (days)</label>
          <div className="range-inputs">
            <input
              type="number"
              id="maturity-min"
              placeholder="Min"
              value={localFilters.maturity_range?.min || ''}
              onChange={(e) => handleFilterChange('maturity_range', {
                ...localFilters.maturity_range,
                min: e.target.value ? parseInt(e.target.value) : undefined
              })}
            />
            <span>to</span>
            <input
              type="number"
              id="maturity-max"
              placeholder="Max"
              value={localFilters.maturity_range?.max || ''}
              onChange={(e) => handleFilterChange('maturity_range', {
                ...localFilters.maturity_range,
                max: e.target.value ? parseInt(e.target.value) : undefined
              })}
            />
          </div>
        </div>
        
        <div className="filter-group">
          <label htmlFor="yield-min">Minimum Yield Potential</label>
          <input
            type="number"
            id="yield-min"
            placeholder="e.g., 180"
            value={localFilters.yield_potential_min || ''}
            onChange={(e) => handleFilterChange('yield_potential_min', 
              e.target.value ? parseFloat(e.target.value) : undefined
            )}
          />
        </div>
        
        <div className="filter-group">
          <label htmlFor="disease-resistance">Disease Resistance</label>
          <select
            id="disease-resistance"
            value={localFilters.disease_resistance || ''}
            onChange={(e) => handleFilterChange('disease_resistance', 
              e.target.value || undefined
            )}
          >
            <option value="">Any</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label htmlFor="traits">Required Traits</label>
          <div className="checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={localFilters.traits?.includes('drought_tolerance') || false}
                onChange={(e) => {
                  const traits = localFilters.traits || [];
                  if (e.target.checked) {
                    handleFilterChange('traits', [...traits, 'drought_tolerance']);
                  } else {
                    handleFilterChange('traits', traits.filter(t => t !== 'drought_tolerance'));
                  }
                }}
              />
              Drought Tolerance
            </label>
            <label>
              <input
                type="checkbox"
                checked={localFilters.traits?.includes('high_yield') || false}
                onChange={(e) => {
                  const traits = localFilters.traits || [];
                  if (e.target.checked) {
                    handleFilterChange('traits', [...traits, 'high_yield']);
                  } else {
                    handleFilterChange('traits', traits.filter(t => t !== 'high_yield'));
                  }
                }}
              />
              High Yield
            </label>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VarietyFilters;
```

## Custom Hooks

### 1. Variety Recommendations Hook

```typescript
// hooks/useVarietyRecommendations.ts
import { useState, useEffect, useCallback } from 'react';
import { VarietyRecommendation, VarietyRecommendationRequest } from '../types';
import VarietyService from '../services/varietyService';

interface UseVarietyRecommendationsReturn {
  varieties: VarietyRecommendation[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
  selectVariety: (variety: VarietyRecommendation) => void;
  selectedVariety: VarietyRecommendation | null;
}

export const useVarietyRecommendations = (
  varietyService: VarietyService,
  request: VarietyRecommendationRequest
): UseVarietyRecommendationsReturn => {
  const [varieties, setVarieties] = useState<VarietyRecommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedVariety, setSelectedVariety] = useState<VarietyRecommendation | null>(null);

  const fetchVarieties = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const recommendations = await varietyService.getVarietyRecommendations(request);
      setVarieties(recommendations);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [varietyService, request]);

  useEffect(() => {
    fetchVarieties();
  }, [fetchVarieties]);

  const selectVariety = useCallback((variety: VarietyRecommendation) => {
    setSelectedVariety(variety);
  }, []);

  return {
    varieties,
    loading,
    error,
    refetch: fetchVarieties,
    selectVariety,
    selectedVariety
  };
};
```

### 2. Variety Comparison Hook

```typescript
// hooks/useVarietyComparison.ts
import { useState, useCallback } from 'react';
import { VarietyComparison, VarietyComparisonRequest } from '../types';
import VarietyService from '../services/varietyService';

interface UseVarietyComparisonReturn {
  comparison: VarietyComparison | null;
  loading: boolean;
  error: string | null;
  compareVarieties: (request: VarietyComparisonRequest) => void;
  clearComparison: () => void;
}

export const useVarietyComparison = (
  varietyService: VarietyService
): UseVarietyComparisonReturn => {
  const [comparison, setComparison] = useState<VarietyComparison | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const compareVarieties = useCallback(async (request: VarietyComparisonRequest) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await varietyService.compareVarieties(request);
      setComparison(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [varietyService]);

  const clearComparison = useCallback(() => {
    setComparison(null);
    setError(null);
  }, []);

  return {
    comparison,
    loading,
    error,
    compareVarieties,
    clearComparison
  };
};
```

## TypeScript Types

### 1. Core Types

```typescript
// types/index.ts
export interface VarietyRecommendation {
  id: string;
  name: string;
  company: string;
  description: string;
  yield_potential: string;
  maturity_days: number;
  confidence: number;
  suitability: string;
  disease_resistance: string;
  traits: Trait[];
  regional_performance?: RegionalPerformance;
  economic_analysis?: EconomicAnalysis;
}

export interface Trait {
  name: string;
  category: string;
  description?: string;
}

export interface RegionalPerformance {
  yield_advantage: string;
  disease_rating: string;
  stress_tolerance: string;
}

export interface EconomicAnalysis {
  seed_cost_per_acre: number;
  expected_roi: number;
  break_even_yield: number;
  market_premium?: number;
}

export interface VarietyRecommendationRequest {
  crop_id: string;
  farm_data: FarmData;
  user_preferences?: UserPreferences;
  max_recommendations?: number;
}

export interface FarmData {
  location: Location;
  soil_data: SoilData;
  field_size_acres: number;
  irrigation_available: boolean;
  crop_type: string;
  user_preferences?: UserPreferences;
}

export interface Location {
  latitude: number;
  longitude: number;
  climate_zone?: string;
}

export interface SoilData {
  ph: number;
  organic_matter_percent: number;
  drainage: string;
  soil_type: string;
}

export interface UserPreferences {
  yield_priority: string;
  disease_resistance_priority: string;
  maturity_preference: string;
  seed_budget: number;
}

export interface VarietyFilter {
  maturity_range?: {
    min?: number;
    max?: number;
  };
  yield_potential_min?: number;
  disease_resistance?: string;
  traits?: string[];
  price_range?: {
    min?: number;
    max?: number;
  };
}

export interface VarietyComparisonRequest {
  variety_ids: string[];
  comparison_criteria: string[];
  farm_context: FarmData;
  analysis_options?: {
    include_economic_analysis?: boolean;
    include_regional_performance?: boolean;
    include_risk_assessment?: boolean;
  };
}

export interface VarietyComparison {
  comparison_id: string;
  varieties: VarietyComparisonItem[];
  comparison_summary: ComparisonSummary;
  detailed_comparison: DetailedComparison;
  recommendation?: ComparisonRecommendation;
}

export interface VarietyComparisonItem {
  id: string;
  name: string;
  company: string;
  scores: Record<string, number>;
  rank: number;
  detailed_analysis: Record<string, any>;
  economic_analysis?: EconomicAnalysis;
  regional_performance?: RegionalPerformance;
  risk_assessment?: RiskAssessment;
}

export interface ComparisonSummary {
  best_overall: string;
  best_yield: string;
  best_disease_resistance: string;
  best_economic_value: string;
  most_balanced: string;
}

export interface DetailedComparison {
  yield_potential: ComparisonDetail;
  disease_resistance: ComparisonDetail;
  economic_value: ComparisonDetail;
}

export interface ComparisonDetail {
  winner: string;
  range?: string;
  difference?: string;
  summary?: string;
}

export interface ComparisonRecommendation {
  primary_recommendation: string;
  reasoning: string;
  alternative_options: AlternativeOption[];
  considerations: string[];
}

export interface AlternativeOption {
  variety: string;
  reason: string;
}

export interface RiskAssessment {
  overall_risk: string;
  risk_factors: string[];
  mitigation_strategies: string[];
}
```

## Error Handling

### 1. Error Boundary Component

```typescript
// components/Shared/ErrorBoundary.tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>An error occurred while loading variety recommendations.</p>
          <button onClick={() => this.setState({ hasError: false })}>
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

### 2. Error Handling Utilities

```typescript
// utils/errorHandling.ts
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export const handleApiError = (error: any): string => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        return data.detail || 'Invalid request parameters';
      case 401:
        return 'Authentication required';
      case 403:
        return 'Insufficient permissions';
      case 404:
        return 'Resource not found';
      case 429:
        return 'Rate limit exceeded. Please try again later.';
      case 500:
        return 'Internal server error. Please try again later.';
      default:
        return data.detail || 'An unexpected error occurred';
    }
  } else if (error.request) {
    // Network error
    return 'Network error. Please check your connection.';
  } else {
    // Other error
    return error.message || 'An unexpected error occurred';
  }
};

export const isRetryableError = (error: any): boolean => {
  if (error.response) {
    const status = error.response.status;
    return status >= 500 || status === 429;
  }
  return false;
};
```

## Performance Optimization

### 1. Lazy Loading

```typescript
// utils/lazyLoading.ts
import { lazy, ComponentType } from 'react';

export const lazyLoadComponent = <T extends ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>
) => {
  return lazy(importFunc);
};

// Usage
const VarietyComparison = lazyLoadComponent(
  () => import('../components/VarietySelection/VarietyComparison')
);

const RecommendationEngine = lazyLoadComponent(
  () => import('../components/RecommendationEngine/RecommendationEngine')
);
```

### 2. Memoization

```typescript
// utils/memoization.ts
import { useMemo, useCallback } from 'react';

export const useMemoizedVarieties = (
  varieties: VarietyRecommendation[],
  filters: VarietyFilter
) => {
  return useMemo(() => {
    return varieties.filter(variety => {
      // Apply filters
      if (filters.maturity_range) {
        const { min, max } = filters.maturity_range;
        if (min && variety.maturity_days < min) return false;
        if (max && variety.maturity_days > max) return false;
      }
      
      if (filters.yield_potential_min) {
        const yieldValue = parseFloat(variety.yield_potential);
        if (yieldValue < filters.yield_potential_min) return false;
      }
      
      if (filters.disease_resistance) {
        if (variety.disease_resistance !== filters.disease_resistance) return false;
      }
      
      if (filters.traits && filters.traits.length > 0) {
        const varietyTraits = variety.traits.map(t => t.name.toLowerCase());
        const hasAllTraits = filters.traits.every(trait => 
          varietyTraits.some(vt => vt.includes(trait.toLowerCase()))
        );
        if (!hasAllTraits) return false;
      }
      
      return true;
    });
  }, [varieties, filters]);
};

export const useMemoizedCallbacks = (
  onVarietySelect: (variety: VarietyRecommendation) => void
) => {
  const handleVarietySelect = useCallback((variety: VarietyRecommendation) => {
    onVarietySelect(variety);
  }, [onVarietySelect]);
  
  return { handleVarietySelect };
};
```

### 3. Virtual Scrolling

```typescript
// components/VarietySelection/VirtualizedVarietyList.tsx
import React, { useMemo } from 'react';
import { FixedSizeList as List } from 'react-window';
import VarietyCard from './VarietyCard';

interface VirtualizedVarietyListProps {
  varieties: VarietyRecommendation[];
  onVarietySelect: (variety: VarietyRecommendation) => void;
  farmData: FarmData;
  height: number;
}

const VirtualizedVarietyList: React.FC<VirtualizedVarietyListProps> = ({
  varieties,
  onVarietySelect,
  farmData,
  height
}) => {
  const itemData = useMemo(() => ({
    varieties,
    onVarietySelect,
    farmData
  }), [varieties, onVarietySelect, farmData]);

  const Row = ({ index, style, data }: any) => {
    const { varieties, onVarietySelect, farmData } = data;
    const variety = varieties[index];
    
    return (
      <div style={style}>
        <VarietyCard
          variety={variety}
          onSelect={onVarietySelect}
          farmData={farmData}
        />
      </div>
    );
  };

  return (
    <List
      height={height}
      itemCount={varieties.length}
      itemSize={200}
      itemData={itemData}
    >
      {Row}
    </List>
  );
};

export default VirtualizedVarietyList;
```

## Testing

### 1. Component Tests

```typescript
// __tests__/VarietyCard.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import VarietyCard from '../components/VarietySelection/VarietyCard';
import { VarietyRecommendation } from '../types';

const mockVariety: VarietyRecommendation = {
  id: 'test-variety',
  name: 'Test Variety',
  company: 'Test Company',
  description: 'A test variety for testing',
  yield_potential: '180 bu/acre',
  maturity_days: 105,
  confidence: 0.9,
  suitability: 'Excellent',
  disease_resistance: 'high',
  traits: [
    { name: 'Drought Tolerance', category: 'resistance' },
    { name: 'High Yield', category: 'yield' }
  ]
};

const mockFarmData = {
  location: { latitude: 40.7128, longitude: -74.0060 },
  soil_data: { ph: 6.5, organic_matter_percent: 3.2, drainage: 'well_drained', soil_type: 'clay_loam' },
  field_size_acres: 100,
  irrigation_available: true,
  crop_type: 'corn'
};

describe('VarietyCard', () => {
  it('renders variety information correctly', () => {
    const mockOnSelect = jest.fn();
    
    render(
      <VarietyCard
        variety={mockVariety}
        onSelect={mockOnSelect}
        farmData={mockFarmData}
      />
    );
    
    expect(screen.getByText('Test Variety')).toBeInTheDocument();
    expect(screen.getByText('Test Company')).toBeInTheDocument();
    expect(screen.getByText('A test variety for testing')).toBeInTheDocument();
    expect(screen.getByText('180 bu/acre')).toBeInTheDocument();
    expect(screen.getByText('105 days')).toBeInTheDocument();
    expect(screen.getByText('Drought Tolerance')).toBeInTheDocument();
    expect(screen.getByText('High Yield')).toBeInTheDocument();
  });
  
  it('calls onSelect when clicked', () => {
    const mockOnSelect = jest.fn();
    
    render(
      <VarietyCard
        variety={mockVariety}
        onSelect={mockOnSelect}
        farmData={mockFarmData}
      />
    );
    
    fireEvent.click(screen.getByText('Test Variety'));
    expect(mockOnSelect).toHaveBeenCalledWith(mockVariety);
  });
});
```

### 2. Service Tests

```typescript
// __tests__/varietyService.test.ts
import VarietyService from '../services/varietyService';
import ApiService from '../services/api';
import { VarietyRecommendationRequest } from '../types';

// Mock the API service
jest.mock('../services/api');

describe('VarietyService', () => {
  let varietyService: VarietyService;
  let mockApiService: jest.Mocked<ApiService>;
  
  beforeEach(() => {
    mockApiService = new ApiService('http://localhost:8001', 'test-key') as jest.Mocked<ApiService>;
    varietyService = new VarietyService(mockApiService);
  });
  
  it('should get variety recommendations', async () => {
    const mockResponse = [
      {
        id: 'test-variety',
        name: 'Test Variety',
        company: 'Test Company',
        description: 'A test variety',
        yield_potential: '180 bu/acre',
        maturity_days: 105,
        confidence: 0.9,
        suitability: 'Excellent',
        disease_resistance: 'high',
        traits: []
      }
    ];
    
    mockApiService.post.mockResolvedValue(mockResponse);
    
    const request: VarietyRecommendationRequest = {
      crop_id: 'corn',
      farm_data: {
        location: { latitude: 40.7128, longitude: -74.0060 },
        soil_data: { ph: 6.5, organic_matter_percent: 3.2, drainage: 'well_drained', soil_type: 'clay_loam' },
        field_size_acres: 100,
        irrigation_available: true
      }
    };
    
    const result = await varietyService.getVarietyRecommendations(request);
    
    expect(mockApiService.post).toHaveBeenCalledWith('/api/v1/varieties/recommend', request);
    expect(result).toEqual(mockResponse);
  });
  
  it('should handle API errors', async () => {
    mockApiService.post.mockRejectedValue(new Error('API Error'));
    
    const request: VarietyRecommendationRequest = {
      crop_id: 'corn',
      farm_data: {
        location: { latitude: 40.7128, longitude: -74.0060 },
        soil_data: { ph: 6.5, organic_matter_percent: 3.2, drainage: 'well_drained', soil_type: 'clay_loam' },
        field_size_acres: 100,
        irrigation_available: true
      }
    };
    
    await expect(varietyService.getVarietyRecommendations(request)).rejects.toThrow('Failed to get variety recommendations');
  });
});
```

## Best Practices

### 1. Component Design

- Use functional components with hooks
- Implement proper error boundaries
- Use TypeScript for type safety
- Follow React best practices
- Implement proper loading states

### 2. State Management

- Use local state for component-specific data
- Use context for global state
- Implement proper state updates
- Use memoization for performance
- Handle async state properly

### 3. API Integration

- Implement proper error handling
- Use retry logic for failed requests
- Implement loading states
- Cache frequently accessed data
- Use proper authentication

### 4. Performance

- Implement lazy loading
- Use virtual scrolling for large lists
- Implement proper memoization
- Optimize re-renders
- Use efficient data structures

### 5. Testing

- Write comprehensive unit tests
- Test error scenarios
- Mock external dependencies
- Test user interactions
- Implement integration tests