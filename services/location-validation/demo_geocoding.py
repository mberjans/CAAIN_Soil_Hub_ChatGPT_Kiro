"""
Demo script for geocoding service functionality.

This script demonstrates the geocoding service capabilities including:
- Address to coordinates conversion
- Reverse geocoding (coordinates to address)
- Address autocomplete suggestions
- Caching functionality
- Error handling

Run this script to test the geocoding service with real data.
"""

import asyncio
import logging
import sys
import os
from typing import List

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src/services'))

from geocoding_service import GeocodingService, GeocodingError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_address_geocoding():
    """Demonstrate address to coordinates conversion."""
    print("\n" + "="*60)
    print("DEMO: Address Geocoding (Address → Coordinates)")
    print("="*60)
    
    service = GeocodingService()
    
    # Test addresses (agricultural/rural focus)
    test_addresses = [
        "Ames, Iowa",
        "Iowa State University, Ames, IA",
        "123 Main Street, Ames, Iowa",
        "Rural Route 1, Story County, Iowa",
        "Farm Road 123, Boone County, Iowa",
        "InvalidAddressThatDoesNotExist12345"  # Test error handling
    ]
    
    for address in test_addresses:
        print(f"\nGeocoding: '{address}'")
        try:
            result = await service.geocode_address(address)
            
            print(f"  ✓ Success!")
            print(f"    Coordinates: {result.latitude:.6f}, {result.longitude:.6f}")
            print(f"    Formatted Address: {result.address}")
            print(f"    Display Name: {result.display_name}")
            print(f"    Confidence: {result.confidence:.2f}")
            print(f"    Provider: {result.provider}")
            
            if result.components:
                print(f"    Components: {dict(list(result.components.items())[:3])}...")  # Show first 3
            
        except GeocodingError as e:
            print(f"  ✗ Failed: {e.message}")
            print(f"    Provider: {e.provider}")
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
    
    await service.close()


async def demo_reverse_geocoding():
    """Demonstrate coordinates to address conversion."""
    print("\n" + "="*60)
    print("DEMO: Reverse Geocoding (Coordinates → Address)")
    print("="*60)
    
    service = GeocodingService()
    
    # Test coordinates (Iowa agricultural areas)
    test_coordinates = [
        (42.0308, -93.6319),  # Ames, Iowa (Iowa State University)
        (41.5868, -93.6250),  # Des Moines, Iowa
        (42.5080, -94.1742),  # Fort Dodge, Iowa
        (41.2033, -95.8608),  # Omaha, Nebraska (nearby)
        (0.0, 0.0),           # Invalid location (ocean)
        (91.0, -93.0)         # Invalid coordinates
    ]
    
    for lat, lon in test_coordinates:
        print(f"\nReverse geocoding: {lat:.4f}, {lon:.4f}")
        try:
            result = await service.reverse_geocode(lat, lon)
            
            print(f"  ✓ Success!")
            print(f"    Address: {result.address}")
            print(f"    Display Name: {result.display_name}")
            print(f"    Confidence: {result.confidence:.2f}")
            print(f"    Provider: {result.provider}")
            
            if result.components:
                print(f"    Components: {dict(list(result.components.items())[:3])}...")
            
        except GeocodingError as e:
            print(f"  ✗ Failed: {e.message}")
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
    
    await service.close()


async def demo_address_suggestions():
    """Demonstrate address autocomplete suggestions."""
    print("\n" + "="*60)
    print("DEMO: Address Suggestions (Autocomplete)")
    print("="*60)
    
    service = GeocodingService()
    
    # Test queries (agricultural/rural focus)
    test_queries = [
        "Ames",
        "Iowa State",
        "Farm Road",
        "Rural Route",
        "County Highway",
        "Main Street, Ames",
        "123",  # Short query
        "",     # Empty query
        "XYZ123NonexistentPlace"  # Non-existent place
    ]
    
    for query in test_queries:
        print(f"\nGetting suggestions for: '{query}'")
        try:
            suggestions = await service.get_address_suggestions(query, limit=5)
            
            if suggestions:
                print(f"  ✓ Found {len(suggestions)} suggestions:")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"    {i}. {suggestion.display_name}")
                    print(f"       Address: {suggestion.address}")
                    if suggestion.latitude and suggestion.longitude:
                        print(f"       Coordinates: {suggestion.latitude:.4f}, {suggestion.longitude:.4f}")
                    print(f"       Relevance: {suggestion.relevance:.2f}")
                    print()
            else:
                print(f"  ○ No suggestions found")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    await service.close()


async def demo_caching_performance():
    """Demonstrate caching functionality and performance."""
    print("\n" + "="*60)
    print("DEMO: Caching Performance")
    print("="*60)
    
    service = GeocodingService()
    
    address = "Ames, Iowa"
    
    print(f"Testing caching with address: '{address}'")
    
    # First request (should hit the provider)
    print("\n1. First request (cache miss):")
    import time
    start_time = time.time()
    try:
        result1 = await service.geocode_address(address)
        first_time = time.time() - start_time
        print(f"   ✓ Success in {first_time:.3f} seconds")
        print(f"   Coordinates: {result1.latitude:.6f}, {result1.longitude:.6f}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        await service.close()
        return
    
    # Second request (should use cache)
    print("\n2. Second request (cache hit):")
    start_time = time.time()
    try:
        result2 = await service.geocode_address(address)
        second_time = time.time() - start_time
        print(f"   ✓ Success in {second_time:.3f} seconds")
        print(f"   Coordinates: {result2.latitude:.6f}, {result2.longitude:.6f}")
        
        # Verify results are identical
        if (result1.latitude == result2.latitude and 
            result1.longitude == result2.longitude):
            print("   ✓ Results are identical (cache working)")
        else:
            print("   ⚠ Results differ (cache may not be working)")
        
        # Show performance improvement
        if second_time < first_time:
            improvement = ((first_time - second_time) / first_time) * 100
            print(f"   ✓ Cache improved performance by {improvement:.1f}%")
        
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    await service.close()


async def demo_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n" + "="*60)
    print("DEMO: Error Handling")
    print("="*60)
    
    service = GeocodingService()
    
    print("Testing various error conditions:")
    
    # Test empty address
    print("\n1. Empty address:")
    try:
        await service.geocode_address("")
    except GeocodingError as e:
        print(f"   ✓ Correctly handled: {e.message}")
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
    
    # Test invalid coordinates
    print("\n2. Invalid coordinates:")
    try:
        await service.reverse_geocode(91.0, -93.0)  # Invalid latitude
    except GeocodingError as e:
        print(f"   ✓ Correctly handled: {e.message}")
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
    
    # Test very short query for suggestions
    print("\n3. Very short query:")
    try:
        suggestions = await service.get_address_suggestions("A")
        print(f"   ✓ Handled gracefully: {len(suggestions)} suggestions")
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
    
    await service.close()


async def demo_agricultural_use_cases():
    """Demonstrate agricultural-specific use cases."""
    print("\n" + "="*60)
    print("DEMO: Agricultural Use Cases")
    print("="*60)
    
    service = GeocodingService()
    
    print("Testing agricultural/rural address patterns:")
    
    # Agricultural addresses
    agricultural_addresses = [
        "County Road 123, Story County, Iowa",
        "Farm Road 456, Boone County, Iowa",
        "Rural Route 2, Box 789, Ames, IA",
        "Township Road 15, Agricultural Area, Iowa",
        "Section 12, Township 84N, Range 24W, Iowa"
    ]
    
    for address in agricultural_addresses:
        print(f"\nTesting: '{address}'")
        try:
            result = await service.geocode_address(address)
            print(f"   ✓ Geocoded successfully")
            print(f"     Coordinates: {result.latitude:.6f}, {result.longitude:.6f}")
            print(f"     Confidence: {result.confidence:.2f}")
            
            # Test reverse geocoding to see if we get back something reasonable
            reverse_result = await service.reverse_geocode(result.latitude, result.longitude)
            print(f"     Reverse geocoded: {reverse_result.address}")
            
        except GeocodingError as e:
            print(f"   ○ Could not geocode: {e.message}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    await service.close()


async def main():
    """Run all geocoding demos."""
    print("AFAS Geocoding Service Demo")
    print("=" * 60)
    print("This demo tests the geocoding service functionality")
    print("with real API calls to OpenStreetMap Nominatim.")
    print("\nNote: This requires internet connection and may take a few moments.")
    
    input("\nPress Enter to start the demo...")
    
    try:
        # Run all demos
        await demo_address_geocoding()
        await demo_reverse_geocoding()
        await demo_address_suggestions()
        await demo_caching_performance()
        await demo_error_handling()
        await demo_agricultural_use_cases()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)
        print("All geocoding functionality has been demonstrated.")
        print("Check the output above for results and any issues.")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo failed with error: {e}")
        logger.exception("Demo failed")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())