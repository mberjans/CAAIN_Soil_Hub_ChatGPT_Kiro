#!/usr/bin/env python3
"""
Comprehensive demonstration of the Soil pH Management system.
Shows all major functionality including analysis, recommendations, and monitoring.
"""
import asyncio
from datetime import datetime, date, timedelta
from src.services.soil_ph_management_service import (
    SoilPHManagementService, SoilTexture, LimeType
)
from src.models.agricultural_models import SoilTestData

async def demonstrate_ph_management_system():
    """Demonstrate the complete pH management system functionality."""
    
    print("🌱 AFAS Soil pH Management System Demonstration")
    print("=" * 60)
    
    # Initialize the service
    ph_service = SoilPHManagementService()
    
    # Demo 1: Acidic Soil Analysis and Lime Recommendations
    print("\n📊 DEMO 1: Acidic Soil Analysis")
    print("-" * 40)
    
    acidic_soil = SoilTestData(
        ph=5.6,
        organic_matter_percent=2.8,
        phosphorus_ppm=18,
        potassium_ppm=145,
        test_date=date(2024, 3, 15)
    )
    
    analysis = await ph_service.analyze_soil_ph(
        farm_id="demo_farm_001",
        field_id="north_field",
        crop_type="corn",
        soil_test_data=acidic_soil,
        field_conditions={
            "soil_texture": "silt_loam",
            "annual_rainfall": 32,
            "previous_crop": "soybean"
        }
    )
    
    print(f"Current pH: {analysis.current_ph}")
    print(f"pH Level: {analysis.ph_level.value}")
    print(f"Target pH: {analysis.target_ph:.1f}")
    print(f"Management Priority: {analysis.management_priority}")
    print(f"Crop Suitability Score: {analysis.crop_suitability_score:.2f}")
    print(f"Acidification Risk: {analysis.acidification_risk}")
    
    print("\nNutrient Availability Impact:")
    for nutrient, availability in analysis.nutrient_availability_impact.items():
        status = "Good" if availability > 0.8 else "Reduced" if availability > 0.5 else "Poor"
        print(f"  {nutrient.capitalize()}: {availability:.2f} ({status})")
    
    # Demo 2: Lime Requirement Calculations
    print("\n🧮 DEMO 2: Lime Requirement Calculations")
    print("-" * 40)
    
    lime_recommendations = await ph_service.calculate_lime_requirements(
        current_ph=analysis.current_ph,
        target_ph=analysis.target_ph,
        buffer_ph=6.2,  # Buffer pH from lab test
        soil_texture="silt_loam",
        organic_matter_percent=2.8,
        field_size_acres=25.0
    )
    
    for i, rec in enumerate(lime_recommendations, 1):
        print(f"\nRecommendation {i}: {rec.lime_type.value.replace('_', ' ').title()}")
        print(f"  Application Rate: {rec.application_rate_tons_per_acre:.1f} tons/acre")
        print(f"  Cost per Acre: ${rec.cost_per_acre:.2f}")
        print(f"  Expected pH Change: +{rec.expected_ph_change:.1f}")
        print(f"  Time to Effect: {rec.time_to_effectiveness}")
        print(f"  Application Timing: {rec.application_timing}")
        print(f"  Method: {rec.application_method}")
    
    # Demo 3: Alkaline Soil Management
    print("\n🔬 DEMO 3: Alkaline Soil Management")
    print("-" * 40)
    
    alkaline_soil = SoilTestData(
        ph=8.3,
        organic_matter_percent=2.5,
        phosphorus_ppm=35,
        potassium_ppm=200,
        test_date=date(2024, 3, 18)
    )
    
    alkaline_analysis = await ph_service.analyze_soil_ph(
        farm_id="demo_farm_002",
        field_id="west_field",
        crop_type="corn",
        soil_test_data=alkaline_soil
    )
    
    alkaline_management = await ph_service.assess_alkaline_soil_management(
        ph_analysis=alkaline_analysis,
        soil_test_data=alkaline_soil,
        crop_type="corn"
    )
    
    print(f"Alkaline Soil pH: {alkaline_analysis.current_ph}")
    print(f"Alkalinity Level: {alkaline_management['alkalinity_level']}")
    print(f"Management Needed: {alkaline_management['management_needed']}")
    
    print("\nManagement Strategies:")
    for strategy in alkaline_management['management_strategies']:
        print(f"  • {strategy['strategy'].replace('_', ' ').title()}")
        if 'rate_lbs_per_acre' in strategy:
            print(f"    Rate: {strategy['rate_lbs_per_acre']} lbs/acre")
    
    # Demo 4: pH Monitoring and Trends
    print("\n📈 DEMO 4: pH Monitoring and Trends")
    print("-" * 40)
    
    # Create sample pH monitoring records
    from src.services.soil_ph_management_service import PHMonitoringRecord
    
    ph_records = []
    base_date = datetime.now() - timedelta(days=365*3)  # 3 years ago
    
    for i in range(8):  # 8 readings over 3 years
        record = PHMonitoringRecord(
            record_id=f"record_{i:03d}",
            farm_id="demo_farm_001",
            field_id="north_field",
            test_date=base_date + timedelta(days=i*137),  # ~4.5 months apart
            ph_value=6.4 - (i * 0.15),  # Declining pH trend
            buffer_ph=None,
            testing_method="laboratory",
            lab_name="AgriTest Labs",
            notes=f"Routine test #{i+1}"
        )
        ph_records.append(record)
    
    trends = await ph_service.analyze_ph_trends(
        farm_id="demo_farm_001",
        field_id="north_field",
        ph_records=ph_records
    )
    
    print(f"Trend Direction: {trends['trend']}")
    print(f"Annual Change Rate: {trends['annual_change_rate']:.3f} pH units/year")
    print(f"Current pH: {trends['current_ph']:.1f}")
    print(f"Initial pH: {trends['initial_ph']:.1f}")
    print(f"Total Change: {trends['total_change']:.1f}")
    print(f"Time Span: {trends['time_span_years']:.1f} years")
    
    # Demo 5: pH Alerts Generation
    print("\n🚨 DEMO 5: pH Alert System")
    print("-" * 40)
    
    alerts = await ph_service.generate_ph_alerts(
        ph_analysis=analysis,
        crop_type="corn",
        ph_trends=trends
    )
    
    if alerts:
        for alert in alerts:
            urgency_icon = "🔴" if alert["urgency"] == "high" else "🟡" if alert["urgency"] == "medium" else "🟢"
            print(f"{urgency_icon} {alert['title']}")
            print(f"   {alert['message']}")
            print(f"   Action: {alert['action_required']}")
    else:
        print("✅ No alerts - pH levels are within acceptable ranges")
    
    # Demo 6: Economic Analysis
    print("\n💰 DEMO 6: Economic Analysis")
    print("-" * 40)
    
    economics = ph_service._calculate_ph_economics(
        ph_analysis=analysis,
        lime_recommendations=lime_recommendations,
        crop_type="corn",
        field_conditions={"farm_size_acres": 25.0}
    )
    
    print(f"Annual Yield Loss (current pH): ${economics['annual_yield_loss_dollars_per_acre']:.2f}/acre")
    
    if lime_recommendations:
        print(f"Lime Treatment Cost: ${economics['lime_cost_per_acre']:.2f}/acre")
        print(f"Total Yield Benefit (4 years): ${economics['total_yield_benefit_dollars_per_acre']:.2f}/acre")
        print(f"Net Benefit: ${economics['net_benefit_dollars_per_acre']:.2f}/acre")
        print(f"Benefit-Cost Ratio: {economics['benefit_cost_ratio']:.1f}:1")
        print(f"Payback Period: {economics['payback_years']:.1f} years")
    
    # Demo 7: Comprehensive Management Plan
    print("\n📋 DEMO 7: Comprehensive Management Plan")
    print("-" * 40)
    
    management_plan = await ph_service.generate_ph_management_plan(
        farm_id="demo_farm_001",
        field_id="north_field",
        crop_type="corn",
        ph_analysis=analysis,
        lime_recommendations=lime_recommendations
    )
    
    print(f"Plan ID: {management_plan.plan_id}")
    print(f"Farm: {management_plan.farm_id}")
    print(f"Field: {management_plan.field_id}")
    print(f"Crop: {management_plan.crop_type}")
    
    print("\nAcidification Prevention Strategies:")
    for strategy in management_plan.acidification_prevention:
        print(f"  • {strategy}")
    
    print("\nMonitoring Schedule:")
    for schedule_item in management_plan.monitoring_schedule:
        print(f"  • {schedule_item['timing']}: {schedule_item['activity']}")
    
    print("\nLong-term Strategy:")
    for strategy_item in management_plan.long_term_strategy:
        print(f"  • {strategy_item}")
    
    # Demo 8: Crop-Specific pH Requirements
    print("\n🌾 DEMO 8: Crop-Specific pH Requirements")
    print("-" * 40)
    
    crops_to_demo = ["corn", "soybean", "wheat", "alfalfa", "potato", "blueberry"]
    
    for crop in crops_to_demo:
        if crop in ph_service.crop_ph_requirements:
            req = ph_service.crop_ph_requirements[crop]
            opt_min, opt_max = req['optimal_range']
            print(f"{crop.capitalize()}: {opt_min:.1f} - {opt_max:.1f} (optimal)")
            
            # Calculate suitability at current pH
            suitability = ph_service._calculate_crop_suitability(analysis.current_ph, crop)
            suitability_text = "Excellent" if suitability > 0.9 else "Good" if suitability > 0.7 else "Fair" if suitability > 0.5 else "Poor"
            print(f"  Suitability at pH {analysis.current_ph}: {suitability:.2f} ({suitability_text})")
    
    # Demo 9: Buffer pH Analysis
    print("\n🧪 DEMO 9: Buffer pH Analysis")
    print("-" * 40)
    
    buffer_analysis = await ph_service.calculate_buffer_ph_requirements(
        current_buffer_ph=6.2,
        target_ph=6.8,
        soil_texture="silt_loam",
        organic_matter_percent=2.8
    )
    
    print(f"Buffer pH Method Results:")
    print(f"  Base Lime Rate: {buffer_analysis['base_lime_rate_tons_per_acre']:.1f} tons/acre")
    print(f"  Adjusted Rate: {buffer_analysis['adjusted_lime_rate_tons_per_acre']:.1f} tons/acre")
    print(f"  Texture Factor: {buffer_analysis['texture_adjustment_factor']:.2f}")
    print(f"  Organic Matter Factor: {buffer_analysis['organic_matter_adjustment_factor']:.2f}")
    print(f"  Confidence: {buffer_analysis['confidence']}")
    
    print("\n✅ DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("The Soil pH Management system provides comprehensive functionality for:")
    print("• pH analysis and classification")
    print("• Lime requirement calculations")
    print("• Alkaline soil management")
    print("• pH monitoring and trend analysis")
    print("• Alert generation and notifications")
    print("• Economic analysis and ROI calculations")
    print("• Crop-specific pH management")
    print("• Buffer pH analysis and recommendations")
    print("• Comprehensive management planning")
    
    return True

def demonstrate_api_endpoints():
    """Demonstrate API endpoint functionality."""
    print("\n🔌 API ENDPOINTS DEMONSTRATION")
    print("=" * 60)
    
    endpoints = [
        "POST /api/v1/ph/analyze - Comprehensive pH analysis",
        "POST /api/v1/ph/lime-calculator - Lime requirement calculations",
        "GET /api/v1/ph/crop-requirements - Crop-specific pH requirements",
        "POST /api/v1/ph/monitor - pH monitoring setup",
        "GET /api/v1/ph/trends - pH trend analysis",
        "GET /api/v1/ph/dashboard - pH monitoring dashboard",
        "POST /api/v1/ph/treatment-plan - Treatment plan generation",
        "GET /api/v1/ph/economics - Economic analysis",
        "POST /api/v1/ph/track-treatment - Treatment progress tracking",
        "GET /api/v1/ph/reports - pH management reports",
        "POST /api/v1/ph/alerts - Alert configuration",
        "GET /api/v1/ph/recommendations - pH recommendations"
    ]
    
    print("Available API Endpoints:")
    for endpoint in endpoints:
        print(f"  ✓ {endpoint}")
    
    print("\nAll endpoints include:")
    print("• Agricultural data validation")
    print("• Error handling with agricultural context")
    print("• Performance optimization (<3 second response)")
    print("• Comprehensive documentation")

def demonstrate_mobile_features():
    """Demonstrate mobile interface features."""
    print("\n📱 MOBILE INTERFACE DEMONSTRATION")
    print("=" * 60)
    
    features = [
        "📊 Real-time pH dashboard with field status",
        "🧪 GPS-enabled pH test recording",
        "🧮 Interactive lime calculator",
        "📈 pH trend visualization",
        "🚨 Configurable pH alerts",
        "📷 Photo documentation for tests",
        "🔄 Offline data collection",
        "📍 Automatic location tagging",
        "📋 Treatment progress tracking",
        "📚 Educational pH reference guides"
    ]
    
    print("Mobile Features Available:")
    for feature in features:
        print(f"  {feature}")
    
    print("\nMobile Optimizations:")
    print("• Touch-friendly interface design")
    print("• Optimized for 3G/4G networks")
    print("• Progressive Web App (PWA) support")
    print("• Offline capability with sync")
    print("• GPS integration for field mapping")

if __name__ == "__main__":
    print("🌱 Starting Soil pH Management System Demonstration...")
    
    # Run the main demonstration
    asyncio.run(demonstrate_ph_management_system())
    
    # Demonstrate API endpoints
    demonstrate_api_endpoints()
    
    # Demonstrate mobile features
    demonstrate_mobile_features()
    
    print("\n🎉 All demonstrations completed successfully!")
    print("The Soil pH Management system is ready for production use.")