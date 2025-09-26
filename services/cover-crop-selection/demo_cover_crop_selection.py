#!/usr/bin/env python3
"""
Cover Crop Selection Service Demo

Demonstration script showing how to use the cover crop selection service.
"""

import asyncio
import httpx
import json
from datetime import date
from typing import Dict, Any


async def demo_cover_crop_selection():
    """Demonstrate cover crop selection functionality."""
    
    print("🌱 Cover Crop Selection Service Demo")
    print("=" * 50)
    
    # Service URL
    base_url = "http://localhost:8006"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 1. Check service health
            print("\n1. Checking service health...")
            health_response = await client.get(f"{base_url}/health")
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"✅ Service Status: {health_data['status']}")
                print(f"   Version: {health_data['version']}")
            else:
                print("❌ Service not available")
                return
                
        except Exception as e:
            print(f"❌ Cannot connect to service: {e}")
            print("   Make sure the service is running on port 8006")
            print("   Run: python start_service.py")
            return
        
        # 2. Get service information
        print("\n2. Getting service information...")
        try:
            info_response = await client.get(f"{base_url}/")
            if info_response.status_code == 200:
                info = info_response.json()
                print(f"✅ Service: {info['message']}")
                print("   Available endpoints:")
                for endpoint, url in info['endpoints'].items():
                    print(f"     - {endpoint}: {url}")
        except Exception as e:
            print(f"⚠️ Could not get service info: {e}")
        
        # 3. Lookup cover crop types
        print("\n3. Getting available cover crop types...")
        try:
            types_response = await client.get(f"{base_url}/api/v1/cover-crops/types")
            if types_response.status_code == 200:
                types_data = types_response.json()
                print("✅ Available cover crop types:")
                for crop_type in types_data['types']:
                    print(f"     - {crop_type['type']}: {crop_type['description']}")
        except Exception as e:
            print(f"⚠️ Could not get cover crop types: {e}")
        
        # 4. Lookup cover crop species
        print("\n4. Looking up legume cover crop species...")
        try:
            species_response = await client.get(
                f"{base_url}/api/v1/cover-crops/species",
                params={"cover_crop_type": "legume"}
            )
            if species_response.status_code == 200:
                species_data = species_response.json()
                print(f"✅ Found {species_data['species_count']} legume species:")
                for species in species_data['species_list'][:3]:  # Show first 3
                    print(f"     - {species['common_name']} ({species['scientific_name']})")
                    print(f"       Zones: {', '.join(species['hardiness_zones'])}")
            else:
                print("⚠️ Species lookup not available yet")
        except Exception as e:
            print(f"⚠️ Could not lookup species: {e}")
        
        # 5. Get seasonal recommendations
        print("\n5. Getting winter cover crop recommendations for NY area...")
        try:
            seasonal_response = await client.post(
                f"{base_url}/api/v1/cover-crops/seasonal",
                params={
                    "latitude": 42.3601,  # Albany, NY
                    "longitude": -73.9712,
                    "target_season": "winter",
                    "field_size_acres": 50.0
                }
            )
            
            if seasonal_response.status_code == 200:
                seasonal_data = seasonal_response.json()
                print("✅ Seasonal recommendations generated:")
                print(f"   Overall confidence: {seasonal_data['overall_confidence']:.2f}")
                
                if seasonal_data['single_species_recommendations']:
                    print("   Top recommendations:")
                    for i, rec in enumerate(seasonal_data['single_species_recommendations'][:2]):
                        print(f"     {i+1}. {rec['species']['common_name']}")
                        print(f"        Suitability: {rec['suitability_score']:.2f}")
                        print(f"        Benefits: {', '.join(rec['expected_benefits'][:2])}")
            else:
                print("⚠️ Seasonal recommendations not available yet")
                
        except Exception as e:
            print(f"⚠️ Could not get seasonal recommendations: {e}")
        
        # 6. Full cover crop selection example
        print("\n6. Performing full cover crop selection...")
        
        selection_request = {
            "request_id": "demo_farm_field_1",
            "location": {
                "latitude": 40.7589,  # New York area
                "longitude": -73.9851
            },
            "soil_conditions": {
                "ph": 6.2,
                "organic_matter_percent": 2.5,
                "drainage_class": "moderately_well_drained"
            },
            "objectives": {
                "primary_goals": ["nitrogen_fixation", "erosion_control"],
                "nitrogen_needs": True,
                "erosion_control_priority": True,
                "budget_per_acre": 80.0,
                "management_intensity": "moderate"
            },
            "planting_window": {
                "start": "2024-09-15",
                "end": "2024-10-15"
            },
            "field_size_acres": 35.0,
            "farming_system": "conventional"
        }
        
        try:
            selection_response = await client.post(
                f"{base_url}/api/v1/cover-crops/select",
                json=selection_request
            )
            
            if selection_response.status_code == 200:
                selection_data = selection_response.json()
                print("✅ Full cover crop selection completed:")
                print(f"   Request ID: {selection_data['request_id']}")
                print(f"   Overall confidence: {selection_data['overall_confidence']:.2f}")
                
                # Show field assessment
                field_assessment = selection_data['field_assessment']
                print(f"   Soil health score: {field_assessment['soil_health_score']:.2f}")
                
                if field_assessment['advantages']:
                    print("   Field advantages:")
                    for advantage in field_assessment['advantages']:
                        print(f"     ✓ {advantage}")
                
                # Show top recommendations
                recommendations = selection_data['single_species_recommendations']
                if recommendations:
                    print(f"   Top {min(3, len(recommendations))} recommendations:")
                    for i, rec in enumerate(recommendations[:3]):
                        print(f"     {i+1}. {rec['species']['common_name']}")
                        print(f"        Suitability: {rec['suitability_score']:.2f}")
                        print(f"        Seeding rate: {rec['seeding_rate_recommendation']} lbs/acre")
                        if rec['cost_per_acre']:
                            print(f"        Cost: ${rec['cost_per_acre']:.2f}/acre")
                        print(f"        Key benefits: {', '.join(rec['expected_benefits'][:2])}")
                
                # Show implementation timeline
                if selection_data['implementation_timeline']:
                    print("   Implementation timeline:")
                    for phase in selection_data['implementation_timeline']:
                        print(f"     - {phase['phase']}: {phase['date_range']}")
                
            else:
                error_detail = selection_response.json().get('detail', 'Unknown error')
                print(f"⚠️ Selection failed: {error_detail}")
                
        except Exception as e:
            print(f"⚠️ Could not perform cover crop selection: {e}")
        
        print("\n" + "=" * 50)
        print("🌱 Demo completed!")
        print("\nNext steps:")
        print("- Try different locations and soil conditions")
        print("- Experiment with different objectives")
        print("- Test seasonal recommendations for your area") 
        print("- Integrate with other CAAIN Soil Hub services")


def main():
    """Run the demo."""
    asyncio.run(demo_cover_crop_selection())


if __name__ == "__main__":
    main()