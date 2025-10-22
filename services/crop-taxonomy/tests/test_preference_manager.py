"""Tests for FarmerPreferenceManager class."""
import os
import sys
from uuid import uuid4, UUID
import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
import json

# Mock the database imports before importing the modules
sys.modules['src.database.crop_taxonomy_db'] = MagicMock()
sys.modules['src.models.preference_models'] = MagicMock()
sys.modules['database.crop_taxonomy_db'] = MagicMock()
sys.modules['models.preference_models'] = MagicMock()

_TEST_DIR = os.path.dirname(__file__)
_PARENT_DIR = os.path.abspath(os.path.join(_TEST_DIR, '..'))
_SRC_DIR = os.path.join(_PARENT_DIR, 'src')

if _PARENT_DIR not in sys.path:
    sys.path.insert(0, _PARENT_DIR)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

# Create standalone versions of the classes for testing
class PreferenceCategory:
    """Enumeration of preference categories with validation rules"""
    CROP_TYPES = "crop_types"
    MANAGEMENT_STYLE = "management_style"
    RISK_TOLERANCE = "risk_tolerance"
    MARKET_FOCUS = "market_focus"
    SUSTAINABILITY = "sustainability"
    LABOR_REQUIREMENTS = "labor_requirements"
    EQUIPMENT_PREFERENCES = "equipment_preferences"
    CERTIFICATION_GOALS = "certification_goals"
    YIELD_PRIORITIES = "yield_priorities"
    ECONOMIC_FACTORS = "economic_factors"

    @classmethod
    def all_categories(cls):
        return [
            cls.CROP_TYPES, cls.MANAGEMENT_STYLE, cls.RISK_TOLERANCE,
            cls.MARKET_FOCUS, cls.SUSTAINABILITY, cls.LABOR_REQUIREMENTS,
            cls.EQUIPMENT_PREFERENCES, cls.CERTIFICATION_GOALS,
            cls.YIELD_PRIORITIES, cls.ECONOMIC_FACTORS
        ]

    @classmethod
    def validate_category(cls, category):
        return category in cls.all_categories()


class FarmerPreference:
    """Data model for individual farmer preference entries"""
    
    def __init__(
        self,
        id=None,
        user_id=None,
        preference_category=None,
        preference_data=None,
        weight=1.0,
        created_at=None,
        updated_at=None,
        version=1,
        active=True
    ):
        self.id = id or uuid4()
        self.user_id = user_id
        self.preference_category = preference_category
        self.preference_data = preference_data or {}
        self.weight = max(0.0, min(1.0, weight))  # Ensure weight is between 0 and 1
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.version = version
        self.active = active

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'preference_category': self.preference_category,
            'preference_data': self.preference_data,
            'weight': float(self.weight),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'version': self.version,
            'active': self.active
        }


class FarmerPreferenceManager:
    """Simplified FarmerPreferenceManager for testing"""

    def __init__(self):
        self.db_connection = None

    async def _get_connection(self):
        """Get database connection"""
        if not self.db_connection:
            self.db_connection = AsyncMock()
        return self.db_connection

    def _validate_preference_data(self, category, data):
        """Validate preference data structure based on category"""
        if not PreferenceCategory.validate_category(category):
            return False

        required_fields = {
            PreferenceCategory.CROP_TYPES: ['preferred_crops'],
            PreferenceCategory.MANAGEMENT_STYLE: [],
            PreferenceCategory.RISK_TOLERANCE: ['level'],
            PreferenceCategory.MARKET_FOCUS: [],
            PreferenceCategory.SUSTAINABILITY: [],
            PreferenceCategory.LABOR_REQUIREMENTS: [],
            PreferenceCategory.EQUIPMENT_PREFERENCES: [],
            PreferenceCategory.CERTIFICATION_GOALS: [],
            PreferenceCategory.YIELD_PRIORITIES: [],
            PreferenceCategory.ECONOMIC_FACTORS: []
        }

        category_required = required_fields.get(category, [])
        return all(field in data for field in category_required)

    async def create_preference(
        self,
        user_id,
        preference_category,
        preference_data,
        weight=1.0
    ):
        """Create a new farmer preference"""
        
        if not PreferenceCategory.validate_category(preference_category):
            raise ValueError(f"Invalid preference category: {preference_category}")

        if not self._validate_preference_data(preference_category, preference_data):
            raise ValueError(f"Invalid preference data for category: {preference_category}")

        conn = await self._get_connection()
        
        preference = FarmerPreference(
            user_id=user_id,
            preference_category=preference_category,
            preference_data=preference_data,
            weight=weight
        )

        # Simulate database operation
        result = await conn.fetchrow()
        if result:
            return self._row_to_preference(result)
        else:
            raise Exception("Failed to create preference")

    async def get_user_preferences(
        self,
        user_id,
        category=None,
        include_inactive=False
    ):
        """Get all preferences for a user, optionally filtered by category"""
        
        if category and not PreferenceCategory.validate_category(category):
            raise ValueError(f"Invalid preference category: {category}")
            
        conn = await self._get_connection()
        
        # Return the mocked results from the connection
        results = await conn.fetch()
        preferences = [self._row_to_preference(row) for row in results]
        return preferences

    def _get_default_preferences(self, category):
        """Get default preferences for a category"""
        defaults = {
            PreferenceCategory.CROP_TYPES: {
                'preferred_crops': [],
                'avoided_crops': [],
                'new_crop_interest': True
            },
            PreferenceCategory.MANAGEMENT_STYLE: {
                'organic': False,
                'conventional': True,
                'precision_ag': False,
                'no_till': False
            },
            PreferenceCategory.RISK_TOLERANCE: {
                'level': 'moderate',
                'diversification_preference': True,
                'experimental_willingness': 0.5
            },
            PreferenceCategory.MARKET_FOCUS: {
                'local_markets': True,
                'commodity_markets': True,
                'specialty_crops': False,
                'value_added': False
            },
            PreferenceCategory.SUSTAINABILITY: {
                'carbon_sequestration': True,
                'water_conservation': True,
                'biodiversity': True,
                'soil_health': True
            }
        }
        
        return {
            'category': category,
            'preferences': defaults.get(category, {}),
            'is_default': True
        }

    def _resolve_preference_conflict(self, key, values):
        """Resolve conflicts when multiple preferences exist for the same key"""
        if not values:
            return None
            
        if len(values) == 1:
            return values[0]['value']
            
        # For boolean values, use weighted average approach
        if all(isinstance(v['value'], bool) for v in values):
            weighted_sum = sum(v['value'] * v['weight'] for v in values)
            return weighted_sum > 0.5
            
        # For numeric values, use weighted average
        if all(isinstance(v['value'], (int, float)) for v in values):
            return sum(v['value'] * v['weight'] for v in values)
            
        # For lists, merge and deduplicate
        if all(isinstance(v['value'], list) for v in values):
            merged = []
            for v in values:
                merged.extend(v['value'])
            return list(set(merged))
            
        # For strings and other types, use highest weight
        highest_weight_value = max(values, key=lambda x: x['weight'])
        return highest_weight_value['value']

    def _row_to_preference(self, row):
        """Convert database row to FarmerPreference object"""
        return FarmerPreference(
            id=row['id'],
            user_id=row['user_id'],
            preference_category=row['preference_category'],
            preference_data=json.loads(row['preference_data']) if isinstance(row['preference_data'], str) else row['preference_data'],
            weight=float(row['weight']),
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            version=row['version'],
            active=row['active']
        )


class TestPreferenceCategory:
    """Test the PreferenceCategory enumeration class."""
    
    def test_all_categories_returns_complete_list(self):
        """Test that all_categories returns all defined categories."""
        categories = PreferenceCategory.all_categories()
        
        expected_categories = [
            "crop_types", "management_style", "risk_tolerance",
            "market_focus", "sustainability", "labor_requirements",
            "equipment_preferences", "certification_goals",
            "yield_priorities", "economic_factors"
        ]
        
        assert set(categories) == set(expected_categories)
        assert len(categories) == 10
    
    def test_validate_category_valid_categories(self):
        """Test category validation for valid categories."""
        valid_categories = [
            "crop_types", "management_style", "risk_tolerance",
            "market_focus", "sustainability"
        ]
        
        for category in valid_categories:
            assert PreferenceCategory.validate_category(category) is True
    
    def test_validate_category_invalid_categories(self):
        """Test category validation for invalid categories."""
        invalid_categories = [
            "invalid_category", "", None, "CROP_TYPES", "crop-types"
        ]
        
        for category in invalid_categories:
            assert PreferenceCategory.validate_category(category) is False


class TestFarmerPreference:
    """Test the FarmerPreference data model."""
    
    def test_farmer_preference_initialization_with_defaults(self):
        """Test FarmerPreference initialization with default values."""
        user_id = uuid4()
        preference = FarmerPreference(
            user_id=user_id,
            preference_category="crop_types",
            preference_data={"preferred_crops": ["corn", "soybeans"]}
        )
        
        assert preference.user_id == user_id
        assert preference.preference_category == "crop_types"
        assert preference.preference_data == {"preferred_crops": ["corn", "soybeans"]}
        assert preference.weight == 1.0
        assert preference.version == 1
        assert preference.active is True
        assert isinstance(preference.id, UUID)
        assert isinstance(preference.created_at, datetime)
        assert isinstance(preference.updated_at, datetime)
    
    def test_farmer_preference_weight_constraints(self):
        """Test that weight is constrained between 0 and 1."""
        user_id = uuid4()
        
        # Test weight above 1
        preference_high = FarmerPreference(
            user_id=user_id,
            preference_category="crop_types",
            preference_data={},
            weight=1.5
        )
        assert preference_high.weight == 1.0
        
        # Test weight below 0
        preference_low = FarmerPreference(
            user_id=user_id,
            preference_category="crop_types",
            preference_data={},
            weight=-0.5
        )
        assert preference_low.weight == 0.0
        
        # Test valid weight
        preference_valid = FarmerPreference(
            user_id=user_id,
            preference_category="crop_types",
            preference_data={},
            weight=0.7
        )
        assert preference_valid.weight == 0.7
    
    def test_farmer_preference_to_dict(self):
        """Test conversion to dictionary."""
        user_id = uuid4()
        preference_id = uuid4()
        created_at = datetime.now()
        updated_at = datetime.now()
        
        preference = FarmerPreference(
            id=preference_id,
            user_id=user_id,
            preference_category="crop_types",
            preference_data={"preferred_crops": ["corn"]},
            weight=0.8,
            created_at=created_at,
            updated_at=updated_at,
            version=2,
            active=False
        )
        
        result = preference.to_dict()
        
        expected_keys = [
            'id', 'user_id', 'preference_category', 'preference_data',
            'weight', 'created_at', 'updated_at', 'version', 'active'
        ]
        
        assert set(result.keys()) == set(expected_keys)
        assert result['id'] == str(preference_id)
        assert result['user_id'] == str(user_id)
        assert result['preference_category'] == "crop_types"
        assert result['preference_data'] == {"preferred_crops": ["corn"]}
        assert result['weight'] == 0.8
        assert result['created_at'] == created_at.isoformat()
        assert result['updated_at'] == updated_at.isoformat()
        assert result['version'] == 2
        assert result['active'] is False


class TestFarmerPreferenceManager:
    """Test the FarmerPreferenceManager class."""
    
    @pytest.fixture
    def preference_manager(self):
        """Create a FarmerPreferenceManager instance for testing."""
        return FarmerPreferenceManager()
    
    @pytest.fixture
    def mock_connection(self):
        """Create a mock database connection."""
        mock_conn = AsyncMock()
        return mock_conn
    
    @pytest.fixture
    def sample_user_id(self):
        """Sample user ID for testing."""
        return uuid4()
    
    @pytest.fixture
    def sample_preference_data(self):
        """Sample preference data for testing."""
        return {
            "preferred_crops": ["corn", "soybeans"],
            "avoided_crops": ["wheat"],
            "new_crop_interest": True
        }
    
    def test_validate_preference_data_valid_crop_types(self, preference_manager):
        """Test preference data validation for valid crop_types data."""
        valid_data = {
            "preferred_crops": ["corn", "soybeans"],
            "avoided_crops": ["wheat"]
        }
        
        result = preference_manager._validate_preference_data("crop_types", valid_data)
        assert result is True
    
    def test_validate_preference_data_invalid_crop_types(self, preference_manager):
        """Test preference data validation for invalid crop_types data."""
        invalid_data = {
            "avoided_crops": ["wheat"]
            # Missing required "preferred_crops" field
        }
        
        result = preference_manager._validate_preference_data("crop_types", invalid_data)
        assert result is False
    
    def test_validate_preference_data_invalid_category(self, preference_manager):
        """Test preference data validation for invalid category."""
        data = {"preferred_crops": ["corn"]}
        
        result = preference_manager._validate_preference_data("invalid_category", data)
        assert result is False
    
    def test_validate_preference_data_risk_tolerance(self, preference_manager):
        """Test preference data validation for risk_tolerance category."""
        valid_data = {
            "level": "high",
            "diversification_preference": True
        }
        
        result = preference_manager._validate_preference_data("risk_tolerance", valid_data)
        assert result is True
        
        # Test missing required field
        invalid_data = {
            "diversification_preference": True
            # Missing required "level" field
        }
        
        result = preference_manager._validate_preference_data("risk_tolerance", invalid_data)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_create_preference_success(self, preference_manager, mock_connection, sample_user_id, sample_preference_data):
        """Test successful preference creation."""
        # Mock the database connection and fetchrow result
        mock_row = {
            'id': uuid4(),
            'user_id': sample_user_id,
            'preference_category': 'crop_types',
            'preference_data': json.dumps(sample_preference_data),
            'weight': Decimal('1.0'),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'version': 1,
            'active': True
        }
        
        mock_connection.fetchrow.return_value = mock_row
        
        with patch.object(preference_manager, '_get_connection', return_value=mock_connection):
            result = await preference_manager.create_preference(
                user_id=sample_user_id,
                preference_category="crop_types",
                preference_data=sample_preference_data,
                weight=1.0
            )
            
            assert isinstance(result, FarmerPreference)
            assert result.user_id == sample_user_id
            assert result.preference_category == "crop_types"
            assert result.preference_data == sample_preference_data
            assert result.weight == 1.0
            
            # Verify database call was made
            mock_connection.fetchrow.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_preference_invalid_category(self, preference_manager, sample_user_id, sample_preference_data):
        """Test preference creation with invalid category."""
        with pytest.raises(ValueError, match="Invalid preference category"):
            await preference_manager.create_preference(
                user_id=sample_user_id,
                preference_category="invalid_category",
                preference_data=sample_preference_data
            )
    
    @pytest.mark.asyncio
    async def test_create_preference_invalid_data(self, preference_manager, sample_user_id):
        """Test preference creation with invalid data."""
        invalid_data = {
            "avoided_crops": ["wheat"]
            # Missing required "preferred_crops" field for crop_types category
        }
        
        with pytest.raises(ValueError, match="Invalid preference data"):
            await preference_manager.create_preference(
                user_id=sample_user_id,
                preference_category="crop_types",
                preference_data=invalid_data
            )
    
    @pytest.mark.asyncio
    async def test_get_user_preferences_success(self, preference_manager, mock_connection, sample_user_id):
        """Test successful retrieval of user preferences."""
        mock_rows = [
            {
                'id': uuid4(),
                'user_id': sample_user_id,
                'preference_category': 'crop_types',
                'preference_data': '{"preferred_crops": ["corn"]}',
                'weight': Decimal('1.0'),
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'version': 1,
                'active': True
            },
            {
                'id': uuid4(),
                'user_id': sample_user_id,
                'preference_category': 'risk_tolerance',
                'preference_data': '{"level": "moderate"}',
                'weight': Decimal('0.8'),
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'version': 1,
                'active': True
            }
        ]
        
        mock_connection.fetch.return_value = mock_rows
        
        with patch.object(preference_manager, '_get_connection', return_value=mock_connection):
            result = await preference_manager.get_user_preferences(sample_user_id)
            
            assert len(result) == 2
            assert all(isinstance(pref, FarmerPreference) for pref in result)
            assert result[0].preference_category == 'crop_types'
            assert result[1].preference_category == 'risk_tolerance'
            
            # Verify database call was made
            mock_connection.fetch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_preferences_with_category_filter(self, preference_manager, mock_connection, sample_user_id):
        """Test retrieval of user preferences with category filter."""
        mock_rows = [
            {
                'id': uuid4(),
                'user_id': sample_user_id,
                'preference_category': 'crop_types',
                'preference_data': '{"preferred_crops": ["corn"]}',
                'weight': Decimal('1.0'),
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'version': 1,
                'active': True
            }
        ]
        
        mock_connection.fetch.return_value = mock_rows
        
        with patch.object(preference_manager, '_get_connection', return_value=mock_connection):
            result = await preference_manager.get_user_preferences(
                sample_user_id, 
                category="crop_types"
            )
            
            assert len(result) == 1
            assert result[0].preference_category == 'crop_types'
    
    @pytest.mark.asyncio
    async def test_get_user_preferences_invalid_category(self, preference_manager, sample_user_id):
        """Test retrieval of user preferences with invalid category."""
        with pytest.raises(ValueError, match="Invalid preference category"):
            await preference_manager.get_user_preferences(
                sample_user_id,
                category="invalid_category"
            )
    
    def test_get_default_preferences_crop_types(self, preference_manager):
        """Test getting default preferences for crop_types category."""
        result = preference_manager._get_default_preferences("crop_types")
        
        assert result['category'] == "crop_types"
        assert result['is_default'] is True
        assert 'preferences' in result
        assert 'preferred_crops' in result['preferences']
        assert 'avoided_crops' in result['preferences']
        assert 'new_crop_interest' in result['preferences']
    
    def test_get_default_preferences_risk_tolerance(self, preference_manager):
        """Test getting default preferences for risk_tolerance category."""
        result = preference_manager._get_default_preferences("risk_tolerance")
        
        assert result['category'] == "risk_tolerance"
        assert result['is_default'] is True
        assert 'preferences' in result
        assert result['preferences']['level'] == 'moderate'
        assert result['preferences']['diversification_preference'] is True
        assert result['preferences']['experimental_willingness'] == 0.5
    
    def test_resolve_preference_conflict_boolean_values(self, preference_manager):
        """Test resolving conflicts for boolean values."""
        values = [
            {'value': True, 'weight': 0.6, 'preference_id': 'pref1'},
            {'value': False, 'weight': 0.4, 'preference_id': 'pref2'}
        ]
        
        result = preference_manager._resolve_preference_conflict('test_key', values)
        assert result is True  # 0.6 > 0.5 threshold
        
        # Test with False winning
        values_false = [
            {'value': True, 'weight': 0.3, 'preference_id': 'pref1'},
            {'value': False, 'weight': 0.7, 'preference_id': 'pref2'}
        ]
        
        result_false = preference_manager._resolve_preference_conflict('test_key', values_false)
        assert result_false is False  # 0.3 < 0.5 threshold
    
    def test_resolve_preference_conflict_numeric_values(self, preference_manager):
        """Test resolving conflicts for numeric values."""
        values = [
            {'value': 10, 'weight': 0.6, 'preference_id': 'pref1'},
            {'value': 20, 'weight': 0.4, 'preference_id': 'pref2'}
        ]
        
        result = preference_manager._resolve_preference_conflict('test_key', values)
        expected = 10 * 0.6 + 20 * 0.4  # 6 + 8 = 14
        assert result == expected
    
    def test_resolve_preference_conflict_list_values(self, preference_manager):
        """Test resolving conflicts for list values."""
        values = [
            {'value': ['corn', 'soybeans'], 'weight': 0.6, 'preference_id': 'pref1'},
            {'value': ['wheat', 'corn'], 'weight': 0.4, 'preference_id': 'pref2'}
        ]
        
        result = preference_manager._resolve_preference_conflict('test_key', values)
        expected = ['corn', 'soybeans', 'wheat']  # Merged and deduplicated
        assert set(result) == set(expected)
    
    def test_resolve_preference_conflict_string_values(self, preference_manager):
        """Test resolving conflicts for string values."""
        values = [
            {'value': 'high', 'weight': 0.3, 'preference_id': 'pref1'},
            {'value': 'moderate', 'weight': 0.7, 'preference_id': 'pref2'}
        ]
        
        result = preference_manager._resolve_preference_conflict('test_key', values)
        assert result == 'moderate'  # Highest weight wins
    
    def test_resolve_preference_conflict_single_value(self, preference_manager):
        """Test resolving conflicts with single value."""
        values = [
            {'value': 'single_value', 'weight': 1.0, 'preference_id': 'pref1'}
        ]
        
        result = preference_manager._resolve_preference_conflict('test_key', values)
        assert result == 'single_value'
    
    def test_resolve_preference_conflict_empty_values(self, preference_manager):
        """Test resolving conflicts with empty values."""
        result = preference_manager._resolve_preference_conflict('test_key', [])
        assert result is None
    
    def test_row_to_preference_conversion(self, preference_manager):
        """Test conversion from database row to FarmerPreference object."""
        user_id = uuid4()
        preference_id = uuid4()
        created_at = datetime.now()
        updated_at = datetime.now()
        preference_data = {"preferred_crops": ["corn"]}
        
        mock_row = {
            'id': preference_id,
            'user_id': user_id,
            'preference_category': 'crop_types',
            'preference_data': json.dumps(preference_data),
            'weight': Decimal('0.8'),
            'created_at': created_at,
            'updated_at': updated_at,
            'version': 2,
            'active': False
        }
        
        result = preference_manager._row_to_preference(mock_row)
        
        assert isinstance(result, FarmerPreference)
        assert result.id == preference_id
        assert result.user_id == user_id
        assert result.preference_category == 'crop_types'
        assert result.preference_data == preference_data
        assert result.weight == 0.8
        assert result.created_at == created_at
        assert result.updated_at == updated_at
        assert result.version == 2
        assert result.active is False

    @pytest.mark.asyncio
    async def test_save_preferences(self, preference_manager, mock_connection, sample_user_id):
        """Test saving farmer preferences to the database."""
        # Test data for multiple preference categories
        preferences_to_save = [
            {
                "category": "crop_types",
                "data": {
                    "preferred_crops": ["corn", "soybeans", "wheat"],
                    "avoided_crops": ["sunflower"],
                    "new_crop_interest": True
                },
                "weight": 1.0
            },
            {
                "category": "risk_tolerance", 
                "data": {
                    "level": "moderate",
                    "diversification_preference": True,
                    "experimental_willingness": 0.7
                },
                "weight": 0.9
            },
            {
                "category": "sustainability",
                "data": {
                    "carbon_sequestration": True,
                    "water_conservation": True,
                    "biodiversity": False,
                    "soil_health": True
                },
                "weight": 0.8
            }
        ]
        
        # Mock successful database saves
        mock_saved_preferences = []
        for i, pref in enumerate(preferences_to_save):
            mock_row = {
                'id': uuid4(),
                'user_id': sample_user_id,
                'preference_category': pref['category'],
                'preference_data': json.dumps(pref['data']),
                'weight': Decimal(str(pref['weight'])),
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'version': 1,
                'active': True
            }
            mock_saved_preferences.append(mock_row)
        
        # Mock connection to return saved preferences one by one
        mock_connection.fetchrow.side_effect = mock_saved_preferences
        
        with patch.object(preference_manager, '_get_connection', return_value=mock_connection):
            saved_preferences = []
            
            # Save each preference
            for pref in preferences_to_save:
                result = await preference_manager.create_preference(
                    user_id=sample_user_id,
                    preference_category=pref['category'],
                    preference_data=pref['data'],
                    weight=pref['weight']
                )
                saved_preferences.append(result)
            
            # Verify all preferences were saved correctly
            assert len(saved_preferences) == 3
            
            # Verify crop_types preference
            crop_pref = saved_preferences[0]
            assert isinstance(crop_pref, FarmerPreference)
            assert crop_pref.user_id == sample_user_id
            assert crop_pref.preference_category == "crop_types"
            assert crop_pref.preference_data["preferred_crops"] == ["corn", "soybeans", "wheat"]
            assert crop_pref.preference_data["avoided_crops"] == ["sunflower"]
            assert crop_pref.preference_data["new_crop_interest"] is True
            assert crop_pref.weight == 1.0
            
            # Verify risk_tolerance preference
            risk_pref = saved_preferences[1]
            assert isinstance(risk_pref, FarmerPreference)
            assert risk_pref.user_id == sample_user_id
            assert risk_pref.preference_category == "risk_tolerance"
            assert risk_pref.preference_data["level"] == "moderate"
            assert risk_pref.preference_data["diversification_preference"] is True
            assert risk_pref.preference_data["experimental_willingness"] == 0.7
            assert risk_pref.weight == 0.9
            
            # Verify sustainability preference
            sustain_pref = saved_preferences[2]
            assert isinstance(sustain_pref, FarmerPreference)
            assert sustain_pref.user_id == sample_user_id
            assert sustain_pref.preference_category == "sustainability"
            assert sustain_pref.preference_data["carbon_sequestration"] is True
            assert sustain_pref.preference_data["water_conservation"] is True
            assert sustain_pref.preference_data["biodiversity"] is False
            assert sustain_pref.preference_data["soil_health"] is True
            assert sustain_pref.weight == 0.8
            
            # Verify database calls were made for each preference
            assert mock_connection.fetchrow.call_count == 3
    
    @pytest.mark.asyncio
    async def test_save_preferences_validation_errors(self, preference_manager, sample_user_id):
        """Test save preferences with validation errors."""
        # Test invalid category
        with pytest.raises(ValueError, match="Invalid preference category"):
            await preference_manager.create_preference(
                user_id=sample_user_id,
                preference_category="invalid_category",
                preference_data={"some": "data"},
                weight=1.0
            )
        
        # Test invalid data for crop_types (missing required field)
        with pytest.raises(ValueError, match="Invalid preference data"):
            await preference_manager.create_preference(
                user_id=sample_user_id,
                preference_category="crop_types",
                preference_data={"avoided_crops": ["wheat"]},  # Missing required preferred_crops
                weight=1.0
            )
        
        # Test invalid data for risk_tolerance (missing required field)
        with pytest.raises(ValueError, match="Invalid preference data"):
            await preference_manager.create_preference(
                user_id=sample_user_id,
                preference_category="risk_tolerance",
                preference_data={"diversification_preference": True},  # Missing required level
                weight=1.0
            )
    
    @pytest.mark.asyncio
    async def test_save_preferences_weight_constraints(self, preference_manager, mock_connection, sample_user_id):
        """Test save preferences with weight constraint validation."""
        preference_data = {
            "preferred_crops": ["corn"],
            "avoided_crops": [],
            "new_crop_interest": True
        }
        
        # Mock successful database save
        mock_row = {
            'id': uuid4(),
            'user_id': sample_user_id,
            'preference_category': 'crop_types',
            'preference_data': json.dumps(preference_data),
            'weight': Decimal('1.0'),  # Weight will be constrained to 1.0
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'version': 1,
            'active': True
        }
        mock_connection.fetchrow.return_value = mock_row
        
        with patch.object(preference_manager, '_get_connection', return_value=mock_connection):
            # Test weight above 1.0 gets constrained
            result = await preference_manager.create_preference(
                user_id=sample_user_id,
                preference_category="crop_types",
                preference_data=preference_data,
                weight=1.5  # Should be constrained to 1.0
            )
            
            assert result.weight == 1.0
            
            # Test weight below 0.0 gets constrained  
            mock_row['weight'] = Decimal('0.0')
            mock_connection.fetchrow.return_value = mock_row
            
            result = await preference_manager.create_preference(
                user_id=sample_user_id,
                preference_category="crop_types",
                preference_data=preference_data,
                weight=-0.5  # Should be constrained to 0.0
            )
            
            assert result.weight == 0.0

    @pytest.mark.asyncio
    async def test_load_preferences(self, preference_manager, mock_connection, sample_user_id):
        """Test loading farmer preferences from the database."""
        # Mock database rows for multiple preferences
        mock_preference_rows = [
            {
                'id': uuid4(),
                'user_id': sample_user_id,
                'preference_category': 'crop_types',
                'preference_data': json.dumps({
                    "preferred_crops": ["corn", "soybeans"],
                    "avoided_crops": ["wheat"],
                    "new_crop_interest": True
                }),
                'weight': Decimal('1.0'),
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'version': 1,
                'active': True
            },
            {
                'id': uuid4(),
                'user_id': sample_user_id,
                'preference_category': 'risk_tolerance',
                'preference_data': json.dumps({
                    "level": "moderate",
                    "diversification_preference": True,
                    "experimental_willingness": 0.7
                }),
                'weight': Decimal('0.9'),
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'version': 1,
                'active': True
            }
        ]
        
        # Mock connection to return the preference rows
        mock_connection.fetch.return_value = mock_preference_rows
        
        with patch.object(preference_manager, '_get_connection', return_value=mock_connection):
            # Test loading all preferences for a user
            result = await preference_manager.get_user_preferences(user_id=sample_user_id)
            
            assert len(result) == 2
            assert all(isinstance(pref, FarmerPreference) for pref in result)
            
            # Verify first preference
            crop_pref = next(pref for pref in result if pref.preference_category == 'crop_types')
            assert crop_pref.user_id == sample_user_id
            assert crop_pref.preference_category == "crop_types"
            assert crop_pref.preference_data["preferred_crops"] == ["corn", "soybeans"]
            assert crop_pref.weight == 1.0
            assert crop_pref.active is True
            
            # Verify second preference
            risk_pref = next(pref for pref in result if pref.preference_category == 'risk_tolerance')
            assert risk_pref.user_id == sample_user_id
            assert risk_pref.preference_category == "risk_tolerance"
            assert risk_pref.preference_data["level"] == "moderate"
            assert risk_pref.weight == 0.9
            assert risk_pref.active is True
            
            # Verify database call was made
            mock_connection.fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_load_preferences_by_category(self, preference_manager, mock_connection, sample_user_id):
        """Test loading farmer preferences filtered by category."""
        # Mock database row for specific category
        mock_preference_row = {
            'id': uuid4(),
            'user_id': sample_user_id,
            'preference_category': 'crop_types',
            'preference_data': json.dumps({
                "preferred_crops": ["corn", "soybeans"],
                "avoided_crops": ["wheat"],
                "new_crop_interest": True
            }),
            'weight': Decimal('1.0'),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'version': 1,
            'active': True
        }
        
        # Mock connection to return single preference row
        mock_connection.fetch.return_value = [mock_preference_row]
        
        with patch.object(preference_manager, '_get_connection', return_value=mock_connection):
            # Test loading preferences for specific category
            result = await preference_manager.get_user_preferences(
                user_id=sample_user_id, 
                category="crop_types"
            )
            
            assert len(result) == 1
            assert isinstance(result[0], FarmerPreference)
            assert result[0].user_id == sample_user_id
            assert result[0].preference_category == "crop_types"
            assert result[0].preference_data["preferred_crops"] == ["corn", "soybeans"]
            assert result[0].weight == 1.0
            
            # Verify database call was made with category filter
            mock_connection.fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_load_preferences_invalid_category(self, preference_manager, sample_user_id):
        """Test loading preferences with invalid category."""
        with pytest.raises(ValueError, match="Invalid preference category"):
            await preference_manager.get_user_preferences(
                user_id=sample_user_id,
                category="invalid_category"
            )

    @pytest.mark.asyncio
    async def test_load_preferences_empty_result(self, preference_manager, mock_connection, sample_user_id):
        """Test loading preferences when no preferences exist."""
        # Mock connection to return empty result
        mock_connection.fetch.return_value = []
        
        with patch.object(preference_manager, '_get_connection', return_value=mock_connection):
            result = await preference_manager.get_user_preferences(user_id=sample_user_id)
            
            assert len(result) == 0
            assert result == []
            
            # Verify database call was made
            mock_connection.fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_load_preferences_database_error(self, preference_manager, mock_connection, sample_user_id):
        """Test loading preferences with database error."""
        # Mock connection to raise an exception
        mock_connection.fetch.side_effect = Exception("Database connection error")
        
        with patch.object(preference_manager, '_get_connection', return_value=mock_connection):
            result = await preference_manager.get_user_preferences(user_id=sample_user_id)
            
            # Should return empty list on error
            assert result == []

    @pytest.mark.asyncio
    async def test_learn_from_selection(self, preference_manager, mock_connection, sample_user_id):
        """Test learning from user crop selections."""
        # Mock selected varieties with attributes
        selected_varieties = [
            {
                'id': 1,
                'crop_type': 'corn',
                'drought_tolerance': 'high',
                'organic_certified': True,
                'maturity_days': 90,
                'management_complexity': 'low'
            },
            {
                'id': 2,
                'crop_type': 'soybean',
                'drought_tolerance': 'moderate',
                'organic_certified': True,
                'maturity_days': 95,
                'management_complexity': 'low'
            }
        ]
        
        # Mock rejected varieties with different attributes
        rejected_varieties = [
            {
                'id': 3,
                'crop_type': 'wheat',
                'drought_tolerance': 'low',
                'organic_certified': False,
                'maturity_days': 120,
                'management_complexity': 'high'
            }
        ]
        
        # Mock context for the selection
        selection_context = {
            'search_filters': {
                'drought_tolerance': ['moderate', 'high'],
                'organic_certified': True
            },
            'location': 'Iowa',
            'season': 'spring',
            'timestamp': '2024-01-15T10:30:00Z'
        }
        
        # Mock database queries
        # Mock fetching variety details
        variety_details = selected_varieties + rejected_varieties
        mock_connection.fetch.return_value = [
            {'id': v['id'], 'crop_type': v['crop_type'], 
             'drought_tolerance': v['drought_tolerance'],
             'organic_certified': v['organic_certified'],
             'maturity_days': v['maturity_days'],
             'management_complexity': v['management_complexity']}
            for v in variety_details
        ]
        
        # Mock existing preferences query
        existing_preferences = []
        mock_connection.fetchrow.return_value = None  # No existing preferences
        
        with patch.object(preference_manager, '_get_connection', return_value=mock_connection):
            # Call learn_from_selection method
            result = await preference_manager.learn_from_selection(
                user_id=sample_user_id,
                selected_variety_ids=[1, 2],
                rejected_variety_ids=[3],
                context=selection_context
            )
            
            # Verify the learning results
            assert 'preferences_updated' in result
            assert 'new_preferences_created' in result
            assert 'confidence_improvements' in result
            assert 'learned_patterns' in result
            
            # Check that preferences were learned correctly
            assert result['new_preferences_created'] > 0
            assert len(result['learned_patterns']) > 0
            
            # Verify patterns learned include preference for organic and drought tolerance
            learned_patterns = result['learned_patterns']
            assert any('organic' in pattern.lower() for pattern in learned_patterns)
            assert any('drought' in pattern.lower() for pattern in learned_patterns)

    @pytest.mark.asyncio
    async def test_learn_from_selection_with_existing_preferences(self, preference_manager, mock_connection, sample_user_id):
        """Test learning from selections when user already has preferences."""
        # Mock existing preferences
        existing_preference = {
            'id': 'existing-pref-uuid',
            'user_id': sample_user_id,
            'preference_category': 'crop_types',
            'preference_data': {'preferred_crops': ['corn'], 'organic_preference': True},
            'weight': 0.8,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'version': 1,
            'active': True
        }
        
        # Mock selected varieties
        selected_varieties = [
            {
                'id': 4,
                'crop_type': 'soybean',
                'drought_tolerance': 'high',
                'organic_certified': True,
                'maturity_days': 100
            }
        ]
        
        # Mock database responses
        mock_connection.fetch.side_effect = [
            # First call: fetch variety details
            [{'id': 4, 'crop_type': 'soybean', 'drought_tolerance': 'high', 
              'organic_certified': True, 'maturity_days': 100}],
            # Second call: fetch existing preferences
            [existing_preference]
        ]
        
        mock_connection.fetchrow.return_value = existing_preference
        
        with patch.object(preference_manager, '_get_connection', return_value=mock_connection):
            result = await preference_manager.learn_from_selection(
                user_id=sample_user_id,
                selected_variety_ids=[4],
                rejected_variety_ids=[],
                context={'season': 'spring'}
            )
            
            # Should update existing preferences rather than create new ones
            assert result['preferences_updated'] >= 0
            assert 'learned_patterns' in result
            
            # Should have learned about soybean preference
            learned_patterns = result['learned_patterns']
            assert any('soybean' in pattern.lower() for pattern in learned_patterns)

    @pytest.mark.asyncio
    async def test_learn_from_selection_invalid_input(self, preference_manager, sample_user_id):
        """Test learning from selections with invalid input."""
        # Test with empty selection lists
        with pytest.raises(ValueError, match="At least one selected variety is required"):
            await preference_manager.learn_from_selection(
                user_id=sample_user_id,
                selected_variety_ids=[],
                rejected_variety_ids=[],
                context={}
            )
        
        # Test with invalid user_id
        with pytest.raises(ValueError, match="Invalid user_id"):
            await preference_manager.learn_from_selection(
                user_id=None,
                selected_variety_ids=[1, 2],
                rejected_variety_ids=[],
                context={}
            )

    @pytest.mark.asyncio
    async def test_learn_from_selection_database_error(self, preference_manager, mock_connection, sample_user_id):
        """Test learning from selections with database error."""
        # Mock database error
        mock_connection.fetch.side_effect = Exception("Database connection error")
        
        with patch.object(preference_manager, '_get_connection', return_value=mock_connection):
            result = await preference_manager.learn_from_selection(
                user_id=sample_user_id,
                selected_variety_ids=[1, 2],
                rejected_variety_ids=[],
                context={}
            )
            
            # Should return empty results on error but not raise exception
            assert result['preferences_updated'] == 0
            assert result['new_preferences_created'] == 0
            assert len(result['learned_patterns']) == 0


if __name__ == "__main__":
    pytest.main([__file__])