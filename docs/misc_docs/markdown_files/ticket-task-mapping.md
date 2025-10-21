# Ticket-to-Task ID Mapping Guide

This document provides the complete mapping between tickets in `docs/tickets.md` and task sections in `docs/checklist.md` for AI coding agents.

## Mapping Format

Tasks should be prefixed with: `TICKET-XXX_original-task-id`

## Complete Ticket-to-Task Mapping

### Foundation Tickets (TICKET-001 to TICKET-011)

#### TICKET-001: Climate Zone Data Service Implementation
**Maps to**: `climate-zone-detection-*` sections
- TICKET-001_climate-zone-detection-1.* (Service Implementation)
- TICKET-001_climate-zone-detection-3.* (Manual Specification)
- TICKET-001_climate-zone-detection-4.* (Data Integration)
- TICKET-001_climate-zone-detection-5.* (Frontend Interface)
- TICKET-001_climate-zone-detection-6.* (API Endpoints)
- TICKET-001_climate-zone-detection-7.* (Data Sources)
- TICKET-001_climate-zone-detection-9.* (Crop Integration)
- TICKET-001_climate-zone-detection-11.* (Documentation)

#### TICKET-002: Coordinate-Based Climate Zone Detection
**Maps to**: `climate-zone-detection-*` sections
- TICKET-002_climate-zone-detection-2.* (Auto-Detection Logic)
- TICKET-002_climate-zone-detection-8.* (Validation and Quality)

#### TICKET-003: pH Management Service Structure
**Maps to**: `soil-ph-management-*` sections
- TICKET-003_soil-ph-management-1.* (Service Structure)
- TICKET-003_soil-ph-management-2.* (Data Input/Validation)
- TICKET-003_soil-ph-management-3.* (Crop pH Database)
- TICKET-003_soil-ph-management-5.* (Soil Type Integration)
- TICKET-003_soil-ph-management-8.* (Education System)
- TICKET-003_soil-ph-management-9.* (API Endpoints)
- TICKET-003_soil-ph-management-11.* (UI Components)
- TICKET-003_soil-ph-management-12.* (System Integration)

#### TICKET-004: pH Adjustment Calculation Engine
**Maps to**: `soil-ph-management-*` sections
- TICKET-004_soil-ph-management-4.* (Calculation Engine)
- TICKET-004_soil-ph-management-6.* (Timing Recommendations)
- TICKET-004_soil-ph-management-7.* (Timeline Predictions)

#### TICKET-005: Crop Database Enhancement
**Maps to**: `crop-variety-recommendations-*` sections
- TICKET-005_crop-variety-recommendations-1.* (Database Enhancement)
- TICKET-005_crop-variety-recommendations-2.* through 15.* (All crop variety tasks)

#### TICKET-006: Market Price Integration System
**Maps to**: `fertilizer-strategy-optimization-*` sections
- TICKET-006_fertilizer-strategy-optimization-1.* (Market Price Integration)
- TICKET-006_fertilizer-strategy-optimization-2.* through 10.* (All optimization tasks)

#### TICKET-007: Visual Symptom Analysis System
**Maps to**: `nutrient-deficiency-detection-*` sections
- TICKET-007_nutrient-deficiency-detection-1.* through 10.* (All deficiency detection tasks)

#### TICKET-008: Location Management API Endpoints
**Maps to**: `farm-location-input-*` sections
- TICKET-008_farm-location-input-1.* through 15.* (All location management tasks)

#### TICKET-009: Weather Data Integration System
**Maps to**: `weather-impact-analysis-*` sections
- TICKET-009_weather-impact-analysis-1.* through 15.* (All weather analysis tasks)

#### TICKET-010: Farm Profile Management Interface
**Maps to**: `farm-location-input-*` sections (UI components)
- TICKET-010_farm-location-input-10.* (Field Management UI)
- TICKET-010_farm-location-input-11.* (Mobile-Responsive Design)

#### TICKET-011: Comprehensive Testing Framework
**Maps to**: Testing sections across all features
- TICKET-011_*-testing-* (All testing and validation tasks across features)
- TICKET-011_climate-zone-detection-10.*
- TICKET-011_soil-ph-management-10.*
- TICKET-011_*-comprehensive-testing-*

### Comprehensive Coverage Tickets (TICKET-012 to TICKET-024)

#### TICKET-012: Multi-Year Rotation Optimization Engine
**Maps to**: `crop-rotation-planning-*` sections
- TICKET-012_crop-rotation-planning-1.* through 10.* (All rotation planning tasks)

#### TICKET-013: Cover Crop Selection and Integration System
**Maps to**: `cover-crop-selection-*` sections
- TICKET-013_cover-crop-selection-1.* through 14.* (All cover crop tasks)

#### TICKET-014: Drought Resilience and Water Conservation System
**Maps to**: `drought-management-*` sections
- TICKET-014_drought-management-1.* through 15.* (All drought management tasks)

#### TICKET-015: Precision Agriculture ROI Analysis System
**Maps to**: `precision-agriculture-roi-*` sections
- TICKET-015_precision-agriculture-roi-1.* through 5.* (All precision ag ROI tasks)

#### TICKET-016: Micronutrient Assessment and Management System
**Maps to**: `micronutrient-management-*` sections
- TICKET-016_micronutrient-management-1.* through 15.* (All micronutrient tasks)

#### TICKET-017: Laboratory Test Integration System
**Maps to**: `soil-tissue-test-integration-*` sections
- TICKET-017_soil-tissue-test-integration-1.* through 15.* (All lab integration tasks)

#### TICKET-018: Tillage Practice Optimization System
**Maps to**: `tillage-practice-recommendations-*` sections
- TICKET-018_tillage-practice-recommendations-1.* through 15.* (All tillage tasks)

#### TICKET-019: Sustainable Yield Optimization System
**Maps to**: `sustainable-intensification-*` sections
- TICKET-019_sustainable-intensification-1.* through 5.* (All sustainability tasks)

#### TICKET-020: Government Program Integration System
**Maps to**: `government-program-integration-*` sections
- TICKET-020_government-program-integration-1.* through 5.* (All policy tasks)

#### TICKET-021: Mobile Field Application
**Maps to**: `mobile-field-access-*` sections
- TICKET-021_mobile-field-access-1.* through 5.* (All mobile access tasks)
- Also maps to mobile components across other features:
  - TICKET-021_*-mobile-* (Mobile interface tasks in other sections)

#### TICKET-022: Recommendation History and Outcome Tracking
**Maps to**: `recommendation-tracking-*` sections
- TICKET-022_recommendation-tracking-1.* through 5.* (All tracking tasks)

#### TICKET-023: Fertilizer Type Selection and Application Method Optimization
**Maps to**: Multiple fertilizer sections
- TICKET-023_fertilizer-type-selection-1.* through 13.* (Type selection tasks)
- TICKET-023_fertilizer-application-method-1.* through 13.* (Application method tasks)

#### TICKET-024: Environmental Impact Assessment and Runoff Prevention
**Maps to**: `runoff-prevention-*` sections
- TICKET-024_runoff-prevention-1.* through 14.* (All runoff prevention tasks)

## Implementation Status

### ✅ Completed Sections (Updated with Ticket IDs):
- Climate Zone Detection (TICKET-001, TICKET-002)
- Soil pH Management (TICKET-003, TICKET-004)
- Cover Crop Selection (TICKET-013) - Partially updated

### ⏳ Remaining Sections to Update:
- Crop Rotation Planning (TICKET-012)
- Crop Type Filtering (TICKET-005 related)
- Crop Variety Recommendations (TICKET-005)
- Drought Management (TICKET-014)
- Farm Location Input (TICKET-008, TICKET-010)
- Fertilizer Application Method (TICKET-023)
- Fertilizer Strategy Optimization (TICKET-006)
- Fertilizer Timing Optimization (TICKET-006, TICKET-023)
- Fertilizer Type Selection (TICKET-023)
- Micronutrient Management (TICKET-016)
- Nutrient Deficiency Detection (TICKET-007)
- Soil Fertility Assessment (TICKET-003, TICKET-004, TICKET-017)
- Runoff Prevention (TICKET-024)
- Soil Tissue Test Integration (TICKET-017)
- Tillage Practice Recommendations (TICKET-018)
- Variety Suitability Explanations (TICKET-005)
- Variety Yield Disease Planting (TICKET-005)
- Weather Impact Analysis (TICKET-009)
- Precision Agriculture ROI Assessment (TICKET-015)
- Sustainable Intensification (TICKET-019)
- Government Program Integration (TICKET-020)
- Mobile Field Access (TICKET-021)
- Recommendation History and Tracking (TICKET-022)

## Benefits for AI Coding Agents

With ticket-prefixed task IDs, AI coding agents can:

1. **Direct Traceability**: Instantly map any task to its parent ticket specification
2. **Context Awareness**: Understand which technical requirements apply to each task
3. **Dependency Management**: Identify related tasks within the same ticket
4. **Progress Tracking**: Monitor ticket completion by tracking prefixed tasks
5. **Quality Assurance**: Validate task completion against ticket acceptance criteria

## Next Steps

1. **Complete ID Updates**: Systematically update all remaining 1,400+ task IDs
2. **Validation**: Ensure all tasks map to appropriate tickets
3. **Documentation**: Update plan.md references to use new task IDs
4. **Tool Integration**: Configure project management tools to recognize new ID format

This mapping ensures complete traceability from user stories through tickets to individual implementation tasks.
