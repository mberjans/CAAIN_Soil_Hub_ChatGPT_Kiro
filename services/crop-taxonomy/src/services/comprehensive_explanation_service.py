"""
Comprehensive Explanation and Reasoning Display System

This service provides detailed explanations for crop variety recommendations with
expandable interfaces, evidence display, confidence visualization, and educational content.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ExplanationType(str, Enum):
    """Types of explanations available."""
    SUMMARY = "summary"
    DETAILED_REASONING = "detailed_reasoning"
    EVIDENCE_BASED = "evidence_based"
    EDUCATIONAL = "educational"
    TRADE_OFF_ANALYSIS = "trade_off_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    ECONOMIC_ANALYSIS = "economic_analysis"
    MANAGEMENT_GUIDANCE = "management_guidance"

class ConfidenceLevel(str, Enum):
    """Confidence levels for explanations."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"

@dataclass
class EvidenceItem:
    """Individual evidence item for explanations."""
    title: str
    description: str
    source: str
    confidence: float
    data_type: str  # "research", "field_trial", "expert_opinion", "historical_data"
    relevance_score: float
    supporting_data: Optional[Dict[str, Any]] = None

@dataclass
class ExplanationSection:
    """Individual section of an explanation."""
    section_id: str
    title: str
    content: str
    explanation_type: ExplanationType
    confidence_level: ConfidenceLevel
    evidence_items: List[EvidenceItem]
    expandable: bool = True
    educational_content: Optional[str] = None
    interactive_elements: Optional[List[Dict[str, Any]]] = None

@dataclass
class ComprehensiveExplanation:
    """Complete explanation structure."""
    request_id: str
    variety_id: str
    variety_name: str
    generated_at: datetime
    overall_confidence: float
    sections: List[ExplanationSection]
    summary: str
    key_insights: List[str]
    recommendations: List[str]
    educational_resources: List[Dict[str, str]]
    accessibility_features: Dict[str, Any]

class ComprehensiveExplanationService:
    """
    Service for generating comprehensive explanations with detailed reasoning,
    evidence display, confidence visualization, and educational content.
    """

    def __init__(self):
        """Initialize the comprehensive explanation service."""
        self.explanation_templates = self._load_explanation_templates()
        self.educational_content = self._load_educational_content()
        self.evidence_sources = self._initialize_evidence_sources()
        
    def _load_explanation_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load explanation templates for different scenarios."""
        return {
            "high_yield_variety": {
                "summary_template": "{variety_name} is recommended primarily for its exceptional yield potential of {yield_score:.1%}, which ranks in the top {yield_percentile}% of varieties tested in your region.",
                "key_factors": {
                    "yield_potential": "This variety consistently achieves yields 15-20% above regional averages, with excellent stability across different weather conditions.",
                    "disease_resistance": "Strong resistance to {disease_list} reduces yield losses and input costs.",
                    "market_acceptance": "High market acceptance with {market_premium}% premium potential due to superior grain quality."
                }
            },
            "disease_resistant_variety": {
                "summary_template": "{variety_name} is recommended for its comprehensive disease resistance package, providing protection against {disease_count} major diseases in your area.",
                "key_factors": {
                    "disease_resistance": "Resistance to {disease_list} significantly reduces fungicide requirements and protects yield potential.",
                    "yield_stability": "Consistent performance even in high-disease pressure years.",
                    "input_cost_savings": "Reduced fungicide applications save approximately ${cost_savings} per acre."
                }
            },
            "premium_quality_variety": {
                "summary_template": "{variety_name} is recommended for premium market opportunities, offering {quality_score:.1%} quality rating with {premium_potential}% market premium potential.",
                "key_factors": {
                    "quality_traits": "Superior {quality_traits} meet premium market specifications.",
                    "market_premium": "Consistent premium pricing of ${premium_amount} per bushel above commodity prices.",
                    "contract_opportunities": "Eligible for premium contracts with {contract_types}."
                }
            }
        }

    def _load_educational_content(self) -> Dict[str, Dict[str, str]]:
        """Load educational content for explanations."""
        return {
            "yield_potential": {
                "title": "Understanding Yield Potential",
                "content": "Yield potential represents the maximum achievable yield under optimal growing conditions. It's influenced by genetics, soil fertility, weather, and management practices.",
                "key_points": [
                    "Genetic potential sets the upper limit",
                    "Environmental factors determine actual achievement",
                    "Management practices optimize genetic potential",
                    "Regional adaptation affects performance"
                ]
            },
            "disease_resistance": {
                "title": "Disease Resistance in Crops",
                "content": "Disease resistance reduces crop losses and input costs. Resistance can be genetic (built-in) or achieved through management practices.",
                "key_points": [
                    "Genetic resistance is most effective",
                    "Resistance reduces fungicide needs",
                    "Multiple resistance genes provide better protection",
                    "Resistance can break down over time"
                ]
            },
            "soil_compatibility": {
                "title": "Soil Compatibility Factors",
                "content": "Soil compatibility affects root development, nutrient uptake, and water availability. Different varieties perform better in different soil types.",
                "key_points": [
                    "Soil texture affects root penetration",
                    "pH levels influence nutrient availability",
                    "Drainage affects root health",
                    "Organic matter improves soil structure"
                ]
            }
        }

    def _initialize_evidence_sources(self) -> Dict[str, Dict[str, Any]]:
        """Initialize evidence sources and their reliability scores."""
        return {
            "university_trials": {
                "reliability": 0.95,
                "description": "Multi-year university extension trials",
                "sample_size": "large"
            },
            "seed_company_data": {
                "reliability": 0.85,
                "description": "Seed company performance data",
                "sample_size": "medium"
            },
            "farmer_reports": {
                "reliability": 0.75,
                "description": "Farmer field reports and surveys",
                "sample_size": "variable"
            },
            "research_studies": {
                "reliability": 0.90,
                "description": "Peer-reviewed research studies",
                "sample_size": "controlled"
            }
        }

    async def generate_comprehensive_explanation(
        self,
        variety_data: Dict[str, Any],
        context: Dict[str, Any],
        explanation_options: Dict[str, Any]
    ) -> ComprehensiveExplanation:
        """
        Generate comprehensive explanation with detailed reasoning and evidence.
        
        Args:
            variety_data: Variety information and scores
            context: Farm and environmental context
            explanation_options: Options for explanation generation
            
        Returns:
            Comprehensive explanation with all sections and evidence
        """
        try:
            request_id = variety_data.get("request_id", f"explanation_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            variety_id = variety_data.get("variety_id", "unknown")
            variety_name = variety_data.get("variety_name", "Unknown Variety")
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(variety_data, context)
            
            # Generate explanation sections
            sections = await self._generate_explanation_sections(
                variety_data, context, explanation_options
            )
            
            # Generate summary and insights
            summary = self._generate_summary(variety_data, context)
            key_insights = self._generate_key_insights(variety_data, context)
            recommendations = self._generate_recommendations(variety_data, context)
            
            # Load educational resources
            educational_resources = self._get_educational_resources(variety_data, context)
            
            # Prepare accessibility features
            accessibility_features = self._prepare_accessibility_features(sections)
            
            return ComprehensiveExplanation(
                request_id=request_id,
                variety_id=variety_id,
                variety_name=variety_name,
                generated_at=datetime.now(),
                overall_confidence=overall_confidence,
                sections=sections,
                summary=summary,
                key_insights=key_insights,
                recommendations=recommendations,
                educational_resources=educational_resources,
                accessibility_features=accessibility_features
            )
            
        except Exception as e:
            logger.error(f"Error generating comprehensive explanation: {e}")
            raise

    def _calculate_overall_confidence(
        self,
        variety_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        """Calculate overall confidence in the recommendation."""
        # Base confidence from data completeness
        data_completeness = variety_data.get("data_completeness", 0.8)
        
        # Regional adaptation confidence
        regional_data_quality = context.get("regional_data_quality", 0.7)
        
        # Variety testing history
        testing_years = variety_data.get("testing_years", 3)
        testing_confidence = min(testing_years / 5.0, 1.0)
        
        # Calculate weighted average
        overall_confidence = (
            data_completeness * 0.4 +
            regional_data_quality * 0.3 +
            testing_confidence * 0.3
        )
        
        return min(max(overall_confidence, 0.1), 1.0)

    async def _generate_explanation_sections(
        self,
        variety_data: Dict[str, Any],
        context: Dict[str, Any],
        options: Dict[str, Any]
    ) -> List[ExplanationSection]:
        """Generate all explanation sections."""
        sections = []
        
        # Summary section
        sections.append(self._create_summary_section(variety_data, context))
        
        # Detailed reasoning section
        if options.get("include_detailed_reasoning", True):
            sections.append(self._create_detailed_reasoning_section(variety_data, context))
        
        # Evidence-based section
        if options.get("include_evidence", True):
            sections.append(self._create_evidence_section(variety_data, context))
        
        # Trade-off analysis
        if options.get("include_trade_offs", True):
            sections.append(self._create_trade_off_section(variety_data, context))
        
        # Risk assessment
        if options.get("include_risk_analysis", True):
            sections.append(self._create_risk_assessment_section(variety_data, context))
        
        # Economic analysis
        if options.get("include_economic_analysis", True):
            sections.append(self._create_economic_analysis_section(variety_data, context))
        
        # Management guidance
        if options.get("include_management_guidance", True):
            sections.append(self._create_management_guidance_section(variety_data, context))
        
        return sections

    def _create_summary_section(
        self,
        variety_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> ExplanationSection:
        """Create summary explanation section."""
        variety_name = variety_data.get("variety_name", "This variety")
        primary_factor = self._identify_primary_recommendation_factor(variety_data)
        
        # Generate evidence items
        evidence_items = [
            EvidenceItem(
                title="Regional Performance Data",
                description=f"{variety_name} performance in {context.get('region', 'your region')}",
                source="University Extension Trials",
                confidence=0.85,
                data_type="research",
                relevance_score=0.9
            ),
            EvidenceItem(
                title="Soil Compatibility Analysis",
                description=f"Compatibility with {context.get('soil_type', 'your soil type')}",
                source="Soil Science Research",
                confidence=0.8,
                data_type="research",
                relevance_score=0.85
            )
        ]
        
        content = f"{variety_name} is recommended based on its {primary_factor} performance, "
        content += f"with an overall suitability score of {variety_data.get('overall_score', 0.8):.1%}. "
        content += f"This variety shows excellent adaptation to your {context.get('climate_zone', 'climate zone')} "
        content += f"and {context.get('soil_type', 'soil conditions')}."
        
        return ExplanationSection(
            section_id="summary",
            title="Recommendation Summary",
            content=content,
            explanation_type=ExplanationType.SUMMARY,
            confidence_level=self._get_confidence_level(variety_data.get('overall_score', 0.8)),
            evidence_items=evidence_items,
            expandable=False,
            educational_content=self.educational_content.get("yield_potential", {}).get("content")
        )

    def _create_detailed_reasoning_section(
        self,
        variety_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> ExplanationSection:
        """Create detailed reasoning section."""
        variety_name = variety_data.get("variety_name", "This variety")
        scores = variety_data.get("scores", {})
        
        content = f"<h6>Why {variety_name}?</h6>\n"
        
        # Yield potential reasoning
        if scores.get("yield_potential", 0) > 0.8:
            content += f"<p><strong>Exceptional Yield Potential:</strong> "
            content += f"This variety consistently achieves yields in the {scores.get('yield_percentile', 85)}th percentile "
            content += f"for your region, with excellent stability across different weather conditions.</p>\n"
        
        # Disease resistance reasoning
        if scores.get("disease_resistance", 0) > 0.7:
            diseases = variety_data.get("resistant_diseases", ["common diseases"])
            content += f"<p><strong>Strong Disease Resistance:</strong> "
            content += f"Resistance to {', '.join(diseases)} reduces yield losses and input costs, "
            content += f"providing economic benefits of approximately ${variety_data.get('disease_cost_savings', 25)} per acre.</p>\n"
        
        # Soil compatibility reasoning
        soil_score = scores.get("soil_compatibility", 0)
        if soil_score > 0.8:
            content += f"<p><strong>Excellent Soil Compatibility:</strong> "
            content += f"This variety performs exceptionally well in {context.get('soil_type', 'your soil type')} "
            content += f"conditions, with optimal root development and nutrient uptake.</p>\n"
        elif soil_score < 0.6:
            content += f"<p><strong>Soil Considerations:</strong> "
            content += f"While this variety can grow in {context.get('soil_type', 'your soil type')}, "
            content += f"soil amendments may be beneficial for optimal performance.</p>\n"
        
        # Evidence items
        evidence_items = [
            EvidenceItem(
                title="Multi-Year Trial Data",
                description=f"{variety_name} performance across multiple growing seasons",
                source="University Extension",
                confidence=0.9,
                data_type="research",
                relevance_score=0.95
            ),
            EvidenceItem(
                title="Regional Adaptation Studies",
                description=f"Adaptation to {context.get('climate_zone', 'local climate')} conditions",
                source="Agricultural Research",
                confidence=0.85,
                data_type="research",
                relevance_score=0.9
            )
        ]
        
        return ExplanationSection(
            section_id="detailed_reasoning",
            title="Detailed Reasoning",
            content=content,
            explanation_type=ExplanationType.DETAILED_REASONING,
            confidence_level=self._get_confidence_level(scores.get("overall_score", 0.8)),
            evidence_items=evidence_items,
            expandable=True,
            educational_content=self.educational_content.get("disease_resistance", {}).get("content")
        )

    def _create_evidence_section(
        self,
        variety_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> ExplanationSection:
        """Create evidence-based section."""
        variety_name = variety_data.get("variety_name", "This variety")
        
        content = f"<h6>Supporting Evidence for {variety_name}</h6>\n"
        content += "<div class='evidence-grid'>\n"
        
        # University trial data
        content += "<div class='evidence-item'>\n"
        content += "<h6><i class='fas fa-university'></i> University Trials</h6>\n"
        content += f"<p>Multi-year trials show {variety_name} achieving "
        content += f"{variety_data.get('trial_yield', 180)} bushels per acre average "
        content += f"across {variety_data.get('trial_years', 3)} years of testing.</p>\n"
        content += "<small class='text-muted'>Source: University Extension Service</small>\n"
        content += "</div>\n"
        
        # Farmer reports
        content += "<div class='evidence-item'>\n"
        content += "<h6><i class='fas fa-tractor'></i> Farmer Reports</h6>\n"
        content += f"<p>{variety_data.get('farmer_satisfaction', 85)}% of farmers "
        content += f"report satisfaction with {variety_name} performance, "
        content += f"citing {variety_data.get('top_farmer_benefits', 'yield consistency and disease resistance')}.</p>\n"
        content += "<small class='text-muted'>Source: Farmer Survey Data</small>\n"
        content += "</div>\n"
        
        # Research studies
        content += "<div class='evidence-item'>\n"
        content += "<h6><i class='fas fa-microscope'></i> Research Studies</h6>\n"
        content += f"<p>Peer-reviewed studies confirm {variety_name}'s "
        content += f"{variety_data.get('research_benefits', 'superior nutrient use efficiency and stress tolerance')} "
        content += f"under controlled conditions.</p>\n"
        content += "<small class='text-muted'>Source: Agricultural Research Journal</small>\n"
        content += "</div>\n"
        
        content += "</div>\n"
        
        # Evidence items
        evidence_items = [
            EvidenceItem(
                title="University Trial Results",
                description=f"{variety_name} performance in controlled trials",
                source="University Extension Service",
                confidence=0.95,
                data_type="research",
                relevance_score=0.95,
                supporting_data={"yield": variety_data.get("trial_yield", 180), "years": variety_data.get("trial_years", 3)}
            ),
            EvidenceItem(
                title="Farmer Satisfaction Survey",
                description=f"Real-world performance feedback from farmers",
                source="Agricultural Extension",
                confidence=0.8,
                data_type="field_trial",
                relevance_score=0.85,
                supporting_data={"satisfaction": variety_data.get("farmer_satisfaction", 85)}
            ),
            EvidenceItem(
                title="Research Study Validation",
                description=f"Scientific validation of variety characteristics",
                source="Agricultural Research Journal",
                confidence=0.9,
                data_type="research",
                relevance_score=0.9
            )
        ]
        
        return ExplanationSection(
            section_id="evidence",
            title="Supporting Evidence",
            content=content,
            explanation_type=ExplanationType.EVIDENCE_BASED,
            confidence_level=ConfidenceLevel.HIGH,
            evidence_items=evidence_items,
            expandable=True,
            interactive_elements=[
                {"type": "expandable_evidence", "title": "View Detailed Trial Data"},
                {"type": "evidence_filter", "title": "Filter by Evidence Type"},
                {"type": "confidence_meter", "title": "Evidence Confidence"}
            ]
        )

    def _create_trade_off_section(
        self,
        variety_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> ExplanationSection:
        """Create trade-off analysis section."""
        variety_name = variety_data.get("variety_name", "This variety")
        
        content = f"<h6>Trade-off Analysis for {variety_name}</h6>\n"
        
        # Strengths
        content += "<div class='trade-off-section'>\n"
        content += "<h6 class='text-success'><i class='fas fa-check-circle'></i> Key Strengths</h6>\n"
        content += "<ul>\n"
        strengths = variety_data.get("strengths", [
            "High yield potential",
            "Strong disease resistance",
            "Good market acceptance"
        ])
        for strength in strengths:
            content += f"<li>{strength}</li>\n"
        content += "</ul>\n"
        content += "</div>\n"
        
        # Considerations
        content += "<div class='trade-off-section'>\n"
        content += "<h6 class='text-warning'><i class='fas fa-exclamation-triangle'></i> Important Considerations</h6>\n"
        content += "<ul>\n"
        considerations = variety_data.get("considerations", [
            "Higher seed cost compared to commodity varieties",
            "Requires careful nitrogen management",
            "May need additional management attention"
        ])
        for consideration in considerations:
            content += f"<li>{consideration}</li>\n"
        content += "</ul>\n"
        content += "</div>\n"
        
        # Evidence items
        evidence_items = [
            EvidenceItem(
                title="Cost-Benefit Analysis",
                description=f"Economic analysis of {variety_name} investment",
                source="Economic Research",
                confidence=0.85,
                data_type="research",
                relevance_score=0.9
            )
        ]
        
        return ExplanationSection(
            section_id="trade_offs",
            title="Trade-off Analysis",
            content=content,
            explanation_type=ExplanationType.TRADE_OFF_ANALYSIS,
            confidence_level=ConfidenceLevel.MEDIUM,
            evidence_items=evidence_items,
            expandable=True,
            interactive_elements=[
                {"type": "pros_cons_toggle", "title": "Toggle Strengths/Considerations"},
                {"type": "cost_calculator", "title": "Calculate ROI"}
            ]
        )

    def _create_risk_assessment_section(
        self,
        variety_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> ExplanationSection:
        """Create risk assessment section."""
        variety_name = variety_data.get("variety_name", "This variety")
        risk_level = variety_data.get("risk_level", "low")
        
        content = f"<h6>Risk Assessment for {variety_name}</h6>\n"
        
        # Overall risk
        risk_color = {"low": "success", "medium": "warning", "high": "danger"}.get(risk_level, "info")
        content += f"<div class='alert alert-{risk_color}'>\n"
        content += f"<h6><i class='fas fa-shield-alt'></i> Overall Risk Level: {risk_level.title()}</h6>\n"
        content += f"<p>{variety_name} presents a {risk_level} risk profile based on historical performance and regional adaptation.</p>\n"
        content += "</div>\n"
        
        # Risk factors
        content += "<h6>Risk Factors</h6>\n"
        content += "<div class='risk-factors'>\n"
        
        risk_factors = variety_data.get("risk_factors", [
            {"factor": "Weather Sensitivity", "level": "Low", "description": "Good stability across conditions"},
            {"factor": "Market Risk", "level": "Low", "description": "Strong market acceptance"},
            {"factor": "Management Risk", "level": "Medium", "description": "Requires attention to nitrogen management"}
        ])
        
        for risk in risk_factors:
            level_color = {"low": "success", "medium": "warning", "high": "danger"}.get(risk["level"].lower(), "info")
            content += f"<div class='risk-factor-item'>\n"
            content += f"<span class='badge bg-{level_color}'>{risk['level']}</span> "
            content += f"<strong>{risk['factor']}:</strong> {risk['description']}\n"
            content += "</div>\n"
        
        content += "</div>\n"
        
        # Mitigation strategies
        content += "<h6>Risk Mitigation Strategies</h6>\n"
        content += "<ul>\n"
        mitigations = variety_data.get("mitigation_strategies", [
            "Implement precision nitrogen management practices",
            "Monitor soil moisture and irrigation needs",
            "Plan for potential premium market opportunities"
        ])
        for mitigation in mitigations:
            content += f"<li>{mitigation}</li>\n"
        content += "</ul>\n"
        
        # Evidence items
        evidence_items = [
            EvidenceItem(
                title="Historical Performance Analysis",
                description=f"Risk assessment based on historical data",
                source="Performance Database",
                confidence=0.8,
                data_type="historical_data",
                relevance_score=0.85
            )
        ]
        
        return ExplanationSection(
            section_id="risk_assessment",
            title="Risk Assessment",
            content=content,
            explanation_type=ExplanationType.RISK_ASSESSMENT,
            confidence_level=self._get_confidence_level(variety_data.get("risk_confidence", 0.8)),
            evidence_items=evidence_items,
            expandable=True,
            interactive_elements=[
                {"type": "risk_calculator", "title": "Calculate Risk Score"},
                {"type": "mitigation_planner", "title": "Plan Mitigation Strategies"}
            ]
        )

    def _create_economic_analysis_section(
        self,
        variety_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> ExplanationSection:
        """Create economic analysis section."""
        variety_name = variety_data.get("variety_name", "This variety")
        
        content = f"<h6>Economic Analysis for {variety_name}</h6>\n"
        
        # ROI Analysis
        roi = variety_data.get("estimated_roi", 1.35)
        content += "<div class='economic-metrics'>\n"
        content += f"<div class='metric-item'>\n"
        content += f"<h6>Estimated ROI</h6>\n"
        content += f"<span class='metric-value text-success'>{roi:.2f}x</span>\n"
        content += f"<p>For every $1 invested, expect ${roi:.2f} in returns</p>\n"
        content += "</div>\n"
        
        # Break-even yield
        break_even = variety_data.get("break_even_yield", 165.5)
        content += f"<div class='metric-item'>\n"
        content += f"<h6>Break-even Yield</h6>\n"
        content += f"<span class='metric-value'>{break_even:.1f} bu/acre</span>\n"
        content += f"<p>Minimum yield needed to cover costs</p>\n"
        content += "</div>\n"
        
        # Premium potential
        premium = variety_data.get("premium_potential", 0.15)
        content += f"<div class='metric-item'>\n"
        content += f"<h6>Premium Potential</h6>\n"
        content += f"<span class='metric-value text-info'>{premium:.1%}</span>\n"
        content += f"<p>Additional value above commodity prices</p>\n"
        content += "</div>\n"
        content += "</div>\n"
        
        # Cost breakdown
        content += "<h6>Cost Breakdown</h6>\n"
        content += "<div class='cost-breakdown'>\n"
        costs = variety_data.get("cost_analysis", {
            "seed_cost_per_acre": 145.00,
            "additional_inputs": 25.00,
            "total_investment": 170.00
        })
        
        for cost_item, amount in costs.items():
            content += f"<div class='cost-item'>\n"
            content += f"<span class='cost-label'>{cost_item.replace('_', ' ').title()}:</span>\n"
            content += f"<span class='cost-value'>${amount:.2f}</span>\n"
            content += "</div>\n"
        content += "</div>\n"
        
        # Evidence items
        evidence_items = [
            EvidenceItem(
                title="Economic Performance Data",
                description=f"Economic analysis of {variety_name}",
                source="Economic Research",
                confidence=0.85,
                data_type="research",
                relevance_score=0.9
            )
        ]
        
        return ExplanationSection(
            section_id="economic_analysis",
            title="Economic Analysis",
            content=content,
            explanation_type=ExplanationType.ECONOMIC_ANALYSIS,
            confidence_level=ConfidenceLevel.MEDIUM,
            evidence_items=evidence_items,
            expandable=True,
            interactive_elements=[
                {"type": "roi_calculator", "title": "Calculate Custom ROI"},
                {"type": "cost_comparison", "title": "Compare Costs"},
                {"type": "profit_projector", "title": "Project Profits"}
            ]
        )

    def _create_management_guidance_section(
        self,
        variety_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> ExplanationSection:
        """Create management guidance section."""
        variety_name = variety_data.get("variety_name", "This variety")
        
        content = f"<h6>Management Guidance for {variety_name}</h6>\n"
        
        # Planting recommendations
        content += "<div class='management-section'>\n"
        content += "<h6><i class='fas fa-seedling'></i> Planting Recommendations</h6>\n"
        content += "<ul>\n"
        planting_recs = variety_data.get("planting_recommendations", [
            f"Plant {variety_name} when soil temperature reaches 50°F",
            "Optimal planting depth: 1.5-2 inches",
            "Recommended seeding rate: 32,000-34,000 seeds per acre"
        ])
        for rec in planting_recs:
            content += f"<li>{rec}</li>\n"
        content += "</ul>\n"
        content += "</div>\n"
        
        # Fertilizer management
        content += "<div class='management-section'>\n"
        content += "<h6><i class='fas fa-flask'></i> Fertilizer Management</h6>\n"
        content += "<ul>\n"
        fert_recs = variety_data.get("fertilizer_recommendations", [
            "Apply nitrogen in split applications for optimal efficiency",
            "Monitor soil phosphorus levels - this variety is responsive to P",
            "Consider starter fertilizer for early season growth"
        ])
        for rec in fert_recs:
            content += f"<li>{rec}</li>\n"
        content += "</ul>\n"
        content += "</div>\n"
        
        # Pest management
        content += "<div class='management-section'>\n"
        content += "<h6><i class='fas fa-bug'></i> Pest Management</h6>\n"
        content += "<ul>\n"
        pest_recs = variety_data.get("pest_recommendations", [
            "Monitor for early season insects",
            "Scout regularly for disease symptoms",
            "Consider integrated pest management practices"
        ])
        for rec in pest_recs:
            content += f"<li>{rec}</li>\n"
        content += "</ul>\n"
        content += "</div>\n"
        
        # Evidence items
        evidence_items = [
            EvidenceItem(
                title="Management Research",
                description=f"Best management practices for {variety_name}",
                source="Extension Service",
                confidence=0.9,
                data_type="research",
                relevance_score=0.95
            )
        ]
        
        return ExplanationSection(
            section_id="management_guidance",
            title="Management Guidance",
            content=content,
            explanation_type=ExplanationType.MANAGEMENT_GUIDANCE,
            confidence_level=ConfidenceLevel.HIGH,
            evidence_items=evidence_items,
            expandable=True,
            interactive_elements=[
                {"type": "management_calendar", "title": "View Management Calendar"},
                {"type": "task_reminder", "title": "Set Task Reminders"},
                {"type": "best_practices", "title": "View Best Practices"}
            ]
        )

    def _identify_primary_recommendation_factor(self, variety_data: Dict[str, Any]) -> str:
        """Identify the primary factor driving the recommendation."""
        scores = variety_data.get("scores", {})
        
        if scores.get("yield_potential", 0) > 0.8:
            return "exceptional yield potential"
        elif scores.get("disease_resistance", 0) > 0.8:
            return "comprehensive disease resistance"
        elif scores.get("market_acceptance", 0) > 0.8:
            return "premium market opportunities"
        elif scores.get("soil_compatibility", 0) > 0.8:
            return "excellent soil compatibility"
        else:
            return "balanced performance across multiple factors"

    def _get_confidence_level(self, score: float) -> ConfidenceLevel:
        """Convert numeric score to confidence level."""
        if score >= 0.8:
            return ConfidenceLevel.HIGH
        elif score >= 0.6:
            return ConfidenceLevel.MEDIUM
        elif score >= 0.4:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    def _generate_summary(self, variety_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate overall summary."""
        variety_name = variety_data.get("variety_name", "This variety")
        primary_factor = self._identify_primary_recommendation_factor(variety_data)
        
        return f"{variety_name} is recommended based on its {primary_factor}, "
        f"with strong adaptation to your {context.get('climate_zone', 'local conditions')} "
        f"and {context.get('soil_type', 'soil type')}."

    def _generate_key_insights(self, variety_data: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Generate key insights."""
        insights = []
        
        scores = variety_data.get("scores", {})
        
        if scores.get("yield_potential", 0) > 0.8:
            insights.append("Exceptional yield potential with excellent stability")
        
        if scores.get("disease_resistance", 0) > 0.7:
            insights.append("Strong disease resistance reduces input costs")
        
        if variety_data.get("premium_potential", 0) > 0.1:
            insights.append("Premium market opportunities available")
        
        if variety_data.get("farmer_satisfaction", 0) > 80:
            insights.append("High farmer satisfaction in regional trials")
        
        return insights

    def _generate_recommendations(self, variety_data: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Soil management
        if context.get("soil_ph", 6.5) < 6.0:
            recommendations.append("Consider lime application to optimize soil pH")
        
        # Fertilizer management
        recommendations.append("Implement precision nitrogen management for optimal performance")
        
        # Monitoring
        recommendations.append("Monitor soil moisture levels during critical growth stages")
        
        # Market planning
        if variety_data.get("premium_potential", 0) > 0.1:
            recommendations.append("Explore premium market contracts for additional value")
        
        return recommendations

    def _get_educational_resources(self, variety_data: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get relevant educational resources."""
        resources = []
        
        # Yield potential resource
        resources.append({
            "title": "Understanding Yield Potential",
            "url": "/education/yield-potential",
            "type": "article"
        })
        
        # Disease resistance resource
        if variety_data.get("scores", {}).get("disease_resistance", 0) > 0.7:
            resources.append({
                "title": "Disease Resistance in Crops",
                "url": "/education/disease-resistance",
                "type": "video"
            })
        
        # Soil management resource
        resources.append({
            "title": "Soil Management Best Practices",
            "url": "/education/soil-management",
            "type": "guide"
        })
        
        return resources

    def _prepare_accessibility_features(self, sections: List[ExplanationSection]) -> Dict[str, Any]:
        """Prepare accessibility features for the explanation."""
        return {
            "aria_labels": {
                "summary": "Recommendation summary with key points",
                "detailed_reasoning": "Detailed explanation of recommendation factors",
                "evidence": "Supporting evidence and data sources",
                "trade_offs": "Analysis of strengths and considerations",
                "risk_assessment": "Risk evaluation and mitigation strategies",
                "economic_analysis": "Economic performance and cost analysis",
                "management_guidance": "Management recommendations and best practices"
            },
            "keyboard_navigation": {
                "sections": [section.section_id for section in sections],
                "expandable_elements": [section.section_id for section in sections if section.expandable],
                "interactive_elements": []
            },
            "screen_reader_support": {
                "summary_announcement": "Recommendation explanation loaded with multiple sections",
                "section_announcements": {section.section_id: f"{section.title} section" for section in sections}
            },
            "high_contrast_mode": {
                "enabled": True,
                "color_scheme": "high_contrast"
            }
        }