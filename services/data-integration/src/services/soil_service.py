"""
Soil Data Service Module

Integrates with USDA soil survey databases and other soil data sources
to provide comprehensive soil information for agricultural decision making.
"""

import asyncio
import aiohttp
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import os
from dataclasses import dataclass
import structlog
import json
from urllib.parse import urlencode

logger = structlog.get_logger(__name__)


@dataclass
class SoilCharacteristics:
    """Standardized soil characteristics data structure."""
    soil_series: str
    soil_texture: str
    drainage_class: str
    typical_ph_range: Dict[str, float]
    organic_matter_typical: float
    slope_range: str
    parent_material: Optional[str] = None
    depth_to_bedrock: Optional[str] = None
    flooding_frequency: Optional[str] = None
    ponding_frequency: Optional[str] = None
    hydrologic_group: Optional[str] = None
    available_water_capacity: Optional[float] = None
    permeability: Optional[str] = None
    erosion_factor_k: Optional[float] = None


@dataclass
class SoilNutrientRanges:
    """Typical nutrient ranges for soil type."""
    phosphorus_ppm_range: Dict[str, float]
    potassium_ppm_range: Dict[str, float]
    nitrogen_typical: float
    cec_range: Dict[str, float]
    base_saturation_range: Dict[str, float]
    micronutrient_status: Dict[str, str]


@dataclass
class SoilSuitability:
    """Crop suitability ratings for soil type."""
    crop_suitability: Dict[str, str]  # crop_name -> rating (excellent, good, fair, poor)
    limitations: List[str]
    management_considerations: List[str]
    irrigation_suitability: str
    erosion_risk: str


class SoilDataError(Exception):
    """Custom exception for soil data errors."""
    pass


class USDAWebSoilSurveyService:
    """USDA Web Soil Survey API integration."""
    
    BASE_URL = "https://sdmdataaccess.sc.egov.usda.gov"
    
    def __init__(self):
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session."""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={"User-Agent": "AFAS/1.0 (Agricultural Advisory System)"}
            )
        return self.session
    
    async def get_soil_data_by_coordinates(self, latitude: float, longitude: float) -> SoilCharacteristics:
        """Get soil data from USDA Web Soil Survey by coordinates."""
        try:
            # First, get the map unit key for the location
            mukey = await self._get_mukey_by_coordinates(latitude, longitude)
            
            if not mukey:
                raise SoilDataError("No soil data found for location")
            
            # Get detailed soil information using the map unit key
            soil_data = await self._get_soil_details_by_mukey(mukey)
            
            return soil_data
            
        except Exception as e:
            logger.error("USDA soil data error", error=str(e), lat=latitude, lon=longitude)
            raise SoilDataError(f"Failed to get USDA soil data: {str(e)}")
    
    async def _get_mukey_by_coordinates(self, latitude: float, longitude: float) -> Optional[str]:
        """Get map unit key (mukey) for coordinates using USDA spatial query."""
        session = await self._get_session()
        
        # USDA SDA spatial query to get mukey
        query = f"""
        SELECT mukey
        FROM mapunit mu
        INNER JOIN sacatalog sac ON mu.lkey = sac.lkey
        WHERE ST_Intersects(
            mu.mupolygongeo,
            ST_GeomFromText('POINT({longitude} {latitude})', 4326)
        )
        """
        
        url = f"{self.BASE_URL}/Tabular/SDMTabularService/post.rest"
        data = {
            "query": query,
            "format": "JSON"
        }
        
        try:
            async with session.post(url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("Table") and len(result["Table"]) > 0:
                        return result["Table"][0]["mukey"]
                    return None
                else:
                    logger.warning("USDA mukey query failed", status=response.status)
                    return None
        except Exception as e:
            logger.error("USDA mukey query error", error=str(e))
            return None
    
    async def _get_soil_details_by_mukey(self, mukey: str) -> SoilCharacteristics:
        """Get detailed soil information using map unit key."""
        session = await self._get_session()
        
        # Complex query to get soil characteristics
        query = f"""
        SELECT 
            mu.muname as soil_series,
            c.comppct_r as component_percent,
            c.taxclname as taxonomic_class,
            c.drainagecl as drainage_class,
            c.slope_r as slope,
            c.om_r as organic_matter,
            c.ph1to1h2o_r as ph,
            c.awc_r as available_water_capacity,
            c.kffact as erosion_k_factor,
            c.hydgrp as hydrologic_group,
            c.flodfreqcl as flooding_frequency,
            c.pondfreqcl as ponding_frequency,
            cht.texcl as texture_class,
            cht.sandtotal_r as sand_percent,
            cht.silttotal_r as silt_percent,
            cht.claytotal_r as clay_percent,
            cht.cec7_r as cec
        FROM mapunit mu
        INNER JOIN component c ON mu.mukey = c.mukey
        LEFT JOIN chorizon ch ON c.cokey = ch.cokey
        LEFT JOIN chtexturegrp chtg ON ch.chkey = chtg.chkey
        LEFT JOIN chtexture cht ON chtg.chtgkey = cht.chtgkey
        WHERE mu.mukey = '{mukey}'
        AND c.majcompflag = 'Yes'
        AND ch.hzdept_r = 0
        ORDER BY c.comppct_r DESC
        LIMIT 1
        """
        
        url = f"{self.BASE_URL}/Tabular/SDMTabularService/post.rest"
        data = {
            "query": query,
            "format": "JSON"
        }
        
        try:
            async with session.post(url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("Table") and len(result["Table"]) > 0:
                        row = result["Table"][0]
                        return self._parse_usda_soil_data(row)
                    else:
                        raise SoilDataError("No detailed soil data found")
                else:
                    raise SoilDataError(f"USDA query failed: {response.status}")
        except Exception as e:
            logger.error("USDA soil details error", error=str(e))
            raise SoilDataError(f"Failed to get soil details: {str(e)}")
    
    def _parse_usda_soil_data(self, row: Dict[str, Any]) -> SoilCharacteristics:
        """Parse USDA soil data into standardized format."""
        # Determine texture class
        texture = row.get("texture_class", "unknown")
        if not texture or texture == "null":
            # Estimate texture from sand/silt/clay percentages
            sand = row.get("sand_percent", 0) or 0
            silt = row.get("silt_percent", 0) or 0
            clay = row.get("clay_percent", 0) or 0
            texture = self._estimate_texture_class(sand, silt, clay)
        
        # Determine pH range based on measured pH
        ph_measured = row.get("ph", 6.5) or 6.5
        ph_range = {
            "min": max(3.0, ph_measured - 0.5),
            "max": min(10.0, ph_measured + 0.5)
        }
        
        # Determine organic matter
        om = row.get("organic_matter", 3.0) or 3.0
        
        # Determine slope range
        slope = row.get("slope", 2.0) or 2.0
        slope_range = f"0-{int(slope + 2)}%"
        
        return SoilCharacteristics(
            soil_series=row.get("soil_series", "Unknown").title(),
            soil_texture=texture.lower().replace(" ", "_"),
            drainage_class=self._standardize_drainage_class(row.get("drainage_class", "well drained")),
            typical_ph_range=ph_range,
            organic_matter_typical=om,
            slope_range=slope_range,
            parent_material=None,  # Would need additional query
            depth_to_bedrock=None,  # Would need additional query
            flooding_frequency=row.get("flooding_frequency", "none"),
            ponding_frequency=row.get("ponding_frequency", "none"),
            hydrologic_group=row.get("hydrologic_group", "B"),
            available_water_capacity=row.get("available_water_capacity", 0.15),
            permeability=self._estimate_permeability(texture),
            erosion_factor_k=row.get("erosion_k_factor", 0.3)
        )
    
    def _estimate_texture_class(self, sand: float, silt: float, clay: float) -> str:
        """Estimate texture class from particle size percentages."""
        if clay >= 40:
            return "clay"
        elif clay >= 27:
            if sand >= 45:
                return "sandy_clay"
            elif silt >= 40:
                return "silty_clay"
            else:
                return "clay"
        elif clay >= 20:
            if sand >= 45:
                return "sandy_clay_loam"
            elif silt >= 28:
                return "silty_clay_loam"
            else:
                return "clay_loam"
        elif silt >= 50:
            if clay >= 12:
                return "silt_loam"
            else:
                return "silt"
        elif sand >= 70:
            if clay >= 15:
                return "sandy_loam"
            else:
                return "sand"
        else:
            return "loam"
    
    def _standardize_drainage_class(self, drainage: str) -> str:
        """Standardize drainage class to match database constraints."""
        drainage_lower = drainage.lower().replace(" ", "_")
        
        drainage_map = {
            "excessively_drained": "well_drained",
            "somewhat_excessively_drained": "well_drained",
            "well_drained": "well_drained",
            "moderately_well_drained": "moderately_well_drained",
            "somewhat_poorly_drained": "somewhat_poorly_drained",
            "poorly_drained": "poorly_drained",
            "very_poorly_drained": "very_poorly_drained"
        }
        
        return drainage_map.get(drainage_lower, "well_drained")
    
    def _estimate_permeability(self, texture: str) -> str:
        """Estimate permeability based on soil texture."""
        texture_permeability = {
            "sand": "rapid",
            "sandy_loam": "moderately_rapid",
            "loam": "moderate",
            "silt_loam": "moderate",
            "silt": "moderate",
            "clay_loam": "moderately_slow",
            "silty_clay_loam": "moderately_slow",
            "sandy_clay": "slow",
            "silty_clay": "slow",
            "clay": "very_slow"
        }
        
        return texture_permeability.get(texture.lower(), "moderate")
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()


class SoilGridsService:
    """SoilGrids global soil information service as fallback."""
    
    BASE_URL = "https://rest.soilgrids.org"
    
    async def get_soil_data_by_coordinates(self, latitude: float, longitude: float) -> SoilCharacteristics:
        """Get soil data from SoilGrids API."""
        try:
            # SoilGrids properties to query
            properties = [
                "phh2o",  # pH in water
                "soc",    # Soil organic carbon
                "sand",   # Sand content
                "silt",   # Silt content  
                "clay",   # Clay content
                "cec",    # Cation exchange capacity
                "bdod"    # Bulk density
            ]
            
            # Query SoilGrids API
            url = f"{self.BASE_URL}/query"
            params = {
                "lon": longitude,
                "lat": latitude,
                "property": properties,
                "depth": "0-5cm",  # Surface layer
                "value": "mean"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_soilgrids_data(data, latitude, longitude)
                else:
                    raise SoilDataError(f"SoilGrids API error: {response.status_code}")
                    
        except Exception as e:
            logger.error("SoilGrids error", error=str(e), lat=latitude, lon=longitude)
            raise SoilDataError(f"Failed to get SoilGrids data: {str(e)}")
    
    def _parse_soilgrids_data(self, data: Dict[str, Any], latitude: float, longitude: float) -> SoilCharacteristics:
        """Parse SoilGrids data into standardized format."""
        properties = data.get("properties", {})
        
        # Extract values (SoilGrids returns values in specific units)
        ph = properties.get("phh2o", {}).get("0-5cm", {}).get("mean", 65) / 10.0  # pH * 10
        sand = properties.get("sand", {}).get("0-5cm", {}).get("mean", 300) / 10.0  # g/kg to %
        silt = properties.get("silt", {}).get("0-5cm", {}).get("mean", 400) / 10.0  # g/kg to %
        clay = properties.get("clay", {}).get("0-5cm", {}).get("mean", 300) / 10.0  # g/kg to %
        soc = properties.get("soc", {}).get("0-5cm", {}).get("mean", 15) / 10.0  # dg/kg to %
        cec = properties.get("cec", {}).get("0-5cm", {}).get("mean", 150) / 10.0  # mmol(c)/kg to cmol/kg
        
        # Estimate organic matter from soil organic carbon
        organic_matter = soc * 1.724  # Van Bemmelen factor
        
        # Determine texture class
        texture = self._estimate_texture_class(sand, silt, clay)
        
        # Estimate drainage based on texture and location
        drainage = self._estimate_drainage_from_texture(texture)
        
        return SoilCharacteristics(
            soil_series=f"SoilGrids_{int(latitude*100)}_{int(longitude*100)}",
            soil_texture=texture,
            drainage_class=drainage,
            typical_ph_range={"min": ph - 0.3, "max": ph + 0.3},
            organic_matter_typical=organic_matter,
            slope_range="0-5%",  # Default for SoilGrids
            parent_material="Various",
            hydrologic_group="B",  # Default assumption
            available_water_capacity=0.15,  # Default assumption
            permeability=self._estimate_permeability(texture)
        )
    
    def _estimate_texture_class(self, sand: float, silt: float, clay: float) -> str:
        """Estimate texture class from particle size percentages."""
        # Same logic as USDA service
        if clay >= 40:
            return "clay"
        elif clay >= 27:
            if sand >= 45:
                return "sandy_clay"
            elif silt >= 40:
                return "silty_clay"
            else:
                return "clay"
        elif clay >= 20:
            if sand >= 45:
                return "sandy_clay_loam"
            elif silt >= 28:
                return "silty_clay_loam"
            else:
                return "clay_loam"
        elif silt >= 50:
            if clay >= 12:
                return "silt_loam"
            else:
                return "silt"
        elif sand >= 70:
            if clay >= 15:
                return "sandy_loam"
            else:
                return "sand"
        else:
            return "loam"
    
    def _estimate_drainage_from_texture(self, texture: str) -> str:
        """Estimate drainage class from soil texture."""
        drainage_map = {
            "sand": "well_drained",
            "sandy_loam": "well_drained",
            "loam": "moderately_well_drained",
            "silt_loam": "moderately_well_drained",
            "silt": "moderately_well_drained",
            "clay_loam": "somewhat_poorly_drained",
            "silty_clay_loam": "somewhat_poorly_drained",
            "sandy_clay": "poorly_drained",
            "silty_clay": "poorly_drained",
            "clay": "poorly_drained"
        }
        
        return drainage_map.get(texture, "moderately_well_drained")
    
    def _estimate_permeability(self, texture: str) -> str:
        """Estimate permeability based on soil texture."""
        texture_permeability = {
            "sand": "rapid",
            "sandy_loam": "moderately_rapid",
            "loam": "moderate",
            "silt_loam": "moderate",
            "silt": "moderate",
            "clay_loam": "moderately_slow",
            "silty_clay_loam": "moderately_slow",
            "sandy_clay": "slow",
            "silty_clay": "slow",
            "clay": "very_slow"
        }
        
        return texture_permeability.get(texture.lower(), "moderate")


class SoilService:
    """Main soil service with fallback capabilities and nutrient estimation."""
    
    def __init__(self):
        self.usda_service = USDAWebSoilSurveyService()
        self.soilgrids_service = SoilGridsService()
    
    async def get_soil_characteristics(self, latitude: float, longitude: float) -> SoilCharacteristics:
        """Get soil characteristics with fallback to multiple services."""
        # Try USDA first (most detailed for US locations)
        try:
            return await self.usda_service.get_soil_data_by_coordinates(latitude, longitude)
        except SoilDataError as e:
            logger.warning("USDA soil data failed, trying SoilGrids", error=str(e))
            
            # Fallback to SoilGrids (global coverage)
            try:
                return await self.soilgrids_service.get_soil_data_by_coordinates(latitude, longitude)
            except SoilDataError as e2:
                logger.error("All soil services failed", usda_error=str(e), soilgrids_error=str(e2))
                
                # Return default soil characteristics as last resort
                return self._get_default_soil_characteristics(latitude, longitude)
    
    async def get_nutrient_ranges(self, soil_characteristics: SoilCharacteristics) -> SoilNutrientRanges:
        """Get typical nutrient ranges for soil type."""
        try:
            # Estimate nutrient ranges based on soil characteristics
            texture = soil_characteristics.soil_texture
            drainage = soil_characteristics.drainage_class
            ph_avg = (soil_characteristics.typical_ph_range["min"] + 
                     soil_characteristics.typical_ph_range["max"]) / 2
            
            # Phosphorus ranges based on texture and pH
            p_ranges = self._estimate_phosphorus_ranges(texture, ph_avg)
            
            # Potassium ranges based on texture and CEC
            k_ranges = self._estimate_potassium_ranges(texture, drainage)
            
            # Nitrogen based on organic matter
            n_typical = soil_characteristics.organic_matter_typical * 20  # Rough estimate
            
            # CEC ranges based on texture and organic matter
            cec_ranges = self._estimate_cec_ranges(texture, soil_characteristics.organic_matter_typical)
            
            # Base saturation ranges
            base_sat_ranges = self._estimate_base_saturation_ranges(ph_avg)
            
            # Micronutrient status
            micronutrients = self._estimate_micronutrient_status(ph_avg, texture)
            
            return SoilNutrientRanges(
                phosphorus_ppm_range=p_ranges,
                potassium_ppm_range=k_ranges,
                nitrogen_typical=n_typical,
                cec_range=cec_ranges,
                base_saturation_range=base_sat_ranges,
                micronutrient_status=micronutrients
            )
            
        except Exception as e:
            logger.error("Nutrient range estimation failed", error=str(e))
            return self._get_default_nutrient_ranges()
    
    async def get_crop_suitability(self, soil_characteristics: SoilCharacteristics) -> SoilSuitability:
        """Get crop suitability ratings for soil type."""
        try:
            texture = soil_characteristics.soil_texture
            drainage = soil_characteristics.drainage_class
            ph_avg = (soil_characteristics.typical_ph_range["min"] + 
                     soil_characteristics.typical_ph_range["max"]) / 2
            
            # Evaluate crop suitability
            crop_ratings = {}
            
            # Corn suitability
            corn_rating = self._evaluate_corn_suitability(texture, drainage, ph_avg)
            crop_ratings["corn"] = corn_rating
            
            # Soybean suitability
            soybean_rating = self._evaluate_soybean_suitability(texture, drainage, ph_avg)
            crop_ratings["soybean"] = soybean_rating
            
            # Wheat suitability
            wheat_rating = self._evaluate_wheat_suitability(texture, drainage, ph_avg)
            crop_ratings["wheat"] = wheat_rating
            
            # Identify limitations
            limitations = self._identify_soil_limitations(soil_characteristics)
            
            # Management considerations
            management = self._get_management_considerations(soil_characteristics)
            
            # Irrigation suitability
            irrigation_suit = self._evaluate_irrigation_suitability(texture, drainage)
            
            # Erosion risk
            erosion_risk = self._evaluate_erosion_risk(soil_characteristics)
            
            return SoilSuitability(
                crop_suitability=crop_ratings,
                limitations=limitations,
                management_considerations=management,
                irrigation_suitability=irrigation_suit,
                erosion_risk=erosion_risk
            )
            
        except Exception as e:
            logger.error("Crop suitability evaluation failed", error=str(e))
            return self._get_default_crop_suitability()
    
    def _estimate_phosphorus_ranges(self, texture: str, ph: float) -> Dict[str, float]:
        """Estimate phosphorus ranges based on soil properties."""
        # Base ranges by texture
        base_ranges = {
            "sand": {"low": 8, "medium": 15, "high": 25},
            "sandy_loam": {"low": 10, "medium": 18, "high": 30},
            "loam": {"low": 12, "medium": 22, "high": 35},
            "silt_loam": {"low": 15, "medium": 25, "high": 40},
            "clay_loam": {"low": 18, "medium": 30, "high": 45},
            "clay": {"low": 20, "medium": 35, "high": 50}
        }
        
        ranges = base_ranges.get(texture, base_ranges["loam"])
        
        # Adjust for pH (P availability decreases at high pH)
        if ph > 7.5:
            multiplier = 1.2
        elif ph < 6.0:
            multiplier = 0.8
        else:
            multiplier = 1.0
        
        return {
            "low": ranges["low"] * multiplier,
            "medium": ranges["medium"] * multiplier,
            "high": ranges["high"] * multiplier
        }
    
    def _estimate_potassium_ranges(self, texture: str, drainage: str) -> Dict[str, float]:
        """Estimate potassium ranges based on soil properties."""
        # Base ranges by texture (higher clay = higher K retention)
        base_ranges = {
            "sand": {"low": 60, "medium": 100, "high": 150},
            "sandy_loam": {"low": 80, "medium": 120, "high": 180},
            "loam": {"low": 100, "medium": 150, "high": 220},
            "silt_loam": {"low": 120, "medium": 180, "high": 260},
            "clay_loam": {"low": 140, "medium": 200, "high": 300},
            "clay": {"low": 160, "medium": 240, "high": 350}
        }
        
        ranges = base_ranges.get(texture, base_ranges["loam"])
        
        # Adjust for drainage (poor drainage can increase K)
        if "poorly" in drainage:
            multiplier = 1.1
        else:
            multiplier = 1.0
        
        return {
            "low": ranges["low"] * multiplier,
            "medium": ranges["medium"] * multiplier,
            "high": ranges["high"] * multiplier
        }
    
    def _estimate_cec_ranges(self, texture: str, organic_matter: float) -> Dict[str, float]:
        """Estimate CEC ranges based on texture and organic matter."""
        # Base CEC by texture
        base_cec = {
            "sand": 5,
            "sandy_loam": 8,
            "loam": 12,
            "silt_loam": 15,
            "clay_loam": 20,
            "clay": 30
        }
        
        base = base_cec.get(texture, 12)
        
        # Add organic matter contribution (roughly 2 meq/100g per 1% OM)
        om_contribution = organic_matter * 2
        
        total_cec = base + om_contribution
        
        return {
            "min": total_cec * 0.8,
            "max": total_cec * 1.2
        }
    
    def _estimate_base_saturation_ranges(self, ph: float) -> Dict[str, float]:
        """Estimate base saturation ranges based on pH."""
        if ph < 5.5:
            return {"min": 40, "max": 60}
        elif ph < 6.5:
            return {"min": 60, "max": 80}
        else:
            return {"min": 80, "max": 95}
    
    def _estimate_micronutrient_status(self, ph: float, texture: str) -> Dict[str, str]:
        """Estimate micronutrient availability status."""
        status = {}
        
        # Iron - decreases with high pH
        if ph > 7.5:
            status["iron"] = "potentially_deficient"
        else:
            status["iron"] = "adequate"
        
        # Manganese - decreases with high pH
        if ph > 7.0:
            status["manganese"] = "potentially_deficient"
        else:
            status["manganese"] = "adequate"
        
        # Zinc - decreases with high pH, low in sandy soils
        if ph > 7.5 or "sand" in texture:
            status["zinc"] = "potentially_deficient"
        else:
            status["zinc"] = "adequate"
        
        # Boron - variable, often deficient in sandy soils
        if "sand" in texture:
            status["boron"] = "potentially_deficient"
        else:
            status["boron"] = "adequate"
        
        return status
    
    def _evaluate_corn_suitability(self, texture: str, drainage: str, ph: float) -> str:
        """Evaluate corn suitability for soil conditions."""
        score = 0
        
        # pH preference (6.0-6.8 optimal)
        if 6.0 <= ph <= 6.8:
            score += 3
        elif 5.8 <= ph <= 7.2:
            score += 2
        elif 5.5 <= ph <= 7.5:
            score += 1
        
        # Drainage preference (well to moderately well drained)
        if drainage in ["well_drained", "moderately_well_drained"]:
            score += 3
        elif drainage == "somewhat_poorly_drained":
            score += 1
        
        # Texture preference (loams are best)
        if texture in ["loam", "silt_loam", "clay_loam"]:
            score += 3
        elif texture in ["sandy_loam", "silty_clay_loam"]:
            score += 2
        elif texture in ["sand", "clay"]:
            score += 1
        
        # Convert score to rating
        if score >= 7:
            return "excellent"
        elif score >= 5:
            return "good"
        elif score >= 3:
            return "fair"
        else:
            return "poor"
    
    def _evaluate_soybean_suitability(self, texture: str, drainage: str, ph: float) -> str:
        """Evaluate soybean suitability for soil conditions."""
        score = 0
        
        # pH preference (6.0-7.0 optimal)
        if 6.0 <= ph <= 7.0:
            score += 3
        elif 5.8 <= ph <= 7.2:
            score += 2
        elif 5.5 <= ph <= 7.5:
            score += 1
        
        # Drainage preference (well to moderately well drained)
        if drainage in ["well_drained", "moderately_well_drained"]:
            score += 3
        elif drainage == "somewhat_poorly_drained":
            score += 2
        
        # Texture preference (wide range acceptable)
        if texture in ["loam", "silt_loam", "clay_loam", "silty_clay_loam"]:
            score += 3
        elif texture in ["sandy_loam", "sandy_clay_loam"]:
            score += 2
        else:
            score += 1
        
        # Convert score to rating
        if score >= 7:
            return "excellent"
        elif score >= 5:
            return "good"
        elif score >= 3:
            return "fair"
        else:
            return "poor"
    
    def _evaluate_wheat_suitability(self, texture: str, drainage: str, ph: float) -> str:
        """Evaluate wheat suitability for soil conditions."""
        score = 0
        
        # pH preference (6.0-7.5 optimal, tolerates higher pH)
        if 6.0 <= ph <= 7.5:
            score += 3
        elif 5.8 <= ph <= 8.0:
            score += 2
        elif 5.5 <= ph <= 8.5:
            score += 1
        
        # Drainage preference (well drained preferred)
        if drainage == "well_drained":
            score += 3
        elif drainage == "moderately_well_drained":
            score += 2
        elif drainage == "somewhat_poorly_drained":
            score += 1
        
        # Texture preference (silt loams are excellent)
        if texture in ["silt_loam", "silty_clay_loam"]:
            score += 3
        elif texture in ["loam", "clay_loam"]:
            score += 2
        else:
            score += 1
        
        # Convert score to rating
        if score >= 7:
            return "excellent"
        elif score >= 5:
            return "good"
        elif score >= 3:
            return "fair"
        else:
            return "poor"
    
    def _identify_soil_limitations(self, soil_chars: SoilCharacteristics) -> List[str]:
        """Identify potential soil limitations."""
        limitations = []
        
        ph_avg = (soil_chars.typical_ph_range["min"] + soil_chars.typical_ph_range["max"]) / 2
        
        if ph_avg < 5.5:
            limitations.append("Acidic soil - may limit nutrient availability")
        elif ph_avg > 8.0:
            limitations.append("Alkaline soil - may limit micronutrient availability")
        
        if "poorly" in soil_chars.drainage_class:
            limitations.append("Poor drainage - may limit root development and field access")
        
        if soil_chars.organic_matter_typical < 2.0:
            limitations.append("Low organic matter - may affect soil structure and nutrient retention")
        
        if "sand" in soil_chars.soil_texture:
            limitations.append("Sandy texture - may have low water and nutrient retention")
        elif soil_chars.soil_texture == "clay":
            limitations.append("Heavy clay - may have poor drainage and difficult tillage")
        
        if soil_chars.erosion_factor_k and soil_chars.erosion_factor_k > 0.4:
            limitations.append("High erosion potential - requires conservation practices")
        
        return limitations
    
    def _get_management_considerations(self, soil_chars: SoilCharacteristics) -> List[str]:
        """Get management considerations for soil type."""
        considerations = []
        
        if "sand" in soil_chars.soil_texture:
            considerations.append("Consider split nitrogen applications to reduce leaching")
            considerations.append("Monitor soil moisture closely - irrigation may be beneficial")
        
        if soil_chars.soil_texture == "clay":
            considerations.append("Avoid field operations when soil is wet to prevent compaction")
            considerations.append("Consider controlled traffic patterns")
        
        if soil_chars.organic_matter_typical < 3.0:
            considerations.append("Consider cover crops or organic amendments to build soil health")
        
        ph_avg = (soil_chars.typical_ph_range["min"] + soil_chars.typical_ph_range["max"]) / 2
        if ph_avg < 6.0:
            considerations.append("Consider lime application to improve pH and nutrient availability")
        
        if "poorly" in soil_chars.drainage_class:
            considerations.append("Consider drainage improvements or select appropriate crops")
        
        return considerations
    
    def _evaluate_irrigation_suitability(self, texture: str, drainage: str) -> str:
        """Evaluate irrigation suitability."""
        if "sand" in texture and "well" in drainage:
            return "excellent"
        elif texture in ["loam", "silt_loam"] and "well" in drainage:
            return "good"
        elif "poorly" in drainage:
            return "poor"
        else:
            return "fair"
    
    def _evaluate_erosion_risk(self, soil_chars: SoilCharacteristics) -> str:
        """Evaluate erosion risk."""
        if soil_chars.erosion_factor_k:
            if soil_chars.erosion_factor_k > 0.4:
                return "high"
            elif soil_chars.erosion_factor_k > 0.3:
                return "moderate"
            else:
                return "low"
        
        # Estimate based on texture and slope
        if "sand" in soil_chars.soil_texture or "silt" in soil_chars.soil_texture:
            if "5%" in soil_chars.slope_range or "10%" in soil_chars.slope_range:
                return "moderate"
            else:
                return "low"
        else:
            return "low"
    
    def _get_default_soil_characteristics(self, latitude: float, longitude: float) -> SoilCharacteristics:
        """Return default soil characteristics when all services fail."""
        return SoilCharacteristics(
            soil_series="Unknown",
            soil_texture="loam",
            drainage_class="moderately_well_drained",
            typical_ph_range={"min": 6.0, "max": 7.0},
            organic_matter_typical=3.0,
            slope_range="0-3%",
            parent_material="Unknown",
            hydrologic_group="B",
            available_water_capacity=0.15,
            permeability="moderate"
        )
    
    def _get_default_nutrient_ranges(self) -> SoilNutrientRanges:
        """Return default nutrient ranges when estimation fails."""
        return SoilNutrientRanges(
            phosphorus_ppm_range={"low": 15, "medium": 25, "high": 40},
            potassium_ppm_range={"low": 120, "medium": 180, "high": 250},
            nitrogen_typical=60.0,
            cec_range={"min": 12, "max": 18},
            base_saturation_range={"min": 70, "max": 85},
            micronutrient_status={
                "iron": "adequate",
                "manganese": "adequate", 
                "zinc": "adequate",
                "boron": "adequate"
            }
        )
    
    def _get_default_crop_suitability(self) -> SoilSuitability:
        """Return default crop suitability when evaluation fails."""
        return SoilSuitability(
            crop_suitability={
                "corn": "good",
                "soybean": "good",
                "wheat": "fair"
            },
            limitations=["Limited soil data available"],
            management_considerations=["Obtain soil test for specific recommendations"],
            irrigation_suitability="fair",
            erosion_risk="moderate"
        )
    
    async def close(self):
        """Close all soil service connections."""
        await self.usda_service.close()