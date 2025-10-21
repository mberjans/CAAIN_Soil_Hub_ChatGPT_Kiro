# Parallel Job 2: Fertilizer Strategy Optimization

**TICKET-006: Market Price Integration System**  
**Estimated Timeline**: 3-4 weeks  
**Priority**: High  
**Can Start**: Immediately (No blocking dependencies)

## Executive Summary

This job implements real-time fertilizer price tracking, economic optimization algorithms, and cost-effective fertilizer strategy recommendations. This work is **completely independent** of other parallel jobs and can proceed without blocking.

## Related Tickets from Checklist

- **TICKET-006_fertilizer-strategy-optimization-1.1**: Implement real-time fertilizer price tracking
- **TICKET-006_fertilizer-strategy-optimization-1.2**: Create price trend analysis system
- **TICKET-006_fertilizer-strategy-optimization-1.3**: Develop economic optimization engine
- **TICKET-006_fertilizer-strategy-optimization-2.1**: Implement ROI calculation algorithms
- **TICKET-006_fertilizer-strategy-optimization-2.2**: Create cost-benefit analysis tools
- **TICKET-006_fertilizer-strategy-optimization-3.1**: Build fertilizer recommendation optimizer

## Technical Stack

```yaml
Languages: Python 3.11+
Framework: FastAPI
Database: PostgreSQL with TimescaleDB extension
ORM: SQLAlchemy 2.0+
Validation: Pydantic v2
Testing: pytest, pytest-asyncio
External APIs: USDA NASS, CME Group (mock for development)
Optimization: scipy, numpy
Scheduling: APScheduler
```

## Service Architecture

**Service Location**: `services/fertilizer-optimization/`  
**Port**: 8008 (new service)  
**Reference Pattern**: Follow `services/recommendation-engine/` structure

```
services/fertilizer-optimization/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── price_models.py
│   │   ├── optimization_models.py
│   │   └── recommendation_models.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── price_tracker.py
│   │   ├── trend_analyzer.py
│   │   ├── economic_optimizer.py
│   │   └── recommendation_service.py
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── usda_nass_provider.py
│   │   ├── cme_provider.py
│   │   └── mock_provider.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── price_routes.py
│   │   └── optimization_routes.py
│   └── schemas/
│       ├── __init__.py
│       ├── price_schemas.py
│       └── optimization_schemas.py
├── tests/
│   ├── __init__.py
│   ├── test_price_tracker.py
│   ├── test_economic_optimizer.py
│   └── test_api_endpoints.py
├── requirements.txt
└── README.md
```

## Week 1: Foundation & Price Tracking (Days 1-5)

### Day 1: Service Structure Setup

**Step 1: Create Service Directory**
```bash
# Execute from repository root
mkdir -p services/fertilizer-optimization/src/{models,services,providers,api,schemas}
mkdir -p services/fertilizer-optimization/tests
touch services/fertilizer-optimization/src/__init__.py
touch services/fertilizer-optimization/src/main.py
```

**Step 2: Create requirements.txt**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
psycopg2-binary==2.9.9
alembic==1.12.1
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1
numpy==1.26.2
scipy==1.11.4
pandas==2.1.3
APScheduler==3.10.4
```

**Step 3: Install Dependencies**
```bash
cd services/fertilizer-optimization
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Day 2-3: Database Schema for Price Tracking

**File**: `services/fertilizer-optimization/src/models/price_models.py`

```python
from sqlalchemy import Column, Integer, String, DECIMAL, Date, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date

Base = declarative_base()

class FertilizerType(Base):
    """Fertilizer type reference table"""
    __tablename__ = 'fertilizer_types'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    chemical_formula = Column(String(50))
    nutrient_content = Column(String(20))  # e.g., "46-0-0" for urea
    category = Column(String(50))  # nitrogen, phosphorus, potassium, blend
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    prices = relationship("FertilizerPrice", back_populates="fertilizer_type")

class FertilizerPrice(Base):
    """Time series fertilizer price data"""
    __tablename__ = 'fertilizer_prices'
    
    id = Column(Integer, primary_key=True)
    fertilizer_type_id = Column(Integer, ForeignKey('fertilizer_types.id'), nullable=False)
    price_per_unit = Column(DECIMAL(10, 2), nullable=False)
    unit = Column(String(20), nullable=False)  # ton, cwt, lb
    region = Column(String(100))
    source = Column(String(50), nullable=False)
    price_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    fertilizer_type = relationship("FertilizerType", back_populates="prices")
    
    # Composite index for time series queries
    __table_args__ = (
        Index('idx_fertilizer_prices_type_date', 'fertilizer_type_id', 'price_date'),
        Index('idx_fertilizer_prices_region', 'region'),
        Index('idx_fertilizer_prices_date', 'price_date'),
    )

class PriceTrend(Base):
    """Calculated price trends and statistics"""
    __tablename__ = 'price_trends'
    
    id = Column(Integer, primary_key=True)
    fertilizer_type_id = Column(Integer, ForeignKey('fertilizer_types.id'), nullable=False)
    region = Column(String(100))
    period_days = Column(Integer, nullable=False)  # 7, 30, 90, 365
    average_price = Column(DECIMAL(10, 2))
    min_price = Column(DECIMAL(10, 2))
    max_price = Column(DECIMAL(10, 2))
    volatility = Column(DECIMAL(5, 4))  # Standard deviation
    trend_direction = Column(String(20))  # increasing, decreasing, stable
    price_change_percent = Column(DECIMAL(6, 2))
    calculation_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_trends_type_period', 'fertilizer_type_id', 'period_days'),
    )
```

**Database Migration SQL**:
```sql
-- Create fertilizer_types table
CREATE TABLE IF NOT EXISTS fertilizer_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    chemical_formula VARCHAR(50),
    nutrient_content VARCHAR(20),
    category VARCHAR(50),
    description VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create fertilizer_prices table with TimescaleDB hypertable
CREATE TABLE IF NOT EXISTS fertilizer_prices (
    id SERIAL PRIMARY KEY,
    fertilizer_type_id INTEGER REFERENCES fertilizer_types(id) ON DELETE CASCADE,
    price_per_unit DECIMAL(10,2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    region VARCHAR(100),
    source VARCHAR(50) NOT NULL,
    price_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Convert to TimescaleDB hypertable for time series optimization
SELECT create_hypertable('fertilizer_prices', 'price_date', if_not_exists => TRUE);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_fertilizer_prices_type_date ON fertilizer_prices(fertilizer_type_id, price_date);
CREATE INDEX IF NOT EXISTS idx_fertilizer_prices_region ON fertilizer_prices(region);
CREATE INDEX IF NOT EXISTS idx_fertilizer_prices_date ON fertilizer_prices(price_date);

-- Create price_trends table
CREATE TABLE IF NOT EXISTS price_trends (
    id SERIAL PRIMARY KEY,
    fertilizer_type_id INTEGER REFERENCES fertilizer_types(id) ON DELETE CASCADE,
    region VARCHAR(100),
    period_days INTEGER NOT NULL,
    average_price DECIMAL(10,2),
    min_price DECIMAL(10,2),
    max_price DECIMAL(10,2),
    volatility DECIMAL(5,4),
    trend_direction VARCHAR(20),
    price_change_percent DECIMAL(6,2),
    calculation_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trends_type_period ON price_trends(fertilizer_type_id, period_days);

-- Insert sample fertilizer types
INSERT INTO fertilizer_types (name, chemical_formula, nutrient_content, category, description) VALUES
('Urea', 'CO(NH2)2', '46-0-0', 'nitrogen', 'High nitrogen fertilizer'),
('DAP', '(NH4)2HPO4', '18-46-0', 'phosphorus', 'Diammonium phosphate'),
('Potash', 'KCl', '0-0-60', 'potassium', 'Muriate of potash'),
('10-10-10', 'Blend', '10-10-10', 'blend', 'Balanced NPK fertilizer'),
('Anhydrous Ammonia', 'NH3', '82-0-0', 'nitrogen', 'Highest nitrogen content')
ON CONFLICT (name) DO NOTHING;
```

**Validation Command**:
```bash
psql -U postgres -d caain_soil_hub -f migrations/002_fertilizer_prices_schema.sql
psql -U postgres -d caain_soil_hub -c "SELECT * FROM fertilizer_types;"
```

### Day 3-4: Price Tracking Service

**File**: `services/fertilizer-optimization/src/services/price_tracker.py`

```python
import asyncio
import logging
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from ..models.price_models import FertilizerType, FertilizerPrice
from ..providers.usda_nass_provider import USDANASSProvider
from ..providers.mock_provider import MockPriceProvider

logger = logging.getLogger(__name__)

class FertilizerPriceTracker:
    """Real-time fertilizer price tracking (TICKET-006_fertilizer-strategy-optimization-1.1)"""
    
    def __init__(self, db: Session):
        self.db = db
        self.providers = [
            MockPriceProvider(),  # Use mock for development
            # USDANASSProvider(),  # Enable for production
        ]
    
    async def update_prices(self) -> Dict[str, Any]:
        """
        Daily price update from all sources
        
        Returns summary of updates
        """
        logger.info("Starting daily price update")
        start_time = datetime.utcnow()
        
        fertilizer_types = self.db.query(FertilizerType).all()
        
        updates = {
            "total_updates": 0,
            "successful_updates": 0,
            "failed_updates": 0,
            "sources_used": [],
            "errors": []
        }
        
        for fertilizer_type in fertilizer_types:
            for provider in self.providers:
                try:
                    price_data = await provider.get_current_price(fertilizer_type.name)
                    
                    if price_data:
                        # Store price in database
                        db_price = FertilizerPrice(
                            fertilizer_type_id=fertilizer_type.id,
                            price_per_unit=price_data['price'],
                            unit=price_data['unit'],
                            region=price_data.get('region', 'US'),
                            source=provider.name,
                            price_date=date.today()
                        )
                        self.db.add(db_price)
                        updates["successful_updates"] += 1
                        
                        if provider.name not in updates["sources_used"]:
                            updates["sources_used"].append(provider.name)
                    
                except Exception as e:
                    logger.error(f"Error fetching price for {fertilizer_type.name} from {provider.name}: {e}")
                    updates["failed_updates"] += 1
                    updates["errors"].append(str(e))
        
        self.db.commit()
        updates["total_updates"] = updates["successful_updates"] + updates["failed_updates"]
        updates["duration_seconds"] = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(f"Price update completed: {updates}")
        return updates
    
    async def get_current_prices(
        self,
        region: Optional[str] = None,
        fertilizer_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get current prices for specified fertilizers in region"""
        
        query = self.db.query(FertilizerPrice, FertilizerType).join(
            FertilizerType, FertilizerPrice.fertilizer_type_id == FertilizerType.id
        )
        
        # Filter by region
        if region:
            query = query.filter(FertilizerPrice.region == region)
        
        # Filter by fertilizer types
        if fertilizer_types:
            query = query.filter(FertilizerType.name.in_(fertilizer_types))
        
        # Get most recent prices (within last 7 days)
        cutoff_date = date.today() - timedelta(days=7)
        query = query.filter(FertilizerPrice.price_date >= cutoff_date)
        
        # Order by date descending
        query = query.order_by(FertilizerPrice.price_date.desc())
        
        results = query.all()
        
        # Group by fertilizer type and get most recent
        prices_by_type = {}
        for price, fert_type in results:
            if fert_type.name not in prices_by_type:
                prices_by_type[fert_type.name] = {
                    "fertilizer_type": fert_type.name,
                    "nutrient_content": fert_type.nutrient_content,
                    "price_per_unit": float(price.price_per_unit),
                    "unit": price.unit,
                    "region": price.region,
                    "price_date": price.price_date.isoformat(),
                    "source": price.source
                }
        
        return list(prices_by_type.values())
```

**File**: `services/fertilizer-optimization/src/providers/mock_provider.py`

```python
import random
from typing import Dict, Any, Optional

class MockPriceProvider:
    """Mock price provider for development and testing"""
    
    def __init__(self):
        self.name = "MockProvider"
        self.base_prices = {
            "Urea": 450.0,  # $/ton
            "DAP": 650.0,
            "Potash": 550.0,
            "10-10-10": 500.0,
            "Anhydrous Ammonia": 700.0
        }
    
    async def get_current_price(self, fertilizer_name: str) -> Optional[Dict[str, Any]]:
        """Get mock price with random variation"""
        
        if fertilizer_name not in self.base_prices:
            return None
        
        base_price = self.base_prices[fertilizer_name]
        # Add ±10% random variation
        variation = random.uniform(-0.1, 0.1)
        current_price = base_price * (1 + variation)
        
        return {
            "price": round(current_price, 2),
            "unit": "ton",
            "region": "US",
            "currency": "USD"
        }
```

**Validation Command**:
```bash
cd services/fertilizer-optimization
python -c "from src.services.price_tracker import FertilizerPriceTracker; print('PriceTracker OK')"
```

## Week 2: Economic Optimization Engine (Days 6-10)

### Day 6-8: Optimization Models and Algorithms

**File**: `services/fertilizer-optimization/src/services/economic_optimizer.py`

```python
import numpy as np
from scipy.optimize import minimize, LinearConstraint
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class OptimizationConstraints:
    """Constraints for fertilizer optimization"""
    max_budget: Optional[float] = None
    min_nitrogen_lbs: Optional[float] = None
    min_phosphorus_lbs: Optional[float] = None
    min_potassium_lbs: Optional[float] = None
    max_application_rate: Optional[float] = None
    environmental_limits: Optional[Dict[str, float]] = None

@dataclass
class FertilizerOption:
    """Fertilizer option with pricing and nutrients"""
    name: str
    price_per_unit: float
    unit: str
    nitrogen_percent: float
    phosphorus_percent: float
    potassium_percent: float
    application_efficiency: float = 0.85

class EconomicOptimizer:
    """Multi-objective fertilizer optimization (TICKET-006_fertilizer-strategy-optimization-1.3)"""

    def optimize_fertilizer_strategy(
        self,
        field_acres: float,
        nutrient_requirements: Dict[str, float],  # N, P, K in lbs/acre
        available_fertilizers: List[FertilizerOption],
        constraints: OptimizationConstraints,
        yield_goal_bu_acre: float
    ) -> Dict[str, Any]:
        """
        Multi-objective optimization:
        - Minimize cost
        - Meet nutrient requirements
        - Maximize yield potential
        - Minimize environmental impact
        """

        n_fertilizers = len(available_fertilizers)

        # Objective function: minimize cost
        def objective(x):
            total_cost = sum(
                x[i] * available_fertilizers[i].price_per_unit * field_acres
                for i in range(n_fertilizers)
            )
            return total_cost

        # Constraint: meet nitrogen requirement
        def nitrogen_constraint(x):
            total_n = sum(
                x[i] * available_fertilizers[i].nitrogen_percent / 100 * available_fertilizers[i].application_efficiency
                for i in range(n_fertilizers)
            )
            return total_n - nutrient_requirements.get('N', 0)

        # Constraint: meet phosphorus requirement
        def phosphorus_constraint(x):
            total_p = sum(
                x[i] * available_fertilizers[i].phosphorus_percent / 100 * available_fertilizers[i].application_efficiency
                for i in range(n_fertilizers)
            )
            return total_p - nutrient_requirements.get('P', 0)

        # Constraint: meet potassium requirement
        def potassium_constraint(x):
            total_k = sum(
                x[i] * available_fertilizers[i].potassium_percent / 100 * available_fertilizers[i].application_efficiency
                for i in range(n_fertilizers)
            )
            return total_k - nutrient_requirements.get('K', 0)

        # Initial guess: equal distribution
        x0 = np.ones(n_fertilizers) * 100

        # Bounds: non-negative application rates
        bounds = [(0, 500) for _ in range(n_fertilizers)]

        # Constraints
        constraints_list = [
            {'type': 'ineq', 'fun': nitrogen_constraint},
            {'type': 'ineq', 'fun': phosphorus_constraint},
            {'type': 'ineq', 'fun': potassium_constraint}
        ]

        # Budget constraint
        if constraints.max_budget:
            def budget_constraint(x):
                total_cost = sum(
                    x[i] * available_fertilizers[i].price_per_unit * field_acres
                    for i in range(n_fertilizers)
                )
                return constraints.max_budget - total_cost
            constraints_list.append({'type': 'ineq', 'fun': budget_constraint})

        # Solve optimization
        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints_list,
            options={'maxiter': 1000}
        )

        if not result.success:
            return {
                "success": False,
                "message": "Optimization failed to converge",
                "reason": result.message
            }

        # Build recommendation
        recommendations = []
        total_cost = 0

        for i, amount in enumerate(result.x):
            if amount > 0.1:  # Only include significant amounts
                fert = available_fertilizers[i]
                cost = amount * fert.price_per_unit * field_acres
                total_cost += cost

                recommendations.append({
                    "fertilizer": fert.name,
                    "application_rate_per_acre": round(amount, 2),
                    "total_amount": round(amount * field_acres, 2),
                    "unit": fert.unit,
                    "cost_per_acre": round(cost / field_acres, 2),
                    "total_cost": round(cost, 2),
                    "nutrients_provided": {
                        "N": round(amount * fert.nitrogen_percent / 100 * fert.application_efficiency, 2),
                        "P": round(amount * fert.phosphorus_percent / 100 * fert.application_efficiency, 2),
                        "K": round(amount * fert.potassium_percent / 100 * fert.application_efficiency, 2)
                    }
                })

        return {
            "success": True,
            "recommendations": recommendations,
            "total_cost": round(total_cost, 2),
            "cost_per_acre": round(total_cost / field_acres, 2),
            "estimated_roi": self._calculate_roi(total_cost, field_acres, yield_goal_bu_acre),
            "environmental_impact": self._assess_environmental_impact(recommendations, field_acres)
        }

    def _calculate_roi(self, total_cost: float, acres: float, yield_goal: float) -> Dict[str, float]:
        """Calculate ROI based on yield goal and commodity prices"""
        # Assume corn at $5/bu
        commodity_price = 5.0
        expected_revenue = yield_goal * acres * commodity_price

        return {
            "total_investment": total_cost,
            "expected_revenue": expected_revenue,
            "net_profit": expected_revenue - total_cost,
            "roi_percent": ((expected_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0,
            "break_even_yield_bu_acre": (total_cost / acres / commodity_price) if acres > 0 else 0
        }

    def _assess_environmental_impact(self, recommendations: List[Dict], acres: float) -> Dict[str, Any]:
        """Assess environmental impact of fertilizer strategy"""
        total_n = sum(r["nutrients_provided"]["N"] for r in recommendations)

        # Simplified runoff risk assessment
        runoff_risk = "low"
        if total_n > 180:
            runoff_risk = "high"
        elif total_n > 150:
            runoff_risk = "moderate"

        return {
            "total_nitrogen_lbs_acre": round(total_n, 2),
            "runoff_risk": runoff_risk,
            "recommendations": [
                "Consider split applications to reduce runoff risk" if runoff_risk != "low" else "Application rate is environmentally sound",
                "Use nitrification inhibitors for high nitrogen rates" if total_n > 180 else None
            ]
        }
```

## Week 3: API Implementation & Testing (Days 11-15)

### Day 11-12: API Endpoints

**File**: `services/fertilizer-optimization/src/api/price_routes.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ..services.price_tracker import FertilizerPriceTracker

router = APIRouter(prefix="/api/v1/prices", tags=["fertilizer-prices"])

def get_db():
    # TODO: Implement database session dependency
    pass

@router.get("/fertilizer-current")
async def get_current_fertilizer_prices(
    region: Optional[str] = Query(None, description="Region filter"),
    fertilizer_types: Optional[List[str]] = Query(None, description="Fertilizer type filter"),
    db: Session = Depends(get_db)
):
    """
    Get current fertilizer prices

    Returns most recent prices from last 7 days
    """
    try:
        tracker = FertilizerPriceTracker(db)
        prices = await tracker.get_current_prices(region, fertilizer_types)
        return {"prices": prices, "count": len(prices)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-prices")
async def trigger_price_update(db: Session = Depends(get_db)):
    """
    Manually trigger price update (admin endpoint)
    """
    try:
        tracker = FertilizerPriceTracker(db)
        result = await tracker.update_prices()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**File**: `services/fertilizer-optimization/src/api/optimization_routes.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from ..services.economic_optimizer import EconomicOptimizer, FertilizerOption, OptimizationConstraints

router = APIRouter(prefix="/api/v1/optimization", tags=["fertilizer-optimization"])

class OptimizationRequest(BaseModel):
    field_acres: float = Field(..., gt=0, description="Field size in acres")
    nutrient_requirements: Dict[str, float] = Field(..., description="N, P, K requirements in lbs/acre")
    yield_goal_bu_acre: float = Field(..., gt=0, description="Target yield in bu/acre")
    max_budget: Optional[float] = Field(None, description="Maximum budget")
    available_fertilizers: List[Dict[str, Any]]

@router.post("/optimize-strategy")
async def optimize_fertilizer_strategy(request: OptimizationRequest):
    """
    Optimize fertilizer strategy for cost-effectiveness

    Multi-objective optimization considering:
    - Cost minimization
    - Nutrient requirement satisfaction
    - Yield goal achievement
    - Environmental impact
    """
    try:
        # Convert request to FertilizerOption objects
        fertilizer_options = [
            FertilizerOption(
                name=f["name"],
                price_per_unit=f["price_per_unit"],
                unit=f["unit"],
                nitrogen_percent=f["nitrogen_percent"],
                phosphorus_percent=f["phosphorus_percent"],
                potassium_percent=f["potassium_percent"]
            )
            for f in request.available_fertilizers
        ]

        constraints = OptimizationConstraints(max_budget=request.max_budget)

        optimizer = EconomicOptimizer()
        result = optimizer.optimize_fertilizer_strategy(
            field_acres=request.field_acres,
            nutrient_requirements=request.nutrient_requirements,
            available_fertilizers=fertilizer_options,
            constraints=constraints,
            yield_goal_bu_acre=request.yield_goal_bu_acre
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Week 4: Testing & Documentation (Days 16-20)

### Day 16-17: Unit Tests

**File**: `services/fertilizer-optimization/tests/test_economic_optimizer.py`

```python
import pytest
from src.services.economic_optimizer import EconomicOptimizer, FertilizerOption, OptimizationConstraints

def test_basic_optimization():
    """Test basic fertilizer optimization"""
    optimizer = EconomicOptimizer()

    fertilizers = [
        FertilizerOption("Urea", 450.0, "ton", 46, 0, 0),
        FertilizerOption("DAP", 650.0, "ton", 18, 46, 0),
        FertilizerOption("Potash", 550.0, "ton", 0, 0, 60)
    ]

    result = optimizer.optimize_fertilizer_strategy(
        field_acres=100,
        nutrient_requirements={"N": 150, "P": 60, "K": 40},
        available_fertilizers=fertilizers,
        constraints=OptimizationConstraints(),
        yield_goal_bu_acre=180
    )

    assert result["success"] is True
    assert "recommendations" in result
    assert result["total_cost"] > 0

def test_budget_constraint():
    """Test optimization with budget constraint"""
    optimizer = EconomicOptimizer()

    fertilizers = [
        FertilizerOption("Urea", 450.0, "ton", 46, 0, 0),
        FertilizerOption("DAP", 650.0, "ton", 18, 46, 0)
    ]

    result = optimizer.optimize_fertilizer_strategy(
        field_acres=100,
        nutrient_requirements={"N": 150, "P": 60, "K": 0},
        available_fertilizers=fertilizers,
        constraints=OptimizationConstraints(max_budget=50000),
        yield_goal_bu_acre=180
    )

    assert result["success"] is True
    assert result["total_cost"] <= 50000
```

## Definition of Done

### Functional Requirements
- [ ] Price tracking service fetches and stores prices
- [ ] Economic optimizer produces valid recommendations
- [ ] ROI calculations are accurate
- [ ] API endpoints return correct responses
- [ ] Scheduled price updates working

### Testing Requirements
- [ ] Unit test coverage >80%
- [ ] Optimization algorithm validated
- [ ] Price tracking tested with mock data
- [ ] Agricultural validation: Test with real fertilizer prices

### Documentation
- [ ] API documentation complete
- [ ] Optimization algorithm documented
- [ ] Setup instructions in README

### Integration Points
- [ ] Mock soil test data for nutrient requirements
- [ ] Document API contracts for integration

## Agricultural Expert Review Checkpoints

**Flag for Human Review**:
1. Nutrient requirement calculations
2. ROI assumptions and commodity prices
3. Environmental impact thresholds
4. Application rate recommendations

## Common Pitfalls

1. **Optimization Convergence**: May fail with infeasible constraints
2. **Price Data Staleness**: Handle missing/old price data
3. **Unit Conversions**: Ensure consistent units (tons, lbs, etc.)
4. **Nutrient Efficiency**: Account for application efficiency losses

## Next Steps for Integration

Integrates with:
- **Soil Testing Service**: For nutrient requirements
- **Weather Service** (Job 5): For application timing
- **Recommendation Engine**: For complete farm plans

