// AFAS MongoDB Database Schema
// Autonomous Farm Advisory System
// Version: 1.0
// Date: December 2024

// Connect to the AFAS database
use afas_db;

// ============================================================================
// QUESTION RESPONSES COLLECTION
// ============================================================================

// Collection for storing complete question-response interactions
db.createCollection("question_responses", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["user_id", "question_type", "request_data", "response_data", "timestamp"],
            properties: {
                user_id: {
                    bsonType: "string",
                    description: "UUID of the user who asked the question"
                },
                farm_id: {
                    bsonType: "string",
                    description: "UUID of the farm context"
                },
                question_type: {
                    bsonType: "string",
                    enum: ["crop_selection", "soil_fertility", "crop_rotation", "nutrient_deficiency", 
                           "fertilizer_type", "application_method", "fertilizer_timing", "environmental_impact",
                           "cover_crops", "soil_ph", "micronutrients", "precision_agriculture", 
                           "drought_management", "deficiency_detection", "tillage_practices", 
                           "cost_optimization", "weather_integration", "testing_integration",
                           "sustainable_intensification", "policy_compliance"],
                    description: "Type of agricultural question"
                },
                request_data: {
                    bsonType: "object",
                    description: "Complete request parameters and context"
                },
                response_data: {
                    bsonType: "object",
                    required: ["recommendations", "confidence_score"],
                    properties: {
                        recommendations: {
                            bsonType: "array",
                            description: "Array of recommendation items"
                        },
                        confidence_score: {
                            bsonType: "double",
                            minimum: 0.0,
                            maximum: 1.0,
                            description: "Overall confidence in recommendations"
                        },
                        confidence_factors: {
                            bsonType: "object",
                            description: "Breakdown of confidence factors"
                        },
                        processing_metadata: {
                            bsonType: "object",
                            description: "Processing time, data sources, etc."
                        }
                    }
                },
                ai_explanation: {
                    bsonType: "object",
                    properties: {
                        explanation_text: {
                            bsonType: "string",
                            description: "Natural language explanation"
                        },
                        llm_model: {
                            bsonType: "string",
                            description: "LLM model used for explanation"
                        },
                        generation_time_ms: {
                            bsonType: "int",
                            description: "Time taken to generate explanation"
                        },
                        tokens_used: {
                            bsonType: "int",
                            description: "Number of tokens used"
                        }
                    }
                },
                user_feedback: {
                    bsonType: "object",
                    properties: {
                        rating: {
                            bsonType: "int",
                            minimum: 1,
                            maximum: 5,
                            description: "User rating of recommendation"
                        },
                        feedback_text: {
                            bsonType: "string",
                            description: "User feedback comments"
                        },
                        implemented: {
                            bsonType: "bool",
                            description: "Whether user implemented the recommendation"
                        },
                        implementation_notes: {
                            bsonType: "string",
                            description: "Notes on implementation"
                        },
                        feedback_date: {
                            bsonType: "date",
                            description: "Date feedback was provided"
                        }
                    }
                },
                timestamp: {
                    bsonType: "date",
                    description: "When the question was processed"
                },
                session_id: {
                    bsonType: "string",
                    description: "Session identifier for conversation tracking"
                }
            }
        }
    }
});

// ============================================================================
// EXTERNAL DATA CACHE COLLECTION
// ============================================================================

// Collection for caching external API responses
db.createCollection("external_data_cache", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["cache_key", "data_source", "data", "cached_at", "expires_at"],
            properties: {
                cache_key: {
                    bsonType: "string",
                    description: "Unique cache key for the data"
                },
                data_source: {
                    bsonType: "string",
                    enum: ["weather_api", "soil_database", "crop_database", "market_data", 
                           "government_programs", "extension_service"],
                    description: "Source of the cached data"
                },
                location: {
                    bsonType: "object",
                    properties: {
                        latitude: {
                            bsonType: "double",
                            minimum: -90,
                            maximum: 90
                        },
                        longitude: {
                            bsonType: "double",
                            minimum: -180,
                            maximum: 180
                        },
                        region: {
                            bsonType: "string",
                            description: "Geographic region identifier"
                        }
                    }
                },
                data: {
                    bsonType: "object",
                    description: "The cached data payload"
                },
                cached_at: {
                    bsonType: "date",
                    description: "When the data was cached"
                },
                expires_at: {
                    bsonType: "date",
                    description: "When the cached data expires"
                },
                api_endpoint: {
                    bsonType: "string",
                    description: "Original API endpoint"
                },
                request_parameters: {
                    bsonType: "object",
                    description: "Parameters used in the original request"
                }
            }
        }
    }
});

// ============================================================================
// AGRICULTURAL KNOWLEDGE BASE COLLECTION
// ============================================================================

// Collection for storing agricultural knowledge and best practices
db.createCollection("agricultural_knowledge", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["knowledge_id", "category", "content", "source", "created_at"],
            properties: {
                knowledge_id: {
                    bsonType: "string",
                    description: "Unique identifier for knowledge item"
                },
                category: {
                    bsonType: "string",
                    enum: ["crop_management", "soil_health", "nutrient_management", "pest_management",
                           "equipment_operation", "economic_analysis", "environmental_stewardship",
                           "regulatory_compliance", "best_practices"],
                    description: "Category of agricultural knowledge"
                },
                subcategory: {
                    bsonType: "string",
                    description: "More specific subcategory"
                },
                content: {
                    bsonType: "object",
                    required: ["title", "description"],
                    properties: {
                        title: {
                            bsonType: "string",
                            description: "Title of the knowledge item"
                        },
                        description: {
                            bsonType: "string",
                            description: "Detailed description"
                        },
                        guidelines: {
                            bsonType: "array",
                            items: {
                                bsonType: "string"
                            },
                            description: "Array of guideline statements"
                        },
                        calculations: {
                            bsonType: "object",
                            description: "Calculation formulas and parameters"
                        },
                        regional_variations: {
                            bsonType: "array",
                            items: {
                                bsonType: "object",
                                properties: {
                                    region: { bsonType: "string" },
                                    modifications: { bsonType: "string" }
                                }
                            }
                        }
                    }
                },
                source: {
                    bsonType: "object",
                    required: ["type", "name"],
                    properties: {
                        type: {
                            bsonType: "string",
                            enum: ["extension_service", "research_paper", "expert_knowledge", 
                                   "government_guideline", "industry_standard"],
                            description: "Type of source"
                        },
                        name: {
                            bsonType: "string",
                            description: "Name of the source"
                        },
                        url: {
                            bsonType: "string",
                            description: "URL reference if available"
                        },
                        publication_date: {
                            bsonType: "date",
                            description: "Publication date of source"
                        },
                        credibility_score: {
                            bsonType: "double",
                            minimum: 0.0,
                            maximum: 1.0,
                            description: "Credibility score of the source"
                        }
                    }
                },
                applicability: {
                    bsonType: "object",
                    properties: {
                        regions: {
                            bsonType: "array",
                            items: { bsonType: "string" },
                            description: "Applicable geographic regions"
                        },
                        crops: {
                            bsonType: "array",
                            items: { bsonType: "string" },
                            description: "Applicable crop types"
                        },
                        soil_types: {
                            bsonType: "array",
                            items: { bsonType: "string" },
                            description: "Applicable soil types"
                        },
                        farm_sizes: {
                            bsonType: "object",
                            properties: {
                                min_acres: { bsonType: "double" },
                                max_acres: { bsonType: "double" }
                            }
                        }
                    }
                },
                tags: {
                    bsonType: "array",
                    items: { bsonType: "string" },
                    description: "Tags for searchability"
                },
                created_at: {
                    bsonType: "date",
                    description: "When the knowledge was added"
                },
                updated_at: {
                    bsonType: "date",
                    description: "When the knowledge was last updated"
                },
                expert_validated: {
                    bsonType: "bool",
                    description: "Whether validated by agricultural expert"
                },
                validation_date: {
                    bsonType: "date",
                    description: "Date of expert validation"
                }
            }
        }
    }
});

// ============================================================================
// IMAGE ANALYSIS COLLECTION
// ============================================================================

// Collection for storing image analysis results
db.createCollection("image_analysis", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["analysis_id", "user_id", "image_metadata", "analysis_results", "created_at"],
            properties: {
                analysis_id: {
                    bsonType: "string",
                    description: "Unique identifier for analysis"
                },
                user_id: {
                    bsonType: "string",
                    description: "UUID of user who submitted image"
                },
                farm_id: {
                    bsonType: "string",
                    description: "UUID of associated farm"
                },
                field_id: {
                    bsonType: "string",
                    description: "UUID of associated field"
                },
                image_metadata: {
                    bsonType: "object",
                    required: ["filename", "file_size", "dimensions"],
                    properties: {
                        filename: { bsonType: "string" },
                        file_size: { bsonType: "int" },
                        dimensions: {
                            bsonType: "object",
                            properties: {
                                width: { bsonType: "int" },
                                height: { bsonType: "int" }
                            }
                        },
                        format: { bsonType: "string" },
                        capture_date: { bsonType: "date" },
                        gps_coordinates: {
                            bsonType: "object",
                            properties: {
                                latitude: { bsonType: "double" },
                                longitude: { bsonType: "double" }
                            }
                        },
                        camera_info: {
                            bsonType: "object",
                            properties: {
                                make: { bsonType: "string" },
                                model: { bsonType: "string" },
                                settings: { bsonType: "object" }
                            }
                        }
                    }
                },
                analysis_results: {
                    bsonType: "object",
                    required: ["deficiencies_detected", "confidence_scores"],
                    properties: {
                        deficiencies_detected: {
                            bsonType: "array",
                            items: {
                                bsonType: "object",
                                properties: {
                                    nutrient: { bsonType: "string" },
                                    severity: { 
                                        bsonType: "string",
                                        enum: ["mild", "moderate", "severe"]
                                    },
                                    confidence: { 
                                        bsonType: "double",
                                        minimum: 0.0,
                                        maximum: 1.0
                                    },
                                    affected_area_percent: { bsonType: "double" }
                                }
                            }
                        },
                        confidence_scores: {
                            bsonType: "object",
                            properties: {
                                overall: { bsonType: "double" },
                                image_quality: { bsonType: "double" },
                                lighting_conditions: { bsonType: "double" },
                                crop_visibility: { bsonType: "double" }
                            }
                        },
                        crop_stage: {
                            bsonType: "string",
                            description: "Detected crop growth stage"
                        },
                        recommendations: {
                            bsonType: "array",
                            items: {
                                bsonType: "object",
                                properties: {
                                    action: { bsonType: "string" },
                                    priority: { bsonType: "string" },
                                    timing: { bsonType: "string" }
                                }
                            }
                        }
                    }
                },
                processing_metadata: {
                    bsonType: "object",
                    properties: {
                        model_version: { bsonType: "string" },
                        processing_time_ms: { bsonType: "int" },
                        gpu_used: { bsonType: "bool" },
                        preprocessing_steps: { bsonType: "array" }
                    }
                },
                created_at: {
                    bsonType: "date",
                    description: "When the analysis was performed"
                }
            }
        }
    }
});

// ============================================================================
// CONVERSATION HISTORY COLLECTION
// ============================================================================

// Collection for storing AI conversation history
db.createCollection("conversation_history", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["session_id", "user_id", "messages", "created_at"],
            properties: {
                session_id: {
                    bsonType: "string",
                    description: "Unique session identifier"
                },
                user_id: {
                    bsonType: "string",
                    description: "UUID of the user"
                },
                farm_context: {
                    bsonType: "object",
                    properties: {
                        farm_id: { bsonType: "string" },
                        farm_name: { bsonType: "string" },
                        location: { bsonType: "object" }
                    }
                },
                messages: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        required: ["role", "content", "timestamp"],
                        properties: {
                            role: {
                                bsonType: "string",
                                enum: ["user", "assistant", "system"],
                                description: "Message sender role"
                            },
                            content: {
                                bsonType: "string",
                                description: "Message content"
                            },
                            timestamp: {
                                bsonType: "date",
                                description: "When message was sent"
                            },
                            metadata: {
                                bsonType: "object",
                                properties: {
                                    tokens_used: { bsonType: "int" },
                                    model_used: { bsonType: "string" },
                                    processing_time_ms: { bsonType: "int" }
                                }
                            }
                        }
                    }
                },
                session_metadata: {
                    bsonType: "object",
                    properties: {
                        total_messages: { bsonType: "int" },
                        total_tokens: { bsonType: "int" },
                        session_duration_minutes: { bsonType: "int" },
                        topics_discussed: { bsonType: "array" }
                    }
                },
                created_at: {
                    bsonType: "date",
                    description: "When the session started"
                },
                updated_at: {
                    bsonType: "date",
                    description: "When the session was last updated"
                },
                ended_at: {
                    bsonType: "date",
                    description: "When the session ended"
                }
            }
        }
    }
});

// ============================================================================
// SYSTEM ANALYTICS COLLECTION
// ============================================================================

// Collection for storing system usage analytics
db.createCollection("system_analytics", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["event_type", "timestamp", "data"],
            properties: {
                event_type: {
                    bsonType: "string",
                    enum: ["user_registration", "question_asked", "recommendation_generated",
                           "feedback_provided", "image_analyzed", "api_call", "error_occurred"],
                    description: "Type of system event"
                },
                user_id: {
                    bsonType: "string",
                    description: "UUID of user (if applicable)"
                },
                session_id: {
                    bsonType: "string",
                    description: "Session identifier"
                },
                data: {
                    bsonType: "object",
                    description: "Event-specific data payload"
                },
                performance_metrics: {
                    bsonType: "object",
                    properties: {
                        response_time_ms: { bsonType: "int" },
                        memory_usage_mb: { bsonType: "double" },
                        cpu_usage_percent: { bsonType: "double" },
                        database_queries: { bsonType: "int" }
                    }
                },
                timestamp: {
                    bsonType: "date",
                    description: "When the event occurred"
                },
                ip_address: {
                    bsonType: "string",
                    description: "Client IP address"
                },
                user_agent: {
                    bsonType: "string",
                    description: "Client user agent"
                }
            }
        }
    }
});

// ============================================================================
// CREATE INDEXES FOR PERFORMANCE
// ============================================================================

// Question responses indexes
db.question_responses.createIndex({ "user_id": 1 });
db.question_responses.createIndex({ "farm_id": 1 });
db.question_responses.createIndex({ "question_type": 1 });
db.question_responses.createIndex({ "timestamp": -1 });
db.question_responses.createIndex({ "response_data.confidence_score": -1 });
db.question_responses.createIndex({ "user_feedback.rating": 1 });

// External data cache indexes
db.external_data_cache.createIndex({ "cache_key": 1 }, { unique: true });
db.external_data_cache.createIndex({ "data_source": 1 });
db.external_data_cache.createIndex({ "expires_at": 1 });
db.external_data_cache.createIndex({ "location.latitude": 1, "location.longitude": 1 });

// Agricultural knowledge indexes
db.agricultural_knowledge.createIndex({ "knowledge_id": 1 }, { unique: true });
db.agricultural_knowledge.createIndex({ "category": 1, "subcategory": 1 });
db.agricultural_knowledge.createIndex({ "tags": 1 });
db.agricultural_knowledge.createIndex({ "applicability.regions": 1 });
db.agricultural_knowledge.createIndex({ "applicability.crops": 1 });
db.agricultural_knowledge.createIndex({ "expert_validated": 1 });

// Text search indexes
db.agricultural_knowledge.createIndex({ 
    "content.title": "text", 
    "content.description": "text", 
    "tags": "text" 
});

// Image analysis indexes
db.image_analysis.createIndex({ "analysis_id": 1 }, { unique: true });
db.image_analysis.createIndex({ "user_id": 1 });
db.image_analysis.createIndex({ "farm_id": 1 });
db.image_analysis.createIndex({ "created_at": -1 });
db.image_analysis.createIndex({ "analysis_results.deficiencies_detected.nutrient": 1 });

// Conversation history indexes
db.conversation_history.createIndex({ "session_id": 1 }, { unique: true });
db.conversation_history.createIndex({ "user_id": 1 });
db.conversation_history.createIndex({ "created_at": -1 });
db.conversation_history.createIndex({ "updated_at": -1 });

// System analytics indexes
db.system_analytics.createIndex({ "event_type": 1 });
db.system_analytics.createIndex({ "user_id": 1 });
db.system_analytics.createIndex({ "timestamp": -1 });
db.system_analytics.createIndex({ "session_id": 1 });

// Compound indexes for common queries
db.question_responses.createIndex({ "user_id": 1, "timestamp": -1 });
db.question_responses.createIndex({ "question_type": 1, "timestamp": -1 });
db.external_data_cache.createIndex({ "data_source": 1, "expires_at": 1 });

// ============================================================================
// SAMPLE DATA INSERTION
// ============================================================================

// Insert sample agricultural knowledge
db.agricultural_knowledge.insertMany([
    {
        knowledge_id: "corn_nitrogen_management_001",
        category: "nutrient_management",
        subcategory: "nitrogen",
        content: {
            title: "Corn Nitrogen Rate Calculation",
            description: "Standard method for calculating nitrogen fertilizer rates for corn production",
            guidelines: [
                "Base nitrogen rate on realistic yield goal",
                "Credit nitrogen from previous legume crops",
                "Account for soil organic matter mineralization",
                "Consider soil test nitrate levels"
            ],
            calculations: {
                formula: "N_rate = (Yield_goal * 1.2) - Legume_credit - Soil_N_credit - OM_credit",
                parameters: {
                    yield_goal_multiplier: 1.2,
                    soybean_credit: 40,
                    alfalfa_credit: 100,
                    om_mineralization_rate: 20
                }
            }
        },
        source: {
            type: "extension_service",
            name: "Iowa State University Extension",
            url: "https://extension.iastate.edu/corn/nitrogen",
            publication_date: new Date("2024-01-01"),
            credibility_score: 0.95
        },
        applicability: {
            regions: ["midwest", "corn_belt"],
            crops: ["corn"],
            soil_types: ["silt_loam", "clay_loam", "sandy_loam"]
        },
        tags: ["nitrogen", "corn", "fertilizer", "calculation", "yield"],
        created_at: new Date(),
        expert_validated: true,
        validation_date: new Date()
    },
    {
        knowledge_id: "soil_ph_management_001",
        category: "soil_health",
        subcategory: "ph_management",
        content: {
            title: "Soil pH Management for Optimal Nutrient Availability",
            description: "Guidelines for managing soil pH to optimize nutrient availability for crops",
            guidelines: [
                "Maintain pH between 6.0-7.0 for most crops",
                "Apply lime 6-12 months before planting",
                "Consider buffer pH for lime rate calculations",
                "Monitor pH changes over time"
            ],
            calculations: {
                lime_rate_formula: "Lime_rate = (Target_pH - Current_pH) * Buffer_pH_factor * CEC",
                typical_lime_rates: {
                    sandy_soil: "1-2 tons/acre per 0.5 pH unit",
                    clay_soil: "2-4 tons/acre per 0.5 pH unit"
                }
            }
        },
        source: {
            type: "extension_service",
            name: "University of Wisconsin Extension",
            url: "https://extension.wisc.edu/soil-ph",
            publication_date: new Date("2023-12-01"),
            credibility_score: 0.92
        },
        applicability: {
            regions: ["midwest", "northeast", "southeast"],
            crops: ["corn", "soybean", "wheat", "alfalfa"],
            soil_types: ["all"]
        },
        tags: ["soil_ph", "lime", "nutrient_availability", "soil_management"],
        created_at: new Date(),
        expert_validated: true,
        validation_date: new Date()
    }
]);

// Insert sample external data cache entry
db.external_data_cache.insertOne({
    cache_key: "weather_ames_ia_2024_12_09",
    data_source: "weather_api",
    location: {
        latitude: 42.0308,
        longitude: -93.6319,
        region: "iowa"
    },
    data: {
        current_conditions: {
            temperature_f: 32,
            humidity_percent: 75,
            wind_speed_mph: 8,
            precipitation_inches: 0.0
        },
        forecast: [
            {
                date: "2024-12-09",
                high_f: 35,
                low_f: 28,
                precipitation_chance: 20
            }
        ]
    },
    cached_at: new Date(),
    expires_at: new Date(Date.now() + 3600000), // 1 hour from now
    api_endpoint: "https://api.weather.gov/points/42.0308,-93.6319",
    request_parameters: {
        lat: 42.0308,
        lon: -93.6319,
        units: "imperial"
    }
});

print("MongoDB schema and collections created successfully!");
print("Collections created:");
print("- question_responses");
print("- external_data_cache");
print("- agricultural_knowledge");
print("- image_analysis");
print("- conversation_history");
print("- system_analytics");
print("");
print("Indexes created for optimal query performance");
print("Sample data inserted for testing");