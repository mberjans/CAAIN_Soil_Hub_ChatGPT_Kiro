"""
Mobile-optimized price alert orchestration.

This service adapts the core price optimization alert capabilities for
mobile devices by combining location awareness, personalized thresholds,
and concise alert packaging suitable for push and in-app delivery.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from ..models.price_models import (
    FertilizerType,
    FertilizerProduct,
    FertilizerPriceData,
    PriceSource
)
from ..models.price_adjustment_models import AdjustmentAlert
from ..models.price_optimization_alert_models import (
    MobilePriceAlertRequest,
    MobilePriceAlertResponse,
    MobilePriceAlert,
    AlertType,
    AlertPriority,
    AlertChannel,
    UserAlertPreferences
)
from .price_optimization_alert_service import PriceOptimizationAlertService
from .price_tracking_service import FertilizerPriceTrackingService


class MobilePriceAlertManager:
    """Coordinator for intelligent mobile price alerts."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alert_service = PriceOptimizationAlertService()
        self.price_tracker = FertilizerPriceTrackingService()
        self.region_mappings = self._build_region_mappings()
    
    async def generate_mobile_alerts(
        self,
        request: MobilePriceAlertRequest
    ) -> MobilePriceAlertResponse:
        """Generate mobile-optimized alerts."""
        resolved_region = self._resolve_region(request)
        fallback_used = False
        
        fertilizer_types = self._resolve_fertilizer_types(request)
        alert_types = self._resolve_alert_types(request)
        preferences = self._prepare_preferences(request.user_preferences)
        
        mobile_alerts: List[MobilePriceAlert] = []
        
        for fertilizer_type in fertilizer_types:
            product = self._map_type_to_product(fertilizer_type)
            if not product:
                continue
            
            current_price = await self._fetch_current_price(product, resolved_region)
            if not current_price:
                current_price = self._build_fallback_price(product, fertilizer_type, resolved_region)
                fallback_used = True
            
            historical_data = await self._build_historical_data(
                current_price,
                request.history_days,
                resolved_region
            )
            if not historical_data:
                fallback_used = True
                historical_data = self._build_synthetic_history(current_price, request.history_days)
            
            for alert_type in alert_types:
                alert_model = await self.alert_service.create_intelligent_alert(
                    user_id=request.user_id,
                    fertilizer_type=fertilizer_type,
                    alert_type=alert_type,
                    current_price=current_price,
                    historical_data=historical_data,
                    user_preferences=preferences
                )
                
                if alert_model:
                    price_change_percent = self._calculate_price_change_percent(historical_data, current_price)
                    mobile_alert = self._convert_to_mobile_alert(
                        request=request,
                        fertilizer_type=fertilizer_type,
                        current_price=current_price,
                        alert_model=alert_model,
                        alert_type=alert_type,
                        resolved_region=resolved_region,
                        price_change_percent=price_change_percent
                    )
                    mobile_alerts.append(mobile_alert)
        
        limited_alerts = self._limit_alerts(mobile_alerts, request.max_alerts)
        insights = self._build_insights(limited_alerts)
        recommendations = self._build_recommendations(limited_alerts, request)
        
        response = MobilePriceAlertResponse(
            user_id=request.user_id,
            region=resolved_region,
            alerts=limited_alerts,
            fallback_used=fallback_used,
            insights=insights,
            recommendations=recommendations
        )
        
        return response
    
    def _resolve_region(self, request: MobilePriceAlertRequest) -> str:
        """Determine best-fit region from location data."""
        if request.region:
            return request.region
        
        if request.latitude is None or request.longitude is None:
            return "US"
        
        latitude = request.latitude
        longitude = request.longitude
        resolved_region = "US"
        
        for mapping in self.region_mappings:
            if latitude >= mapping["lat_min"] and latitude <= mapping["lat_max"]:
                if longitude >= mapping["lon_min"] and longitude <= mapping["lon_max"]:
                    resolved_region = mapping["name"]
                    break
        
        return resolved_region
    
    def _resolve_fertilizer_types(self, request: MobilePriceAlertRequest) -> List[FertilizerType]:
        """Resolve fertilizer types to monitor."""
        resolved_types: List[FertilizerType] = []
        if request.fertilizer_types:
            for fertilizer_type in request.fertilizer_types:
                resolved_types.append(fertilizer_type)
        else:
            resolved_types.append(FertilizerType.NITROGEN)
            resolved_types.append(FertilizerType.PHOSPHORUS)
            resolved_types.append(FertilizerType.POTASSIUM)
        
        return resolved_types
    
    def _resolve_alert_types(self, request: MobilePriceAlertRequest) -> List[AlertType]:
        """Resolve alert types to evaluate."""
        resolved_types: List[AlertType] = []
        if request.alert_types:
            for alert_type in request.alert_types:
                resolved_types.append(alert_type)
        else:
            resolved_types.append(AlertType.PRICE_THRESHOLD)
            resolved_types.append(AlertType.OPPORTUNITY)
            resolved_types.append(AlertType.TIMING)
            resolved_types.append(AlertType.RISK)
        
        return resolved_types
    
    def _prepare_preferences(
        self,
        preferences: Optional[UserAlertPreferences]
    ) -> Optional[Dict[str, Any]]:
        """Prepare user preferences for the core alert service."""
        if not preferences:
            return None
        
        try:
            return preferences.model_dump()
        except Exception:
            return None
    
    async def _fetch_current_price(
        self,
        product: FertilizerProduct,
        region: str
    ) -> Optional[FertilizerPriceData]:
        """Fetch current price with graceful error handling."""
        try:
            return await self.price_tracker.get_current_price(
                product=product,
                region=region,
                max_age_hours=24
            )
        except Exception as error:
            self.logger.warning("Price lookup failed for %s in %s: %s", product.value, region, error)
            return None
    
    async def _build_historical_data(
        self,
        current_price: FertilizerPriceData,
        history_days: int,
        region: str
    ) -> List[FertilizerPriceData]:
        """Attempt to build historical dataset from stored prices."""
        # Placeholder for future database integration - currently returns empty list
        _ = region  # Suppress unused parameter warning
        _ = history_days
        _ = current_price
        historical_records: List[FertilizerPriceData] = []
        return historical_records
    
    def _build_synthetic_history(
        self,
        current_price: FertilizerPriceData,
        history_days: int
    ) -> List[FertilizerPriceData]:
        """Generate synthetic history when stored data is unavailable."""
        synthetic_history: List[FertilizerPriceData] = []
        base_price = current_price.price_per_unit
        base_date = current_price.price_date
        if not base_date:
            base_date = datetime.utcnow().date()
        
        index = 0
        while index < history_days:
            day_offset = history_days - index
            adjustment = (day_offset - (history_days / 2.0)) * 0.6
            price_value = base_price - adjustment
            if price_value <= 0:
                price_value = base_price
            
            history_price = FertilizerPriceData(
                product_id=f"{current_price.product_id}_hist_{index}",
                product_name=current_price.product_name,
                fertilizer_type=current_price.fertilizer_type,
                specific_product=current_price.specific_product,
                price_per_unit=price_value,
                unit=current_price.unit,
                currency=current_price.currency,
                region=current_price.region,
                state=current_price.state,
                source=PriceSource.FALLBACK,
                price_date=base_date - timedelta(days=day_offset),
                is_spot_price=True,
                is_contract_price=False,
                market_conditions=current_price.market_conditions,
                seasonal_factors=current_price.seasonal_factors,
                confidence=current_price.confidence,
                volatility=current_price.volatility,
                created_at=datetime.utcnow() - timedelta(days=day_offset),
                updated_at=datetime.utcnow() - timedelta(days=day_offset)
            )
            synthetic_history.append(history_price)
            index += 1
        
        return synthetic_history
    
    def _map_type_to_product(self, fertilizer_type: FertilizerType) -> Optional[FertilizerProduct]:
        """Map fertilizer type to representative product for pricing."""
        if fertilizer_type == FertilizerType.NITROGEN:
            return FertilizerProduct.UREA
        if fertilizer_type == FertilizerType.PHOSPHORUS:
            return FertilizerProduct.DAP
        if fertilizer_type == FertilizerType.POTASSIUM:
            return FertilizerProduct.MURIATE_OF_POTASH
        if fertilizer_type == FertilizerType.BLEND:
            return FertilizerProduct.NPK_BLEND
        if fertilizer_type == FertilizerType.ORGANIC:
            return FertilizerProduct.CUSTOM_BLEND
        if fertilizer_type == FertilizerType.MICRONUTRIENT:
            return FertilizerProduct.CUSTOM_BLEND
        return None
    
    def _convert_to_mobile_alert(
        self,
        request: MobilePriceAlertRequest,
        fertilizer_type: FertilizerType,
        current_price: FertilizerPriceData,
        alert_model: AdjustmentAlert,
        alert_type: AlertType,
        resolved_region: str,
        price_change_percent: Optional[float]
    ) -> MobilePriceAlert:
        """Convert core alert model into mobile format."""
        confidence_score = 0.0
        recommended_actions: List[str] = []
        details: Dict[str, Any] = {}
        
        if alert_model.details:
            details = alert_model.details
            confidence_candidate = alert_model.details.get("analysis_confidence")
            if isinstance(confidence_candidate, (float, int)):
                confidence_score = float(confidence_candidate)
            
            actions_candidate = alert_model.details.get("recommended_actions")
            if isinstance(actions_candidate, list):
                for action in actions_candidate:
                    if isinstance(action, str):
                        recommended_actions.append(action)
        
        if not recommended_actions:
            recommended_actions.append("Review fertilizer purchase schedule and confirm supplier pricing.")
        
        if request.include_price_details:
            details["current_price"] = current_price.price_per_unit
            details["price_unit"] = current_price.unit
            if price_change_percent is not None:
                details["price_change_percent"] = price_change_percent
        
        mobile_alert = MobilePriceAlert(
            alert_id=alert_model.alert_id,
            user_id=request.user_id,
            fertilizer_type=fertilizer_type,
            alert_type=alert_type,
            priority=AlertPriority(alert_model.priority),
            title=alert_model.message.split(":")[0] if ":" in alert_model.message else alert_model.message,
            summary=alert_model.message,
            details=details,
            price_per_unit=current_price.price_per_unit,
            price_unit=current_price.unit,
            price_change_percent=price_change_percent,
            region=resolved_region,
            confidence_score=confidence_score,
            recommended_actions=recommended_actions,
            notification_channel=request.delivery_channel,
            created_at=alert_model.timestamp,
            action_deadline=alert_model.action_deadline,
            requires_action=alert_model.requires_action
        )
        
        return mobile_alert
    
    def _calculate_price_change_percent(
        self,
        historical_data: List[FertilizerPriceData],
        current_price: FertilizerPriceData
    ) -> Optional[float]:
        """Calculate price change from historical series."""
        if not historical_data:
            return None
        
        first_record = historical_data[0]
        last_record = historical_data[-1]
        
        starting_price = first_record.price_per_unit
        ending_price = last_record.price_per_unit
        if current_price.price_per_unit:
            ending_price = current_price.price_per_unit
        
        if starting_price <= 0:
            return None
        
        change = ((ending_price - starting_price) / starting_price) * 100.0
        return change
    
    def _limit_alerts(
        self,
        alerts: List[MobilePriceAlert],
        max_alerts: int
    ) -> List[MobilePriceAlert]:
        """Limit alerts to requested maximum."""
        limited: List[MobilePriceAlert] = []
        for alert in alerts:
            if len(limited) >= max_alerts:
                break
            limited.append(alert)
        return limited
    
    def _build_insights(self, alerts: List[MobilePriceAlert]) -> Dict[str, Any]:
        """Build aggregated insight summary."""
        insights: Dict[str, Any] = {
            "total_alerts": len(alerts),
            "priority_counts": {},
            "alert_types": {}
        }
        
        for alert in alerts:
            priority_key = alert.priority.value
            if priority_key not in insights["priority_counts"]:
                insights["priority_counts"][priority_key] = 0
            insights["priority_counts"][priority_key] += 1
            
            alert_type_key = alert.alert_type.value
            if alert_type_key not in insights["alert_types"]:
                insights["alert_types"][alert_type_key] = 0
            insights["alert_types"][alert_type_key] += 1
        
        return insights
    
    def _build_recommendations(
        self,
        alerts: List[MobilePriceAlert],
        request: MobilePriceAlertRequest
    ) -> List[str]:
        """Aggregate high-level recommendations for display."""
        if not request.include_recommendations:
            return []
        
        recommendations: List[str] = []
        for alert in alerts:
            if alert.summary and alert.summary not in recommendations:
                recommendations.append(alert.summary)
        
        return recommendations
    
    def _build_fallback_price(
        self,
        product: FertilizerProduct,
        fertilizer_type: FertilizerType,
        region: str
    ) -> FertilizerPriceData:
        """Create fallback price data when providers are unavailable."""
        fallback_prices = {
            FertilizerProduct.UREA: 480.0,
            FertilizerProduct.DAP: 720.0,
            FertilizerProduct.MURIATE_OF_POTASH: 390.0,
            FertilizerProduct.NPK_BLEND: 540.0,
            FertilizerProduct.CUSTOM_BLEND: 520.0
        }
        
        base_price = fallback_prices.get(product, 500.0)
        today = datetime.utcnow().date()
        
        fallback_price = FertilizerPriceData(
            product_id=f"fallback_{product.value}",
            product_name=product.value.replace("_", " ").title(),
            fertilizer_type=fertilizer_type,
            specific_product=product,
            price_per_unit=base_price,
            unit="ton",
            currency="USD",
            region=region,
            state=None,
            source=PriceSource.FALLBACK,
            price_date=today,
            is_spot_price=True,
            is_contract_price=False,
            market_conditions={"source": "fallback"},
            seasonal_factors=None,
            confidence=0.6,
            volatility=12.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return fallback_price
    
    def _build_region_mappings(self) -> List[Dict[str, Any]]:
        """Create coarse region mapping for latitude/longitude."""
        mappings: List[Dict[str, Any]] = []
        
        mappings.append({
            "name": "Corn Belt",
            "lat_min": 36.0,
            "lat_max": 47.0,
            "lon_min": -104.0,
            "lon_max": -82.0
        })
        
        mappings.append({
            "name": "Great Plains",
            "lat_min": 31.0,
            "lat_max": 45.0,
            "lon_min": -109.0,
            "lon_max": -95.0
        })
        
        mappings.append({
            "name": "Delta",
            "lat_min": 30.0,
            "lat_max": 37.0,
            "lon_min": -94.0,
            "lon_max": -88.0
        })
        
        mappings.append({
            "name": "Lake States",
            "lat_min": 41.0,
            "lat_max": 49.0,
            "lon_min": -93.0,
            "lon_max": -82.0
        })
        
        mappings.append({
            "name": "US",
            "lat_min": -90.0,
            "lat_max": 90.0,
            "lon_min": -180.0,
            "lon_max": 180.0
        })
        
        return mappings
