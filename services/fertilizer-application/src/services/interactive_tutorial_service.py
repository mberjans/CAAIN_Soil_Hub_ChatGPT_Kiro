"""
Interactive Tutorial Service for Fertilizer Application Methods.

This service provides interactive tutorials, simulations, and step-by-step guides
for different fertilizer application methods including broadcast, band, foliar,
and injection applications.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4
from datetime import datetime

from src.models.educational_models import (
    InteractiveSimulation, EducationalContent, ContentType, ContentCategory,
    DifficultyLevel, LearningObjective, AssessmentQuestion, UserProfile
)
from src.models.application_models import ApplicationMethodType, EquipmentType, FertilizerForm

logger = logging.getLogger(__name__)


class InteractiveTutorialService:
    """Service for interactive tutorials and simulations for fertilizer application methods."""
    
    def __init__(self):
        self.tutorial_database = {}
        self.simulation_scenarios = {}
        self.assessment_questions = {}
        self._initialize_tutorial_database()
        self._initialize_simulation_scenarios()
        self._initialize_assessment_questions()
    
    def _initialize_tutorial_database(self):
        """Initialize comprehensive tutorial database."""
        self.tutorial_database = {
            ApplicationMethodType.BROADCAST: {
                "basic_tutorial": {
                    "tutorial_id": "broadcast_basic_tutorial",
                    "title": "Broadcast Application: Complete Beginner's Guide",
                    "description": "Step-by-step interactive tutorial for broadcast fertilizer application",
                    "difficulty_level": DifficultyLevel.BEGINNER,
                    "estimated_duration_minutes": 45,
                    "learning_objectives": [
                        LearningObjective(
                            objective_id="broadcast_basic_1",
                            description="Understand broadcast application principles",
                            category="knowledge"
                        ),
                        LearningObjective(
                            objective_id="broadcast_basic_2",
                            description="Learn equipment setup and calibration",
                            category="skill"
                        ),
                        LearningObjective(
                            objective_id="broadcast_basic_3",
                            description="Master safety protocols",
                            category="safety"
                        )
                    ],
                    "steps": [
                        {
                            "step_id": "step_1",
                            "title": "Introduction to Broadcast Application",
                            "content": {
                                "text": "Broadcast application involves spreading fertilizer uniformly across the entire field surface. This method is ideal for large fields and provides quick, efficient coverage.",
                                "interactive_elements": [
                                    {
                                        "type": "animation",
                                        "content": "Field coverage visualization",
                                        "description": "Watch how fertilizer spreads across the field"
                                    },
                                    {
                                        "type": "quiz",
                                        "question": "What is the primary advantage of broadcast application?",
                                        "options": ["Precision", "Speed", "Efficiency", "Cost"],
                                        "correct_answer": "Speed",
                                        "explanation": "Broadcast application is primarily valued for its speed and ability to cover large areas quickly."
                                    }
                                ]
                            },
                            "estimated_time_minutes": 5
                        },
                        {
                            "step_id": "step_2",
                            "title": "Equipment Selection and Setup",
                            "content": {
                                "text": "Choose the right spreader for your fertilizer type and field size. Proper setup ensures accurate application.",
                                "interactive_elements": [
                                    {
                                        "type": "equipment_selector",
                                        "description": "Select appropriate spreader based on field size and fertilizer type",
                                        "options": [
                                            {"equipment": "Small Spreader", "field_size": "1-50 acres", "fertilizer": "Granular"},
                                            {"equipment": "Large Spreader", "field_size": "50+ acres", "fertilizer": "Granular"},
                                            {"equipment": "Broadcast Spreader", "field_size": "Any size", "fertilizer": "Organic"}
                                        ]
                                    },
                                    {
                                        "type": "simulation",
                                        "description": "Practice equipment setup",
                                        "scenarios": ["Calibration", "Loading", "Safety check"]
                                    }
                                ]
                            },
                            "estimated_time_minutes": 10
                        },
                        {
                            "step_id": "step_3",
                            "title": "Calibration Process",
                            "content": {
                                "text": "Proper calibration ensures accurate fertilizer application rates. Follow these steps carefully.",
                                "interactive_elements": [
                                    {
                                        "type": "step_by_step_guide",
                                        "steps": [
                                            "Measure test area (100 ft x 100 ft)",
                                            "Set spreader to recommended rate",
                                            "Apply fertilizer to test area",
                                            "Weigh collected fertilizer",
                                            "Calculate actual application rate",
                                            "Adjust spreader settings if needed"
                                        ]
                                    },
                                    {
                                        "type": "calculator",
                                        "description": "Calibration rate calculator",
                                        "formula": "Rate (lbs/acre) = (Collected weight × 43,560) / Test area (sq ft)"
                                    }
                                ]
                            },
                            "estimated_time_minutes": 15
                        },
                        {
                            "step_id": "step_4",
                            "title": "Application Techniques",
                            "content": {
                                "text": "Learn proper application techniques for uniform coverage and efficiency.",
                                "interactive_elements": [
                                    {
                                        "type": "field_pattern_simulator",
                                        "description": "Practice field application patterns",
                                        "patterns": ["Parallel passes", "Overlap management", "Boundary handling"]
                                    },
                                    {
                                        "type": "wind_assessment",
                                        "description": "Learn to assess wind conditions",
                                        "scenarios": ["Calm conditions", "Light wind", "Strong wind", "Variable wind"]
                                    }
                                ]
                            },
                            "estimated_time_minutes": 10
                        },
                        {
                            "step_id": "step_5",
                            "title": "Safety and Environmental Considerations",
                            "content": {
                                "text": "Safety is paramount in fertilizer application. Follow all safety protocols and environmental guidelines.",
                                "interactive_elements": [
                                    {
                                        "type": "safety_checklist",
                                        "items": [
                                            "Wear appropriate PPE",
                                            "Check equipment safety features",
                                            "Ensure proper ventilation",
                                            "Have emergency procedures ready",
                                            "Follow environmental regulations"
                                        ]
                                    },
                                    {
                                        "type": "environmental_scenarios",
                                        "description": "Practice environmental protection",
                                        "scenarios": ["Buffer zones", "Runoff prevention", "Weather monitoring"]
                                    }
                                ]
                            },
                            "estimated_time_minutes": 5
                        }
                    ]
                },
                "advanced_tutorial": {
                    "tutorial_id": "broadcast_advanced_tutorial",
                    "title": "Advanced Broadcast Application Techniques",
                    "description": "Advanced techniques for experienced operators",
                    "difficulty_level": DifficultyLevel.ADVANCED,
                    "estimated_duration_minutes": 60,
                    "learning_objectives": [
                        LearningObjective(
                            objective_id="broadcast_adv_1",
                            description="Master precision broadcast techniques",
                            category="skill"
                        ),
                        LearningObjective(
                            objective_id="broadcast_adv_2",
                            description="Optimize application efficiency",
                            category="optimization"
                        )
                    ],
                    "steps": [
                        {
                            "step_id": "adv_step_1",
                            "title": "GPS-Guided Precision Application",
                            "content": {
                                "text": "Learn to use GPS guidance systems for precise application patterns.",
                                "interactive_elements": [
                                    {
                                        "type": "gps_simulator",
                                        "description": "Practice GPS-guided application",
                                        "features": ["Auto-steer", "Section control", "Rate control", "Overlap management"]
                                    }
                                ]
                            },
                            "estimated_time_minutes": 20
                        },
                        {
                            "step_id": "adv_step_2",
                            "title": "Variable Rate Application",
                            "content": {
                                "text": "Implement variable rate application based on soil test results and yield maps.",
                                "interactive_elements": [
                                    {
                                        "type": "vr_simulator",
                                        "description": "Variable rate application simulator",
                                        "scenarios": ["Soil test integration", "Yield map analysis", "Rate optimization"]
                                    }
                                ]
                            },
                            "estimated_time_minutes": 25
                        },
                        {
                            "step_id": "adv_step_3",
                            "title": "Efficiency Optimization",
                            "content": {
                                "text": "Optimize application efficiency through advanced techniques and equipment management.",
                                "interactive_elements": [
                                    {
                                        "type": "efficiency_calculator",
                                        "description": "Calculate application efficiency metrics",
                                        "metrics": ["Coverage uniformity", "Time efficiency", "Fuel consumption", "Labor requirements"]
                                    }
                                ]
                            },
                            "estimated_time_minutes": 15
                        }
                    ]
                }
            },
            
            ApplicationMethodType.BAND: {
                "basic_tutorial": {
                    "tutorial_id": "band_basic_tutorial",
                    "title": "Band Application: Complete Guide",
                    "description": "Interactive tutorial for band fertilizer application",
                    "difficulty_level": DifficultyLevel.INTERMEDIATE,
                    "estimated_duration_minutes": 50,
                    "learning_objectives": [
                        LearningObjective(
                            objective_id="band_basic_1",
                            description="Understand band application principles",
                            category="knowledge"
                        ),
                        LearningObjective(
                            objective_id="band_basic_2",
                            description="Learn placement optimization",
                            category="skill"
                        )
                    ],
                    "steps": [
                        {
                            "step_id": "band_step_1",
                            "title": "Band Application Principles",
                            "content": {
                                "text": "Band application places fertilizer in concentrated bands near the seed or plant roots for improved efficiency.",
                                "interactive_elements": [
                                    {
                                        "type": "placement_simulator",
                                        "description": "Practice fertilizer placement",
                                        "scenarios": ["Seed placement", "Root zone placement", "Side dressing"]
                                    }
                                ]
                            },
                            "estimated_time_minutes": 15
                        },
                        {
                            "step_id": "band_step_2",
                            "title": "Equipment Setup and Calibration",
                            "content": {
                                "text": "Proper equipment setup ensures accurate band placement and application rates.",
                                "interactive_elements": [
                                    {
                                        "type": "equipment_configurator",
                                        "description": "Configure banding equipment",
                                        "parameters": ["Band width", "Band depth", "Spacing", "Rate"]
                                    }
                                ]
                            },
                            "estimated_time_minutes": 20
                        },
                        {
                            "step_id": "band_step_3",
                            "title": "Application Techniques",
                            "content": {
                                "text": "Master band application techniques for different crops and field conditions.",
                                "interactive_elements": [
                                    {
                                        "type": "crop_specific_guide",
                                        "description": "Crop-specific banding techniques",
                                        "crops": ["Corn", "Soybeans", "Wheat", "Vegetables"]
                                    }
                                ]
                            },
                            "estimated_time_minutes": 15
                        }
                    ]
                }
            },
            
            ApplicationMethodType.FOLIAR: {
                "basic_tutorial": {
                    "tutorial_id": "foliar_basic_tutorial",
                    "title": "Foliar Application: Complete Guide",
                    "description": "Interactive tutorial for foliar fertilizer application",
                    "difficulty_level": DifficultyLevel.INTERMEDIATE,
                    "estimated_duration_minutes": 40,
                    "learning_objectives": [
                        LearningObjective(
                            objective_id="foliar_basic_1",
                            description="Understand foliar absorption mechanisms",
                            category="knowledge"
                        ),
                        LearningObjective(
                            objective_id="foliar_basic_2",
                            description="Learn timing optimization",
                            category="skill"
                        ),
                        LearningObjective(
                            objective_id="foliar_basic_3",
                            description="Master phytotoxicity prevention",
                            category="safety"
                        )
                    ],
                    "steps": [
                        {
                            "step_id": "foliar_step_1",
                            "title": "Foliar Absorption Principles",
                            "content": {
                                "text": "Foliar application delivers nutrients directly to plant leaves for rapid uptake and correction of deficiencies.",
                                "interactive_elements": [
                                    {
                                        "type": "absorption_simulator",
                                        "description": "Visualize nutrient absorption through leaves",
                                        "factors": ["Stomata", "Cuticle", "Leaf surface", "Environmental conditions"]
                                    }
                                ]
                            },
                            "estimated_time_minutes": 10
                        },
                        {
                            "step_id": "foliar_step_2",
                            "title": "Optimal Timing and Conditions",
                            "content": {
                                "text": "Timing is critical for foliar application success. Learn to identify optimal conditions.",
                                "interactive_elements": [
                                    {
                                        "type": "timing_optimizer",
                                        "description": "Determine optimal application timing",
                                        "factors": ["Growth stage", "Weather conditions", "Plant stress", "Nutrient demand"]
                                    }
                                ]
                            },
                            "estimated_time_minutes": 15
                        },
                        {
                            "step_id": "foliar_step_3",
                            "title": "Sprayer Setup and Calibration",
                            "content": {
                                "text": "Proper sprayer setup ensures effective coverage and prevents phytotoxicity.",
                                "interactive_elements": [
                                    {
                                        "type": "sprayer_configurator",
                                        "description": "Configure sprayer for foliar application",
                                        "parameters": ["Nozzle selection", "Pressure", "Volume", "Coverage"]
                                    }
                                ]
                            },
                            "estimated_time_minutes": 10
                        },
                        {
                            "step_id": "foliar_step_4",
                            "title": "Phytotoxicity Prevention",
                            "content": {
                                "text": "Learn to prevent phytotoxicity through proper formulation and application techniques.",
                                "interactive_elements": [
                                    {
                                        "type": "phytotoxicity_assessor",
                                        "description": "Assess phytotoxicity risk",
                                        "factors": ["Concentration", "Environmental stress", "Plant sensitivity", "Formulation"]
                                    }
                                ]
                            },
                            "estimated_time_minutes": 5
                        }
                    ]
                }
            },
            
            ApplicationMethodType.INJECTION: {
                "basic_tutorial": {
                    "tutorial_id": "injection_basic_tutorial",
                    "title": "Injection Application: Complete Guide",
                    "description": "Interactive tutorial for injection fertilizer application",
                    "difficulty_level": DifficultyLevel.ADVANCED,
                    "estimated_duration_minutes": 55,
                    "learning_objectives": [
                        LearningObjective(
                            objective_id="injection_basic_1",
                            description="Understand injection principles",
                            category="knowledge"
                        ),
                        LearningObjective(
                            objective_id="injection_basic_2",
                            description="Learn depth optimization",
                            category="skill"
                        )
                    ],
                    "steps": [
                        {
                            "step_id": "injection_step_1",
                            "title": "Injection Application Principles",
                            "content": {
                                "text": "Injection application places fertilizer directly into the soil for improved efficiency and reduced losses.",
                                "interactive_elements": [
                                    {
                                        "type": "injection_simulator",
                                        "description": "Practice injection techniques",
                                        "scenarios": ["Depth placement", "Spacing optimization", "Rate control"]
                                    }
                                ]
                            },
                            "estimated_time_minutes": 20
                        },
                        {
                            "step_id": "injection_step_2",
                            "title": "Equipment Setup and Calibration",
                            "content": {
                                "text": "Proper injection equipment setup ensures accurate placement and application rates.",
                                "interactive_elements": [
                                    {
                                        "type": "injection_configurator",
                                        "description": "Configure injection equipment",
                                        "parameters": ["Injection depth", "Spacing", "Rate", "Pressure"]
                                    }
                                ]
                            },
                            "estimated_time_minutes": 20
                        },
                        {
                            "step_id": "injection_step_3",
                            "title": "Soil Conditions and Timing",
                            "content": {
                                "text": "Soil conditions and timing significantly affect injection application success.",
                                "interactive_elements": [
                                    {
                                        "type": "soil_condition_assessor",
                                        "description": "Assess soil conditions for injection",
                                        "factors": ["Moisture", "Temperature", "Compaction", "Organic matter"]
                                    }
                                ]
                            },
                            "estimated_time_minutes": 15
                        }
                    ]
                }
            }
        }
    
    def _initialize_simulation_scenarios(self):
        """Initialize simulation scenarios for interactive tutorials."""
        self.simulation_scenarios = {
            "broadcast_field_simulation": {
                "scenario_id": "broadcast_field_simulation",
                "title": "Broadcast Field Application Simulation",
                "description": "Interactive simulation of broadcast application across a field",
                "difficulty_level": DifficultyLevel.INTERMEDIATE,
                "estimated_duration_minutes": 30,
                "scenario_parameters": {
                    "field_size": "Variable (10-1000 acres)",
                    "fertilizer_type": "Granular NPK",
                    "equipment": "Broadcast spreader",
                    "weather_conditions": "Variable"
                },
                "interactive_elements": [
                    {
                        "element_id": "equipment_setup",
                        "type": "equipment_configuration",
                        "description": "Configure spreader settings",
                        "parameters": {
                            "spread_width": {"min": 20, "max": 60, "unit": "feet"},
                            "application_rate": {"min": 50, "max": 300, "unit": "lbs/acre"},
                            "ground_speed": {"min": 3, "max": 12, "unit": "mph"}
                        }
                    },
                    {
                        "element_id": "field_navigation",
                        "type": "navigation_simulator",
                        "description": "Navigate field application pattern",
                        "features": ["GPS guidance", "Overlap management", "Boundary handling"]
                    },
                    {
                        "element_id": "wind_assessment",
                        "type": "environmental_monitor",
                        "description": "Monitor wind conditions",
                        "parameters": {
                            "wind_speed": {"min": 0, "max": 20, "unit": "mph"},
                            "wind_direction": {"options": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]},
                            "gust_factor": {"min": 1.0, "max": 2.0}
                        }
                    },
                    {
                        "element_id": "coverage_assessment",
                        "type": "coverage_analyzer",
                        "description": "Analyze application coverage",
                        "metrics": ["Uniformity", "Overlap", "Missed areas", "Over-application"]
                    }
                ],
                "assessment_criteria": {
                    "coverage_uniformity": {"weight": 0.4, "target": ">90%"},
                    "application_accuracy": {"weight": 0.3, "target": "±5% of target rate"},
                    "time_efficiency": {"weight": 0.2, "target": "<2 hours for 100 acres"},
                    "safety_compliance": {"weight": 0.1, "target": "100%"}
                }
            },
            
            "foliar_timing_simulation": {
                "scenario_id": "foliar_timing_simulation",
                "title": "Foliar Application Timing Simulation",
                "description": "Interactive simulation for optimal foliar application timing",
                "difficulty_level": DifficultyLevel.INTERMEDIATE,
                "estimated_duration_minutes": 25,
                "scenario_parameters": {
                    "crop_type": "Corn",
                    "growth_stage": "V6-V8",
                    "nutrient_deficiency": "Zinc",
                    "weather_forecast": "7-day forecast"
                },
                "interactive_elements": [
                    {
                        "element_id": "timing_optimizer",
                        "type": "timing_calculator",
                        "description": "Calculate optimal application timing",
                        "factors": {
                            "growth_stage": {"options": ["V4", "V6", "V8", "V10", "R1"]},
                            "weather_conditions": {"temperature": {"min": 50, "max": 90, "unit": "°F"},
                                                   "humidity": {"min": 30, "max": 90, "unit": "%"},
                                                   "wind_speed": {"min": 0, "max": 15, "unit": "mph"}},
                            "plant_stress": {"options": ["Low", "Moderate", "High"]}
                        }
                    },
                    {
                        "element_id": "formulation_selector",
                        "type": "product_selector",
                        "description": "Select appropriate foliar formulation",
                        "options": [
                            {"product": "Zinc Sulfate", "concentration": "0.5-1.0%", "compatibility": "Good"},
                            {"product": "Zinc EDTA", "concentration": "0.25-0.5%", "compatibility": "Excellent"},
                            {"product": "Zinc Amino Acid", "concentration": "0.1-0.3%", "compatibility": "Excellent"}
                        ]
                    },
                    {
                        "element_id": "sprayer_configuration",
                        "type": "sprayer_setup",
                        "description": "Configure sprayer for foliar application",
                        "parameters": {
                            "nozzle_type": {"options": ["Flat fan", "Hollow cone", "Full cone"]},
                            "pressure": {"min": 20, "max": 60, "unit": "psi"},
                            "volume": {"min": 10, "max": 30, "unit": "gal/acre"}
                        }
                    }
                ],
                "assessment_criteria": {
                    "timing_accuracy": {"weight": 0.4, "target": "Optimal growth stage"},
                    "formulation_selection": {"weight": 0.3, "target": "Appropriate for deficiency"},
                    "sprayer_setup": {"weight": 0.2, "target": "Optimal coverage"},
                    "safety_compliance": {"weight": 0.1, "target": "100%"}
                }
            }
        }
    
    def _initialize_assessment_questions(self):
        """Initialize assessment questions for tutorials."""
        self.assessment_questions = {
            ApplicationMethodType.BROADCAST: [
                AssessmentQuestion(
                    question_id="broadcast_q1",
                    question="What is the primary advantage of broadcast application?",
                    question_type="multiple_choice",
                    options=["Precision", "Speed", "Efficiency", "Cost"],
                    correct_answer="Speed",
                    explanation="Broadcast application is primarily valued for its speed and ability to cover large areas quickly.",
                    difficulty_level=DifficultyLevel.BEGINNER,
                    learning_objective_id="broadcast_basic_1"
                ),
                AssessmentQuestion(
                    question_id="broadcast_q2",
                    question="What wind speed is considered safe for broadcast application?",
                    question_type="multiple_choice",
                    options=["<5 mph", "<10 mph", "<15 mph", "<20 mph"],
                    correct_answer="<10 mph",
                    explanation="Wind speeds below 10 mph are considered safe for broadcast application to ensure accurate placement.",
                    difficulty_level=DifficultyLevel.INTERMEDIATE,
                    learning_objective_id="broadcast_basic_2"
                ),
                AssessmentQuestion(
                    question_id="broadcast_q3",
                    question="Calculate the application rate if 25 lbs of fertilizer was collected from a 100 ft x 100 ft test area.",
                    question_type="calculation",
                    correct_answer="109 lbs/acre",
                    explanation="Rate = (25 lbs × 43,560 sq ft/acre) / 10,000 sq ft = 108.9 lbs/acre",
                    difficulty_level=DifficultyLevel.INTERMEDIATE,
                    learning_objective_id="broadcast_basic_2"
                )
            ],
            
            ApplicationMethodType.FOLIAR: [
                AssessmentQuestion(
                    question_id="foliar_q1",
                    question="What is the optimal time of day for foliar application?",
                    question_type="multiple_choice",
                    options=["Early morning", "Midday", "Late afternoon", "Evening"],
                    correct_answer="Early morning",
                    explanation="Early morning (6-8 AM) is optimal when stomata are open and humidity is high for maximum uptake.",
                    difficulty_level=DifficultyLevel.INTERMEDIATE,
                    learning_objective_id="foliar_basic_2"
                ),
                AssessmentQuestion(
                    question_id="foliar_q2",
                    question="What concentration of zinc sulfate is typically used for foliar application?",
                    question_type="multiple_choice",
                    options=["0.1-0.3%", "0.5-1.0%", "1.0-2.0%", "2.0-5.0%"],
                    correct_answer="0.5-1.0%",
                    explanation="Zinc sulfate is typically applied at 0.5-1.0% concentration to avoid phytotoxicity while providing adequate nutrition.",
                    difficulty_level=DifficultyLevel.INTERMEDIATE,
                    learning_objective_id="foliar_basic_3"
                )
            ]
        }
    
    async def get_tutorial_by_method(
        self,
        application_method: ApplicationMethodType,
        difficulty_level: DifficultyLevel,
        tutorial_type: str = "basic"
    ) -> Optional[Dict[str, Any]]:
        """Get interactive tutorial for specific application method."""
        try:
            method_tutorials = self.tutorial_database.get(application_method, {})
            tutorial_key = f"{tutorial_type}_tutorial"
            
            if tutorial_key in method_tutorials:
                tutorial = method_tutorials[tutorial_key]
                
                # Filter by difficulty level if specified
                if tutorial["difficulty_level"] == difficulty_level:
                    return tutorial
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting tutorial for {application_method}: {e}")
            return None
    
    async def get_simulation_scenario(
        self,
        scenario_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get simulation scenario by ID."""
        try:
            return self.simulation_scenarios.get(scenario_id)
        except Exception as e:
            logger.error(f"Error getting simulation scenario {scenario_id}: {e}")
            return None
    
    async def get_assessment_questions(
        self,
        application_method: ApplicationMethodType,
        difficulty_level: Optional[DifficultyLevel] = None
    ) -> List[AssessmentQuestion]:
        """Get assessment questions for application method."""
        try:
            questions = self.assessment_questions.get(application_method, [])
            
            if difficulty_level:
                questions = [q for q in questions if q.difficulty_level == difficulty_level]
            
            return questions
            
        except Exception as e:
            logger.error(f"Error getting assessment questions: {e}")
            return []
    
    async def run_interactive_simulation(
        self,
        scenario_id: str,
        user_inputs: Dict[str, Any],
        user_profile: UserProfile
    ) -> Dict[str, Any]:
        """Run interactive simulation with user inputs."""
        try:
            scenario = await self.get_simulation_scenario(scenario_id)
            if not scenario:
                raise ValueError(f"Simulation scenario {scenario_id} not found")
            
            # Process user inputs and run simulation
            simulation_results = await self._process_simulation_inputs(scenario, user_inputs)
            
            # Calculate performance scores
            performance_scores = await self._calculate_performance_scores(
                scenario, simulation_results, user_profile
            )
            
            # Generate feedback and recommendations
            feedback = await self._generate_simulation_feedback(
                scenario, simulation_results, performance_scores
            )
            
            return {
                "scenario_id": scenario_id,
                "simulation_results": simulation_results,
                "performance_scores": performance_scores,
                "feedback": feedback,
                "recommendations": await self._generate_recommendations(
                    performance_scores, user_profile
                ),
                "completion_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error running simulation {scenario_id}: {e}")
            raise
    
    async def _process_simulation_inputs(
        self,
        scenario: Dict[str, Any],
        user_inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process user inputs for simulation."""
        results = {}
        
        for element in scenario["interactive_elements"]:
            element_id = element["element_id"]
            element_type = element["type"]
            
            if element_id in user_inputs:
                input_value = user_inputs[element_id]
                
                # Process based on element type
                if element_type == "equipment_configuration":
                    results[element_id] = await self._process_equipment_configuration(
                        element, input_value
                    )
                elif element_type == "navigation_simulator":
                    results[element_id] = await self._process_navigation_simulation(
                        element, input_value
                    )
                elif element_type == "environmental_monitor":
                    results[element_id] = await self._process_environmental_monitoring(
                        element, input_value
                    )
                elif element_type == "coverage_analyzer":
                    results[element_id] = await self._process_coverage_analysis(
                        element, input_value
                    )
        
        return results
    
    async def _process_equipment_configuration(
        self,
        element: Dict[str, Any],
        user_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process equipment configuration simulation."""
        parameters = element["parameters"]
        results = {}
        
        for param_name, param_config in parameters.items():
            if param_name in user_input:
                value = user_input[param_name]
                min_val = param_config["min"]
                max_val = param_config["max"]
                
                # Validate range
                if min_val <= value <= max_val:
                    results[param_name] = {
                        "value": value,
                        "status": "valid",
                        "score": 1.0
                    }
                else:
                    results[param_name] = {
                        "value": value,
                        "status": "invalid",
                        "score": 0.0,
                        "message": f"Value must be between {min_val} and {max_val}"
                    }
        
        return results
    
    async def _process_navigation_simulation(
        self,
        element: Dict[str, Any],
        user_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process navigation simulation."""
        # Simulate navigation performance
        overlap_percentage = user_input.get("overlap_percentage", 0)
        boundary_handling = user_input.get("boundary_handling", "good")
        gps_usage = user_input.get("gps_usage", True)
        
        # Calculate scores
        overlap_score = max(0, 1 - abs(overlap_percentage - 10) / 10)  # Optimal 10% overlap
        boundary_score = 1.0 if boundary_handling == "good" else 0.5
        gps_score = 1.0 if gps_usage else 0.7
        
        return {
            "overlap_score": overlap_score,
            "boundary_score": boundary_score,
            "gps_score": gps_score,
            "overall_navigation_score": (overlap_score + boundary_score + gps_score) / 3
        }
    
    async def _process_environmental_monitoring(
        self,
        element: Dict[str, Any],
        user_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process environmental monitoring simulation."""
        wind_speed = user_input.get("wind_speed", 0)
        wind_direction = user_input.get("wind_direction", "N")
        
        # Assess wind conditions
        if wind_speed < 5:
            wind_score = 1.0
            wind_assessment = "Excellent"
        elif wind_speed < 10:
            wind_score = 0.8
            wind_assessment = "Good"
        elif wind_speed < 15:
            wind_score = 0.5
            wind_assessment = "Marginal"
        else:
            wind_score = 0.0
            wind_assessment = "Poor - Application not recommended"
        
        return {
            "wind_score": wind_score,
            "wind_assessment": wind_assessment,
            "recommendation": "Proceed" if wind_score >= 0.5 else "Delay application"
        }
    
    async def _process_coverage_analysis(
        self,
        element: Dict[str, Any],
        user_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process coverage analysis simulation."""
        uniformity = user_input.get("uniformity", 85)
        overlap = user_input.get("overlap", 10)
        missed_areas = user_input.get("missed_areas", 2)
        over_application = user_input.get("over_application", 5)
        
        # Calculate scores
        uniformity_score = min(1.0, uniformity / 90)
        overlap_score = max(0, 1 - abs(overlap - 10) / 10)
        missed_score = max(0, 1 - missed_areas / 5)
        over_score = max(0, 1 - over_application / 10)
        
        return {
            "uniformity_score": uniformity_score,
            "overlap_score": overlap_score,
            "missed_score": missed_score,
            "over_score": over_score,
            "overall_coverage_score": (uniformity_score + overlap_score + missed_score + over_score) / 4
        }
    
    async def _calculate_performance_scores(
        self,
        scenario: Dict[str, Any],
        simulation_results: Dict[str, Any],
        user_profile: UserProfile
    ) -> Dict[str, Any]:
        """Calculate performance scores based on simulation results."""
        assessment_criteria = scenario["assessment_criteria"]
        scores = {}
        
        for criterion, config in assessment_criteria.items():
            weight = config["weight"]
            target = config["target"]
            
            # Calculate score based on simulation results
            if criterion == "coverage_uniformity":
                score = simulation_results.get("coverage_assessment", {}).get("overall_coverage_score", 0)
            elif criterion == "application_accuracy":
                score = simulation_results.get("equipment_setup", {}).get("application_rate", {}).get("score", 0)
            elif criterion == "time_efficiency":
                score = simulation_results.get("field_navigation", {}).get("overall_navigation_score", 0)
            elif criterion == "safety_compliance":
                score = simulation_results.get("wind_assessment", {}).get("wind_score", 0)
            else:
                score = 0
            
            scores[criterion] = {
                "score": score,
                "weight": weight,
                "target": target,
                "weighted_score": score * weight
            }
        
        # Calculate overall score
        overall_score = sum(scores[criterion]["weighted_score"] for criterion in scores)
        
        return {
            "individual_scores": scores,
            "overall_score": overall_score,
            "grade": self._calculate_grade(overall_score)
        }
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade based on score."""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"
    
    async def _generate_simulation_feedback(
        self,
        scenario: Dict[str, Any],
        simulation_results: Dict[str, Any],
        performance_scores: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate detailed feedback for simulation results."""
        feedback = {
            "overall_performance": performance_scores["grade"],
            "strengths": [],
            "areas_for_improvement": [],
            "specific_feedback": {}
        }
        
        # Analyze individual scores
        for criterion, score_data in performance_scores["individual_scores"].items():
            score = score_data["score"]
            
            if score >= 0.8:
                feedback["strengths"].append(f"Excellent {criterion.replace('_', ' ')}")
            elif score < 0.6:
                feedback["areas_for_improvement"].append(f"Improve {criterion.replace('_', ' ')}")
            
            # Specific feedback
            if criterion == "coverage_uniformity":
                if score >= 0.9:
                    feedback["specific_feedback"]["coverage"] = "Excellent coverage uniformity achieved"
                elif score >= 0.7:
                    feedback["specific_feedback"]["coverage"] = "Good coverage, minor improvements possible"
                else:
                    feedback["specific_feedback"]["coverage"] = "Coverage uniformity needs improvement - check calibration and overlap"
            
            elif criterion == "application_accuracy":
                if score >= 0.9:
                    feedback["specific_feedback"]["accuracy"] = "Application rate is very accurate"
                elif score >= 0.7:
                    feedback["specific_feedback"]["accuracy"] = "Application rate is acceptable"
                else:
                    feedback["specific_feedback"]["accuracy"] = "Application rate needs calibration - review spreader settings"
        
        return feedback
    
    async def _generate_recommendations(
        self,
        performance_scores: Dict[str, Any],
        user_profile: UserProfile
    ) -> List[Dict[str, Any]]:
        """Generate personalized recommendations based on performance."""
        recommendations = []
        
        # Analyze performance and generate recommendations
        for criterion, score_data in performance_scores["individual_scores"].items():
            score = score_data["score"]
            
            if score < 0.7:
                if criterion == "coverage_uniformity":
                    recommendations.append({
                        "type": "training",
                        "title": "Improve Coverage Uniformity",
                        "description": "Practice calibration techniques and overlap management",
                        "priority": "high",
                        "estimated_time": "30 minutes"
                    })
                elif criterion == "application_accuracy":
                    recommendations.append({
                        "type": "equipment",
                        "title": "Calibrate Application Equipment",
                        "description": "Review and adjust spreader calibration procedures",
                        "priority": "high",
                        "estimated_time": "45 minutes"
                    })
                elif criterion == "time_efficiency":
                    recommendations.append({
                        "type": "technique",
                        "title": "Optimize Field Navigation",
                        "description": "Learn efficient field patterns and GPS guidance usage",
                        "priority": "medium",
                        "estimated_time": "20 minutes"
                    })
        
        # Add general recommendations based on experience level
        if user_profile.experience_level == DifficultyLevel.BEGINNER:
            recommendations.append({
                "type": "foundation",
                "title": "Master Basic Safety Protocols",
                "description": "Complete comprehensive safety training",
                "priority": "high",
                "estimated_time": "60 minutes"
            })
        
        return recommendations