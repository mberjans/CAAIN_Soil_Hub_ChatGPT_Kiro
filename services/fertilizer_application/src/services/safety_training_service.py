"""
Safety Training Service for Fertilizer Application Methods.

This service provides comprehensive safety training modules, protocols, and
certification programs for fertilizer application methods.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4
from datetime import datetime, timedelta
from enum import Enum

from src.models.educational_models import (
    EducationalContent, TrainingModule, LearningPath, ContentType, ContentCategory,
    DifficultyLevel, LearningObjective, AssessmentQuestion, Certification
)
from src.models.application_models import ApplicationMethodType, EquipmentType, FertilizerForm

logger = logging.getLogger(__name__)


class SafetyCategory(str, Enum):
    """Categories of safety training."""
    PERSONAL_PROTECTIVE_EQUIPMENT = "personal_protective_equipment"
    CHEMICAL_HANDLING = "chemical_handling"
    EQUIPMENT_SAFETY = "equipment_safety"
    ENVIRONMENTAL_SAFETY = "environmental_safety"
    EMERGENCY_RESPONSE = "emergency_response"
    REGULATORY_COMPLIANCE = "regulatory_compliance"


class SafetyLevel(str, Enum):
    """Safety training levels."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    SPECIALIST = "specialist"


class SafetyTrainingService:
    """Service for comprehensive safety training and certification."""
    
    def __init__(self):
        self.safety_modules = {}
        self.safety_protocols = {}
        self.ppe_guidelines = {}
        self.emergency_procedures = {}
        self.regulatory_requirements = {}
        self.certification_programs = {}
        self._initialize_safety_modules()
        self._initialize_safety_protocols()
        self._initialize_ppe_guidelines()
        self._initialize_emergency_procedures()
        self._initialize_regulatory_requirements()
        self._initialize_certification_programs()
    
    def _initialize_safety_modules(self):
        """Initialize comprehensive safety training modules."""
        self.safety_modules = {
            SafetyCategory.PERSONAL_PROTECTIVE_EQUIPMENT: [
                TrainingModule(
                    module_id="ppe_basic_001",
                    title="Personal Protective Equipment Fundamentals",
                    description="Comprehensive training on PPE selection, use, and maintenance",
                    category=ContentCategory.SAFETY,
                    difficulty_level=DifficultyLevel.BEGINNER,
                    learning_objectives=[
                        LearningObjective(
                            objective_id="ppe_1",
                            description="Identify required PPE for fertilizer application",
                            category="knowledge"
                        ),
                        LearningObjective(
                            objective_id="ppe_2",
                            description="Properly don and doff PPE",
                            category="skill"
                        ),
                        LearningObjective(
                            objective_id="ppe_3",
                            description="Maintain and inspect PPE",
                            category="skill"
                        )
                    ],
                    content_items=[
                        EducationalContent(
                            content_id="ppe_guide_001",
                            title="PPE Selection Guide",
                            content_type=ContentType.TEXT_GUIDE,
                            category=ContentCategory.SAFETY,
                            difficulty_level=DifficultyLevel.BEGINNER,
                            description="Complete guide to selecting appropriate PPE",
                            duration_minutes=30,
                            content_data={
                                "sections": [
                                    "PPE Requirements by Application Method",
                                    "Chemical-Specific PPE Requirements",
                                    "Environmental Considerations",
                                    "Comfort and Fit Considerations"
                                ],
                                "ppe_types": [
                                    "Safety glasses",
                                    "Face shields",
                                    "Respirators",
                                    "Chemical-resistant gloves",
                                    "Protective clothing",
                                    "Steel-toed boots"
                                ]
                            }
                        ),
                        EducationalContent(
                            content_id="ppe_video_001",
                            title="PPE Donning and Doffing Procedures",
                            content_type=ContentType.VIDEO_TUTORIAL,
                            category=ContentCategory.SAFETY,
                            difficulty_level=DifficultyLevel.BEGINNER,
                            description="Video demonstration of proper PPE procedures",
                            duration_minutes=15,
                            content_url="/videos/ppe_procedures.mp4"
                        )
                    ],
                    estimated_duration_minutes=45,
                    assessment_questions=[
                        {
                            "question": "What type of respirator is required for ammonia application?",
                            "options": ["Dust mask", "Half-face respirator", "Full-face respirator", "No respirator needed"],
                            "correct_answer": "Full-face respirator",
                            "explanation": "Ammonia requires full-face respiratory protection due to its toxicity."
                        }
                    ],
                    completion_criteria={
                        "min_score": 0.8,
                        "practical_demonstration": True,
                        "ppe_inspection": True
                    }
                )
            ],
            
            SafetyCategory.CHEMICAL_HANDLING: [
                TrainingModule(
                    module_id="chemical_handling_001",
                    title="Safe Chemical Handling Practices",
                    description="Training on safe handling, storage, and disposal of fertilizers",
                    category=ContentCategory.SAFETY,
                    difficulty_level=DifficultyLevel.INTERMEDIATE,
                    learning_objectives=[
                        LearningObjective(
                            objective_id="chem_1",
                            description="Understand chemical hazards and safety data sheets",
                            category="knowledge"
                        ),
                        LearningObjective(
                            objective_id="chem_2",
                            description="Implement safe chemical handling procedures",
                            category="skill"
                        ),
                        LearningObjective(
                            objective_id="chem_3",
                            description="Respond to chemical spills and emergencies",
                            category="skill"
                        )
                    ],
                    content_items=[
                        EducationalContent(
                            content_id="chemical_guide_001",
                            title="Chemical Safety Data Sheets",
                            content_type=ContentType.TEXT_GUIDE,
                            category=ContentCategory.SAFETY,
                            difficulty_level=DifficultyLevel.INTERMEDIATE,
                            description="Understanding and using safety data sheets",
                            duration_minutes=40,
                            content_data={
                                "sections": [
                                    "Reading and Understanding SDS",
                                    "Hazard Identification",
                                    "Exposure Controls",
                                    "Emergency Procedures",
                                    "Storage Requirements"
                                ]
                            }
                        ),
                        EducationalContent(
                            content_id="chemical_simulation_001",
                            title="Chemical Spill Response Simulation",
                            content_type=ContentType.INTERACTIVE_SIMULATION,
                            category=ContentCategory.SAFETY,
                            difficulty_level=DifficultyLevel.INTERMEDIATE,
                            description="Interactive simulation for chemical spill response",
                            duration_minutes=25,
                            content_data={
                                "simulation_scenarios": [
                                    "Small spill containment",
                                    "Large spill response",
                                    "Emergency evacuation",
                                    "Decontamination procedures"
                                ]
                            }
                        )
                    ],
                    estimated_duration_minutes=65,
                    completion_criteria={
                        "min_score": 0.85,
                        "spill_response_demonstration": True,
                        "sds_interpretation": True
                    }
                )
            ],
            
            SafetyCategory.EQUIPMENT_SAFETY: [
                TrainingModule(
                    module_id="equipment_safety_001",
                    title="Equipment Safety and Maintenance",
                    description="Training on safe equipment operation and maintenance",
                    category=ContentCategory.SAFETY,
                    difficulty_level=DifficultyLevel.INTERMEDIATE,
                    learning_objectives=[
                        LearningObjective(
                            objective_id="equip_1",
                            description="Identify equipment safety hazards",
                            category="knowledge"
                        ),
                        LearningObjective(
                            objective_id="equip_2",
                            description="Perform pre-operation safety checks",
                            category="skill"
                        ),
                        LearningObjective(
                            objective_id="equip_3",
                            description="Implement lockout/tagout procedures",
                            category="skill"
                        )
                    ],
                    content_items=[
                        EducationalContent(
                            content_id="equipment_guide_001",
                            title="Equipment Safety Checklist",
                            content_type=ContentType.TEXT_GUIDE,
                            category=ContentCategory.SAFETY,
                            difficulty_level=DifficultyLevel.INTERMEDIATE,
                            description="Comprehensive equipment safety checklist",
                            duration_minutes=35,
                            content_data={
                                "checklist_items": [
                                    "Pre-operation inspection",
                                    "Safety device verification",
                                    "Hydraulic system check",
                                    "Electrical system check",
                                    "Mechanical component inspection"
                                ]
                            }
                        )
                    ],
                    estimated_duration_minutes=35,
                    completion_criteria={
                        "min_score": 0.8,
                        "safety_check_demonstration": True,
                        "lockout_procedures": True
                    }
                )
            ],
            
            SafetyCategory.ENVIRONMENTAL_SAFETY: [
                TrainingModule(
                    module_id="environmental_safety_001",
                    title="Environmental Protection and Stewardship",
                    description="Training on environmental protection during fertilizer application",
                    category=ContentCategory.SAFETY,
                    difficulty_level=DifficultyLevel.INTERMEDIATE,
                    learning_objectives=[
                        LearningObjective(
                            objective_id="env_1",
                            description="Understand environmental regulations",
                            category="knowledge"
                        ),
                        LearningObjective(
                            objective_id="env_2",
                            description="Implement environmental protection measures",
                            category="skill"
                        ),
                        LearningObjective(
                            objective_id="env_3",
                            description="Monitor environmental compliance",
                            category="skill"
                        )
                    ],
                    content_items=[
                        EducationalContent(
                            content_id="environmental_guide_001",
                            title="Environmental Regulations Guide",
                            content_type=ContentType.TEXT_GUIDE,
                            category=ContentCategory.SAFETY,
                            difficulty_level=DifficultyLevel.INTERMEDIATE,
                            description="Guide to environmental regulations and compliance",
                            duration_minutes=50,
                            content_data={
                                "regulations": [
                                    "Clean Water Act",
                                    "Resource Conservation and Recovery Act",
                                    "State environmental regulations",
                                    "Local environmental requirements"
                                ]
                            }
                        )
                    ],
                    estimated_duration_minutes=50,
                    completion_criteria={
                        "min_score": 0.8,
                        "compliance_assessment": True,
                        "protection_measures": True
                    }
                )
            ],
            
            SafetyCategory.EMERGENCY_RESPONSE: [
                TrainingModule(
                    module_id="emergency_response_001",
                    title="Emergency Response Procedures",
                    description="Training on emergency response and first aid",
                    category=ContentCategory.SAFETY,
                    difficulty_level=DifficultyLevel.INTERMEDIATE,
                    learning_objectives=[
                        LearningObjective(
                            objective_id="emergency_1",
                            description="Recognize emergency situations",
                            category="knowledge"
                        ),
                        LearningObjective(
                            objective_id="emergency_2",
                            description="Implement emergency response procedures",
                            category="skill"
                        ),
                        LearningObjective(
                            objective_id="emergency_3",
                            description="Provide first aid assistance",
                            category="skill"
                        )
                    ],
                    content_items=[
                        EducationalContent(
                            content_id="emergency_guide_001",
                            title="Emergency Response Procedures",
                            content_type=ContentType.TEXT_GUIDE,
                            category=ContentCategory.SAFETY,
                            difficulty_level=DifficultyLevel.INTERMEDIATE,
                            description="Comprehensive emergency response procedures",
                            duration_minutes=60,
                            content_data={
                                "emergency_types": [
                                    "Chemical exposure",
                                    "Equipment accidents",
                                    "Fire emergencies",
                                    "Medical emergencies",
                                    "Weather emergencies"
                                ]
                            }
                        ),
                        EducationalContent(
                            content_id="first_aid_training_001",
                            title="First Aid Training",
                            content_type=ContentType.VIDEO_TUTORIAL,
                            category=ContentCategory.SAFETY,
                            difficulty_level=DifficultyLevel.INTERMEDIATE,
                            description="First aid training for agricultural workers",
                            duration_minutes=45,
                            content_url="/videos/first_aid_training.mp4"
                        )
                    ],
                    estimated_duration_minutes=105,
                    completion_criteria={
                        "min_score": 0.85,
                        "emergency_drill": True,
                        "first_aid_certification": True
                    }
                )
            ]
        }
    
    def _initialize_safety_protocols(self):
        """Initialize safety protocols and procedures."""
        self.safety_protocols = {
            ApplicationMethodType.BROADCAST: {
                "pre_operation": [
                    "Check weather conditions (wind < 10 mph)",
                    "Inspect spreader for damage or wear",
                    "Verify calibration accuracy",
                    "Check safety devices and guards",
                    "Ensure proper PPE is available",
                    "Review emergency procedures"
                ],
                "during_operation": [
                    "Monitor wind conditions continuously",
                    "Maintain safe operating speeds",
                    "Avoid application near sensitive areas",
                    "Keep emergency equipment accessible",
                    "Monitor equipment performance",
                    "Communicate with ground crew"
                ],
                "post_operation": [
                    "Clean equipment thoroughly",
                    "Store equipment safely",
                    "Dispose of waste properly",
                    "Document application records",
                    "Report any incidents or near-misses",
                    "Schedule next maintenance"
                ]
            },
            
            ApplicationMethodType.FOLIAR: {
                "pre_operation": [
                    "Check weather conditions (no rain forecast)",
                    "Inspect sprayer for leaks or damage",
                    "Verify nozzle selection and pressure",
                    "Check chemical compatibility",
                    "Ensure proper PPE is available",
                    "Review chemical safety data sheets"
                ],
                "during_operation": [
                    "Monitor weather conditions",
                    "Maintain proper application pressure",
                    "Avoid application during temperature inversions",
                    "Monitor for signs of phytotoxicity",
                    "Keep emergency equipment accessible",
                    "Follow drift prevention protocols"
                ],
                "post_operation": [
                    "Triple rinse sprayer tank",
                    "Clean nozzles and filters",
                    "Dispose of rinse water properly",
                    "Store chemicals safely",
                    "Document application records",
                    "Monitor crop response"
                ]
            },
            
            ApplicationMethodType.BAND: {
                "pre_operation": [
                    "Check soil conditions (not saturated)",
                    "Inspect banding equipment",
                    "Verify band placement settings",
                    "Check fertilizer compatibility",
                    "Ensure proper PPE is available",
                    "Review application plan"
                ],
                "during_operation": [
                    "Monitor soil conditions",
                    "Maintain consistent band placement",
                    "Monitor application rate",
                    "Check for equipment malfunctions",
                    "Keep emergency equipment accessible",
                    "Follow environmental guidelines"
                ],
                "post_operation": [
                    "Clean equipment thoroughly",
                    "Check band placement accuracy",
                    "Document application records",
                    "Schedule next maintenance",
                    "Monitor crop response",
                    "Report any issues"
                ]
            },
            
            ApplicationMethodType.INJECTION: {
                "pre_operation": [
                    "Check soil conditions and moisture",
                    "Inspect injection equipment",
                    "Verify injection depth settings",
                    "Check fertilizer compatibility",
                    "Ensure proper PPE is available",
                    "Review safety procedures"
                ],
                "during_operation": [
                    "Monitor injection quality",
                    "Maintain consistent depth",
                    "Monitor application rate",
                    "Check for equipment malfunctions",
                    "Keep emergency equipment accessible",
                    "Follow environmental guidelines"
                ],
                "post_operation": [
                    "Clean injection equipment",
                    "Check injection quality",
                    "Document application records",
                    "Schedule next maintenance",
                    "Monitor crop response",
                    "Report any issues"
                ]
            }
        }
    
    def _initialize_ppe_guidelines(self):
        """Initialize PPE guidelines and requirements."""
        self.ppe_guidelines = {
            "required_ppe": {
                "eyes": {
                    "safety_glasses": "Required for all operations",
                    "face_shield": "Required for high-pressure applications",
                    "goggles": "Required for chemical handling"
                },
                "respiratory": {
                    "dust_mask": "Required for dusty operations",
                    "half_face_respirator": "Required for moderate chemical exposure",
                    "full_face_respirator": "Required for high chemical exposure"
                },
                "hands": {
                    "chemical_resistant_gloves": "Required for chemical handling",
                    "cut_resistant_gloves": "Required for equipment operation",
                    "disposable_gloves": "Required for mixing operations"
                },
                "body": {
                    "long_sleeve_shirt": "Required for all operations",
                    "chemical_resistant_clothing": "Required for chemical handling",
                    "coveralls": "Required for dusty operations"
                },
                "feet": {
                    "steel_toed_boots": "Required for equipment operation",
                    "chemical_resistant_boots": "Required for chemical handling",
                    "slip_resistant_soles": "Required for wet conditions"
                }
            },
            "ppe_selection_guide": {
                "fertilizer_type": {
                    "granular": ["Safety glasses", "Dust mask", "Long sleeves", "Steel-toed boots"],
                    "liquid": ["Safety glasses", "Chemical-resistant gloves", "Long sleeves", "Steel-toed boots"],
                    "ammonia": ["Full-face respirator", "Chemical-resistant clothing", "Chemical-resistant gloves", "Chemical-resistant boots"],
                    "organic": ["Safety glasses", "Dust mask", "Long sleeves", "Steel-toed boots"]
                },
                "application_method": {
                    "broadcast": ["Safety glasses", "Dust mask", "Long sleeves", "Steel-toed boots"],
                    "foliar": ["Safety glasses", "Half-face respirator", "Chemical-resistant gloves", "Long sleeves"],
                    "band": ["Safety glasses", "Dust mask", "Long sleeves", "Steel-toed boots"],
                    "injection": ["Safety glasses", "Chemical-resistant gloves", "Long sleeves", "Steel-toed boots"]
                }
            },
            "ppe_maintenance": {
                "inspection": [
                    "Check for damage or wear",
                    "Verify proper fit",
                    "Check expiration dates",
                    "Test functionality"
                ],
                "cleaning": [
                    "Follow manufacturer instructions",
                    "Use appropriate cleaning agents",
                    "Allow proper drying time",
                    "Store in clean, dry location"
                ],
                "replacement": [
                    "Replace damaged PPE immediately",
                    "Follow manufacturer replacement schedule",
                    "Document replacement dates",
                    "Train on new PPE features"
                ]
            }
        }
    
    def _initialize_emergency_procedures(self):
        """Initialize emergency response procedures."""
        self.emergency_procedures = {
            "chemical_exposure": {
                "skin_contact": [
                    "Remove contaminated clothing immediately",
                    "Rinse affected area with water for 15 minutes",
                    "Seek medical attention if irritation persists",
                    "Document incident and treatment"
                ],
                "eye_contact": [
                    "Rinse eyes with water for 15 minutes",
                    "Hold eyelids open during rinsing",
                    "Seek immediate medical attention",
                    "Document incident and treatment"
                ],
                "inhalation": [
                    "Move to fresh air immediately",
                    "Remove contaminated clothing",
                    "Seek medical attention if symptoms develop",
                    "Document incident and treatment"
                ],
                "ingestion": [
                    "Do not induce vomiting",
                    "Rinse mouth with water",
                    "Seek immediate medical attention",
                    "Bring chemical label to medical facility"
                ]
            },
            "equipment_accidents": {
                "entanglement": [
                    "Stop equipment immediately",
                    "Do not attempt to free victim",
                    "Call emergency services",
                    "Provide first aid if safe to do so"
                ],
                "crush_injuries": [
                    "Stop equipment immediately",
                    "Do not move victim unless necessary",
                    "Call emergency services",
                    "Provide first aid if trained"
                ],
                "electrical_shock": [
                    "Turn off power source",
                    "Do not touch victim until power is off",
                    "Call emergency services",
                    "Provide CPR if trained"
                ]
            },
            "fire_emergencies": {
                "small_fire": [
                    "Use appropriate fire extinguisher",
                    "Evacuate area if fire spreads",
                    "Call fire department",
                    "Document incident"
                ],
                "large_fire": [
                    "Evacuate area immediately",
                    "Call fire department",
                    "Do not attempt to fight fire",
                    "Account for all personnel"
                ]
            },
            "weather_emergencies": {
                "severe_weather": [
                    "Seek shelter immediately",
                    "Avoid open areas",
                    "Stay away from equipment",
                    "Monitor weather updates"
                ],
                "lightning": [
                    "Seek shelter in building or vehicle",
                    "Avoid open areas and equipment",
                    "Stay away from water",
                    "Wait 30 minutes after last lightning"
                ]
            }
        }
    
    def _initialize_regulatory_requirements(self):
        """Initialize regulatory requirements and compliance."""
        self.regulatory_requirements = {
            "osha_requirements": {
                "hazard_communication": [
                    "Safety data sheets available",
                    "Chemical labels properly maintained",
                    "Employee training completed",
                    "Written program in place"
                ],
                "personal_protective_equipment": [
                    "PPE hazard assessment completed",
                    "Appropriate PPE provided",
                    "Employee training completed",
                    "PPE properly maintained"
                ],
                "lockout_tagout": [
                    "Written program in place",
                    "Employee training completed",
                    "Procedures documented",
                    "Equipment properly identified"
                ]
            },
            "epa_requirements": {
                "spill_prevention": [
                    "Spill prevention plan in place",
                    "Secondary containment provided",
                    "Employee training completed",
                    "Emergency response procedures"
                ],
                "waste_disposal": [
                    "Proper waste identification",
                    "Appropriate disposal methods",
                    "Documentation maintained",
                    "Compliance with regulations"
                ]
            },
            "state_requirements": {
                "worker_protection_standard": [
                    "Employee training completed",
                    "PPE requirements met",
                    "Application restrictions followed",
                    "Record keeping maintained"
                ],
                "pesticide_applicator_certification": [
                    "Certification current",
                    "Continuing education completed",
                    "Records maintained",
                    "Compliance with regulations"
                ]
            }
        }
    
    def _initialize_certification_programs(self):
        """Initialize safety certification programs."""
        self.certification_programs = {
            "basic_safety_certification": {
                "certification_id": "basic_safety_001",
                "name": "Basic Fertilizer Application Safety",
                "description": "Basic safety certification for fertilizer application",
                "requirements": [
                    "Complete basic safety training modules",
                    "Pass written examination (80% score)",
                    "Demonstrate proper PPE usage",
                    "Complete practical safety assessment"
                ],
                "validity_period_months": 24,
                "renewal_requirements": [
                    "Annual refresher training",
                    "Updated regulations training",
                    "Practical assessment"
                ],
                "modules_required": [
                    "ppe_basic_001",
                    "chemical_handling_001",
                    "equipment_safety_001"
                ]
            },
            "advanced_safety_certification": {
                "certification_id": "advanced_safety_001",
                "name": "Advanced Fertilizer Application Safety",
                "description": "Advanced safety certification for complex operations",
                "requirements": [
                    "Complete advanced safety training modules",
                    "Pass written examination (85% score)",
                    "Demonstrate emergency response procedures",
                    "Complete comprehensive practical assessment"
                ],
                "validity_period_months": 36,
                "renewal_requirements": [
                    "Biennial refresher training",
                    "Updated regulations training",
                    "Emergency response drill",
                    "Practical assessment"
                ],
                "modules_required": [
                    "ppe_basic_001",
                    "chemical_handling_001",
                    "equipment_safety_001",
                    "environmental_safety_001",
                    "emergency_response_001"
                ]
            },
            "specialist_safety_certification": {
                "certification_id": "specialist_safety_001",
                "name": "Fertilizer Application Safety Specialist",
                "description": "Specialist certification for safety leadership",
                "requirements": [
                    "Complete all safety training modules",
                    "Pass comprehensive examination (90% score)",
                    "Demonstrate leadership in safety",
                    "Complete instructor training",
                    "Mentor other employees"
                ],
                "validity_period_months": 48,
                "renewal_requirements": [
                    "Annual continuing education",
                    "Updated regulations training",
                    "Leadership development",
                    "Mentoring activities"
                ],
                "modules_required": [
                    "All safety training modules",
                    "Leadership training",
                    "Instructor training"
                ]
            }
        }
    
    async def get_safety_training_modules(
        self,
        category: Optional[SafetyCategory] = None,
        difficulty_level: Optional[DifficultyLevel] = None
    ) -> List[TrainingModule]:
        """Get safety training modules filtered by criteria."""
        try:
            modules = []
            
            if category:
                category_modules = self.safety_modules.get(category, [])
                modules.extend(category_modules)
            else:
                # Return all modules
                for category_modules in self.safety_modules.values():
                    modules.extend(category_modules)
            
            # Filter by difficulty level
            if difficulty_level:
                modules = [module for module in modules if module.difficulty_level == difficulty_level]
            
            return modules
            
        except Exception as e:
            logger.error(f"Error getting safety training modules: {e}")
            return []
    
    async def get_safety_protocols(
        self,
        application_method: ApplicationMethodType,
        operation_phase: str
    ) -> List[str]:
        """Get safety protocols for specific application method and phase."""
        try:
            method_protocols = self.safety_protocols.get(application_method, {})
            return method_protocols.get(operation_phase, [])
        except Exception as e:
            logger.error(f"Error getting safety protocols: {e}")
            return []
    
    async def get_ppe_requirements(
        self,
        application_method: ApplicationMethodType,
        fertilizer_type: str
    ) -> List[str]:
        """Get PPE requirements for specific application method and fertilizer type."""
        try:
            requirements = []
            
            # Get requirements by application method
            method_requirements = self.ppe_guidelines["ppe_selection_guide"]["application_method"].get(
                application_method.value, []
            )
            requirements.extend(method_requirements)
            
            # Get requirements by fertilizer type
            fertilizer_requirements = self.ppe_guidelines["ppe_selection_guide"]["fertilizer_type"].get(
                fertilizer_type.lower(), []
            )
            requirements.extend(fertilizer_requirements)
            
            # Remove duplicates
            return list(set(requirements))
            
        except Exception as e:
            logger.error(f"Error getting PPE requirements: {e}")
            return []
    
    async def get_emergency_procedures(
        self,
        emergency_type: str
    ) -> List[str]:
        """Get emergency procedures for specific emergency type."""
        try:
            return self.emergency_procedures.get(emergency_type, [])
        except Exception as e:
            logger.error(f"Error getting emergency procedures: {e}")
            return []
    
    async def get_regulatory_requirements(
        self,
        agency: str
    ) -> Dict[str, List[str]]:
        """Get regulatory requirements for specific agency."""
        try:
            return self.regulatory_requirements.get(agency, {})
        except Exception as e:
            logger.error(f"Error getting regulatory requirements: {e}")
            return {}
    
    async def get_certification_programs(
        self,
        certification_level: Optional[SafetyLevel] = None
    ) -> List[Dict[str, Any]]:
        """Get certification programs filtered by level."""
        try:
            programs = list(self.certification_programs.values())
            
            if certification_level:
                if certification_level == SafetyLevel.BASIC:
                    programs = [p for p in programs if "basic" in p["certification_id"]]
                elif certification_level == SafetyLevel.ADVANCED:
                    programs = [p for p in programs if "advanced" in p["certification_id"]]
                elif certification_level == SafetyLevel.SPECIALIST:
                    programs = [p for p in programs if "specialist" in p["certification_id"]]
            
            return programs
            
        except Exception as e:
            logger.error(f"Error getting certification programs: {e}")
            return []
    
    async def generate_safety_assessment(
        self,
        user_profile: Dict[str, Any],
        farm_characteristics: Dict[str, Any],
        application_method: ApplicationMethodType
    ) -> Dict[str, Any]:
        """Generate personalized safety assessment."""
        try:
            assessment = {
                "assessment_id": str(uuid4()),
                "user_profile": user_profile,
                "farm_characteristics": farm_characteristics,
                "application_method": application_method,
                "safety_score": 0.0,
                "risk_factors": [],
                "recommendations": [],
                "required_training": [],
                "ppe_requirements": [],
                "compliance_status": {}
            }
            
            # Calculate safety score based on various factors
            safety_score = 0.0
            
            # Experience level factor
            experience_level = user_profile.get("experience_level", DifficultyLevel.BEGINNER)
            if experience_level == DifficultyLevel.BEGINNER:
                safety_score += 0.3
                assessment["risk_factors"].append("Limited experience requires additional training")
            elif experience_level == DifficultyLevel.INTERMEDIATE:
                safety_score += 0.6
            else:
                safety_score += 0.8
            
            # Farm size factor
            farm_size = farm_characteristics.get("farm_size_acres", 0)
            if farm_size > 1000:
                safety_score += 0.1
                assessment["risk_factors"].append("Large operation requires comprehensive safety program")
            elif farm_size < 100:
                safety_score += 0.2
            
            # Equipment factor
            equipment_available = user_profile.get("equipment_available", [])
            if EquipmentType.SPREADER in equipment_available:
                safety_score += 0.1
            if EquipmentType.SPRAYER in equipment_available:
                safety_score += 0.1
                assessment["risk_factors"].append("Sprayer operations require specialized safety training")
            
            # Application method factor
            if application_method == ApplicationMethodType.FOLIAR:
                safety_score -= 0.1
                assessment["risk_factors"].append("Foliar application has higher chemical exposure risk")
            elif application_method == ApplicationMethodType.INJECTION:
                safety_score -= 0.05
                assessment["risk_factors"].append("Injection application requires specialized equipment training")
            
            assessment["safety_score"] = max(0.0, min(1.0, safety_score))
            
            # Generate recommendations based on assessment
            if assessment["safety_score"] < 0.5:
                assessment["recommendations"].append("Complete comprehensive safety training program")
                assessment["required_training"].extend([
                    "ppe_basic_001",
                    "chemical_handling_001",
                    "equipment_safety_001",
                    "emergency_response_001"
                ])
            elif assessment["safety_score"] < 0.7:
                assessment["recommendations"].append("Complete intermediate safety training")
                assessment["required_training"].extend([
                    "chemical_handling_001",
                    "equipment_safety_001"
                ])
            else:
                assessment["recommendations"].append("Maintain current safety practices")
                assessment["required_training"].append("annual_refresher")
            
            # Get PPE requirements
            assessment["ppe_requirements"] = await self.get_ppe_requirements(
                application_method, "granular"  # Default fertilizer type
            )
            
            # Check compliance status
            assessment["compliance_status"] = {
                "osha_compliance": "Needs assessment",
                "epa_compliance": "Needs assessment",
                "state_compliance": "Needs assessment"
            }
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error generating safety assessment: {e}")
            raise
    
    async def validate_safety_certification(
        self,
        certification_id: str,
        user_completion_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate safety certification completion."""
        try:
            certification = self.certification_programs.get(certification_id)
            if not certification:
                raise ValueError(f"Certification {certification_id} not found")
            
            validation_results = {
                "certification_id": certification_id,
                "validation_status": "pending",
                "completed_requirements": [],
                "missing_requirements": [],
                "certification_score": 0.0,
                "recommendations": []
            }
            
            # Check each requirement
            requirements = certification["requirements"]
            completed_count = 0
            
            for requirement in requirements:
                if requirement in user_completion_data.get("completed_items", []):
                    validation_results["completed_requirements"].append(requirement)
                    completed_count += 1
                else:
                    validation_results["missing_requirements"].append(requirement)
            
            # Calculate certification score
            validation_results["certification_score"] = completed_count / len(requirements)
            
            # Determine validation status
            if validation_results["certification_score"] >= 1.0:
                validation_results["validation_status"] = "certified"
                validation_results["recommendations"].append("Certification requirements met")
            elif validation_results["certification_score"] >= 0.8:
                validation_results["validation_status"] = "nearly_complete"
                validation_results["recommendations"].append("Complete remaining requirements")
            else:
                validation_results["validation_status"] = "incomplete"
                validation_results["recommendations"].append("Significant progress needed")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating safety certification: {e}")
            raise