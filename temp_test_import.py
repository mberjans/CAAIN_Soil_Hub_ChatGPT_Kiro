import sys
sys.path.append('/Users/Mark/Research/CAAIN_Soil_Hub/CAAIN_Soil_Hub_ChatGPT_Kiro')

from services.micronutrient_management.src.models.micronutrient_models import MicronutrientPrice

print("Successfully imported MicronutrientPrice.")

try:
    price = MicronutrientPrice(micronutrient_name="Test", price_per_unit=1.0, unit="kg")
    print(f"Instantiated MicronutrientPrice: {price.micronutrient_name}")
except Exception as e:
    print(f"Error during instantiation: {e}")