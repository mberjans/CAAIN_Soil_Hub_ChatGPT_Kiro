"""
Tests for Address Validation Service
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

Comprehensive test suite for address validation and standardization functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

# Import the service and models
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src/services'))

from address_validation_service import (
    AddressValidationService, AddressValidationResult, AddressComponents,
    AddressValidationIssue, AddressValidationSeverity, USPSProvider,
    PostalCodeValidator, AddressStandardizer, AgriculturalAreaValidator
)


class TestAddressComponents:
    """Test AddressComponents model."""
    
    def test_address_components_creation(self):
        """Test creating AddressComponents with valid data."""
        components = AddressComponents(
            street_number="123",
            street_name="Main",
            street_type="St",
            city="Ames",
            state="IA",
            postal_code="50010"
        )
        
        assert components.street_number == "123"
        assert components.street_name == "Main"
        assert components.street_type == "St"
        assert components.city == "Ames"
        assert components.state == "IA"
        assert components.postal_code == "50010"
        assert components.country == "US"  # Default value
    
    def test_address_components_rural(self):
        """Test creating AddressComponents with rural address data."""
        components = AddressComponents(
            rural_route="RR 1",
            box_number="Box 123",
            city="Rural City",
            state="IA",
            postal_code="50010"
        )
        
        assert components.rural_route == "RR 1"
        assert components.box_number == "Box 123"
        assert components.city == "Rural City"
        assert components.state == "IA"


class TestPostalCodeValidator:
    """Test PostalCodeValidator functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = PostalCodeValidator()
    
    def test_validate_us_zip_valid(self):
        """Test validation of valid US ZIP codes."""
        # Test 5-digit ZIP
        result = self.validator.validate_postal_code("50010", "US")
        assert result["valid"] is True
        assert result["zip5"] == "50010"
        assert result["country"] == "US"
        assert result["format"] == "US_ZIP"
        
        # Test ZIP+4
        result = self.validator.validate_postal_code("50010-1234", "US")
        assert result["valid"] is True
        assert result["zip5"] == "50010"
        assert result["zip4"] == "1234"
    
    def test_validate_us_zip_invalid(self):
        """Test validation of invalid US ZIP codes."""
        # Test invalid format
        result = self.validator.validate_postal_code("123", "US")
        assert result["valid"] is False
        assert "error" in result
        
        # Test empty ZIP
        result = self.validator.validate_postal_code("", "US")
        assert result["valid"] is False
        assert "required" in result["error"]
    
    def test_validate_canadian_postal_valid(self):
        """Test validation of valid Canadian postal codes."""
        result = self.validator.validate_postal_code("K1A 0A6", "CA")
        assert result["valid"] is True
        assert result["country"] == "CA"
        assert result["format"] == "CANADIAN_POSTAL"
    
    def test_validate_canadian_postal_invalid(self):
        """Test validation of invalid Canadian postal codes."""
        result = self.validator.validate_postal_code("12345", "CA")
        assert result["valid"] is False
        assert "error" in result
    
    def test_validate_unsupported_country(self):
        """Test validation with unsupported country."""
        result = self.validator.validate_postal_code("12345", "UK")
        assert result["valid"] is False
        assert "Unsupported country" in result["error"]
    
    @pytest.mark.asyncio
    async def test_lookup_postal_code_info(self):
        """Test postal code lookup functionality."""
        result = await self.validator.lookup_postal_code_info("50010", "US")
        
        assert "zip5" in result
        assert result["zip5"] == "50010"
        assert "agricultural_area" in result


class TestAddressStandardizer:
    """Test AddressStandardizer functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.standardizer = AddressStandardizer()
    
    def test_standardize_address_basic(self):
        """Test basic address standardization."""
        address = "123 Main Street, Ames, IA 50010"
        components = self.standardizer.standardize_address(address)
        
        assert components.street_number == "123"
        assert components.street_name == "Main"
        assert components.street_type == "ST"
        assert components.city == "Ames"
        assert components.state == "IA"
        assert components.postal_code == "50010"
    
    def test_standardize_address_with_direction(self):
        """Test address standardization with directional prefix."""
        address = "123 North Main Street, Ames, IA 50010"
        components = self.standardizer.standardize_address(address)
        
        assert components.street_number == "123"
        assert components.street_direction == "N"
        assert components.street_name == "Main"
        assert components.street_type == "ST"
    
    def test_standardize_street_types(self):
        """Test street type standardization."""
        # Test various street types
        test_cases = [
            ("street", "St"),
            ("avenue", "Ave"),
            ("road", "Rd"),
            ("drive", "Dr"),
            ("boulevard", "Blvd"),
            ("highway", "Hwy")
        ]
        
        for input_type, expected_output in test_cases:
            result = self.standardizer._standardize_street_type(input_type)
            assert result == expected_output
    
    def test_standardize_directions(self):
        """Test directional standardization."""
        test_cases = [
            ("north", "N"),
            ("south", "S"),
            ("east", "E"),
            ("west", "W"),
            ("northeast", "NE"),
            ("southwest", "SW")
        ]
        
        for input_dir, expected_output in test_cases:
            result = self.standardizer._standardize_direction(input_dir)
            assert result == expected_output
    
    def test_standardize_states(self):
        """Test state abbreviation standardization."""
        test_cases = [
            ("iowa", "IA"),
            ("california", "CA"),
            ("new york", "NY"),
            ("texas", "TX")
        ]
        
        for input_state, expected_output in test_cases:
            result = self.standardizer._standardize_state(input_state)
            assert result == expected_output
    
    def test_standardize_postal_code(self):
        """Test postal code standardization."""
        # Test ZIP+4 formatting
        result = self.standardizer._standardize_postal_code("500101234")
        assert result == "50010-1234"
        
        # Test already formatted
        result = self.standardizer._standardize_postal_code("50010-1234")
        assert result == "50010-1234"
        
        # Test 5-digit ZIP
        result = self.standardizer._standardize_postal_code("50010")
        assert result == "50010"


class TestAgriculturalAreaValidator:
    """Test AgriculturalAreaValidator functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = AgriculturalAreaValidator()
    
    @pytest.mark.asyncio
    async def test_validate_agricultural_area_farm_street(self):
        """Test agricultural area validation with farm street name."""
        components = AddressComponents(
            street_name="Farm Road",
            city="Ames",
            state="IA",
            postal_code="50010"
        )
        
        result = await self.validator.validate_agricultural_area(components)
        
        assert result["is_agricultural"] is True
        assert result["agricultural_score"] >= 0.25
        assert any("farm" in ind.lower() for ind in result["indicators"])
    
    @pytest.mark.asyncio
    async def test_validate_agricultural_area_rural_route(self):
        """Test agricultural area validation with rural route."""
        components = AddressComponents(
            rural_route="RR 1",
            city="Rural City",
            state="IA",
            postal_code="50010"
        )
        
        result = await self.validator.validate_agricultural_area(components)
        
        assert result["is_agricultural"] is True
        assert result["agricultural_score"] >= 0.25
        assert "Rural route or PO Box address" in result["indicators"]
    
    @pytest.mark.asyncio
    async def test_validate_agricultural_area_po_box(self):
        """Test agricultural area validation with PO Box."""
        components = AddressComponents(
            box_number="Box 123",
            city="Rural City",
            state="IA",
            postal_code="50010"
        )
        
        result = await self.validator.validate_agricultural_area(components)
        
        assert result["is_agricultural"] is True
        assert result["agricultural_score"] >= 0.25
        assert "Rural route or PO Box address" in result["indicators"]
    
    @pytest.mark.asyncio
    async def test_validate_agricultural_area_urban(self):
        """Test agricultural area validation with urban address."""
        components = AddressComponents(
            street_name="Broadway",
            city="New York",
            state="NY",
            postal_code="10001"
        )
        
        result = await self.validator.validate_agricultural_area(components)
        
        # Should not be classified as agricultural
        assert result["is_agricultural"] is False
        assert result["agricultural_score"] < 0.3
    
    def test_build_full_address(self):
        """Test building full address from components."""
        components = AddressComponents(
            street_number="123",
            street_direction="N",
            street_name="Main",
            street_type="St",
            unit_number="Apt 1"
        )
        
        full_address = self.validator._build_full_address(components)
        expected = "123 N Main St Apt 1"
        assert full_address == expected


class TestUSPSProvider:
    """Test USPSProvider functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.provider = USPSProvider("test_api_key")
    
    def test_usps_provider_no_api_key(self):
        """Test USPS provider without API key."""
        provider = USPSProvider()
        assert provider.api_key is None
    
    def test_build_usps_xml(self):
        """Test USPS XML request building."""
        components = AddressComponents(
            street_number="123",
            street_name="Main",
            street_type="St",
            city="Ames",
            state="IA",
            postal_code="50010"
        )
        
        xml = self.provider._build_usps_xml(components)
        
        assert "AddressValidateRequest" in xml
        assert "123 Main St" in xml
        assert "Ames" in xml
        assert "IA" in xml
        assert "50010" in xml
    
    def test_parse_usps_response_valid(self):
        """Test parsing valid USPS response."""
        response_text = "<Address1>123 Main St</Address1>"
        result = self.provider._parse_usps_response(response_text)
        
        assert result["valid"] is True
        assert result["standardized"] is True
        assert result["source"] == "USPS"
    
    def test_parse_usps_response_error(self):
        """Test parsing USPS response with error."""
        response_text = "<Error>Address not found</Error>"
        result = self.provider._parse_usps_response(response_text)
        
        assert result["valid"] is False
        assert "error" in result


class TestAddressValidationService:
    """Test AddressValidationService functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = AddressValidationService()
    
    @pytest.mark.asyncio
    async def test_validate_and_standardize_address_valid(self):
        """Test validation of valid address."""
        address = "123 Main St, Ames, IA 50010"
        
        result = await self.service.validate_and_standardize_address(address)
        
        assert isinstance(result, AddressValidationResult)
        assert result.valid is True
        assert result.confidence_score > 0.0
        assert result.standardized_address is not None
        assert result.components is not None
        assert "address_standardizer" in result.validation_sources
    
    @pytest.mark.asyncio
    async def test_validate_and_standardize_address_invalid_postal(self):
        """Test validation of address with invalid postal code."""
        address = "123 Main St, Ames, IA 123"
        
        result = await self.service.validate_and_standardize_address(address)
        
        assert isinstance(result, AddressValidationResult)
        assert result.valid is False
        assert len(result.errors) > 0
        assert "postal code" in result.errors[0].lower()
    
    @pytest.mark.asyncio
    async def test_validate_and_standardize_address_agricultural(self):
        """Test validation with agricultural context."""
        address = "123 Farm Road, Ames, IA 50010"
        
        result = await self.service.validate_and_standardize_address(address, include_agricultural_context=True)
        
        assert isinstance(result, AddressValidationResult)
        assert result.agricultural_context is not None
        assert "agricultural_validator" in result.validation_sources
    
    @pytest.mark.asyncio
    async def test_validate_address_components(self):
        """Test validation of address components."""
        components = AddressComponents(
            street_number="123",
            street_name="Main",
            street_type="St",
            city="Ames",
            state="IA",
            postal_code="50010"
        )
        
        result = await self.service.validate_address_components(components)
        
        assert isinstance(result, AddressValidationResult)
        assert result.valid is True
        assert result.components is not None
    
    @pytest.mark.asyncio
    async def test_batch_validate_addresses(self):
        """Test batch address validation."""
        addresses = [
            "123 Main St, Ames, IA 50010",
            "456 Oak Ave, Des Moines, IA 50301",
            "789 Pine Rd, Cedar Rapids, IA 52401"
        ]
        
        results = await self.service.batch_validate_addresses(addresses)
        
        assert len(results) == 3
        assert all(isinstance(result, AddressValidationResult) for result in results)
        assert all(result.valid for result in results)
    
    @pytest.mark.asyncio
    async def test_batch_validate_addresses_with_errors(self):
        """Test batch validation with some invalid addresses."""
        addresses = [
            "123 Main St, Ames, IA 50010",  # Valid
            "456 Oak Ave, Des Moines, IA 123",  # Invalid postal code
            "789 Pine Rd, Cedar Rapids, IA 52401"  # Valid
        ]
        
        results = await self.service.batch_validate_addresses(addresses)
        
        assert len(results) == 3
        assert results[0].valid is True
        assert results[1].valid is False
        assert results[2].valid is True
    
    def test_calculate_confidence_score(self):
        """Test confidence score calculation."""
        # Test with all validations passing
        postal_validation = {"valid": True}
        usps_result = {"valid": True}
        agricultural_context = {"is_agricultural": True}
        
        score = self.service._calculate_confidence_score(
            postal_validation, usps_result, agricultural_context
        )
        
        assert score == 1.0
        
        # Test with partial validations
        postal_validation = {"valid": True}
        usps_result = None  # Not available
        agricultural_context = {"is_agricultural": False}
        
        score = self.service._calculate_confidence_score(
            postal_validation, usps_result, agricultural_context
        )
        
        assert abs(score - 0.6) < 0.01  # 0.4 + 0.2 + 0.0 (accounting for floating point precision)
    
    def test_build_standardized_address(self):
        """Test building standardized address string."""
        components = AddressComponents(
            street_number="123",
            street_direction="N",
            street_name="Main",
            street_type="St",
            city="Ames",
            state="IA",
            postal_code="50010"
        )
        
        standardized = self.service._build_standardized_address(components)
        expected = "123 N Main St, Ames, IA, 50010"
        assert standardized == expected


class TestAddressValidationIntegration:
    """Integration tests for address validation system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = AddressValidationService()
    
    @pytest.mark.asyncio
    async def test_complete_address_validation_workflow(self):
        """Test complete address validation workflow."""
        # Test various address formats
        test_addresses = [
            "123 Main Street, Ames, IA 50010",
            "456 North Oak Avenue, Des Moines, IA 50301",
            "789 Farm Road, Cedar Rapids, IA 52401",
            "321 Rural Route 1, Box 123, Iowa City, IA 52240"
        ]
        
        for address in test_addresses:
            result = await self.service.validate_and_standardize_address(address)
            
            # Basic assertions
            assert isinstance(result, AddressValidationResult)
            assert result.confidence_score >= 0.0
            assert result.confidence_score <= 1.0
            
            # Check that components are parsed
            if result.components:
                assert result.components.city is not None
                assert result.components.state is not None
                assert result.components.postal_code is not None
    
    @pytest.mark.asyncio
    async def test_agricultural_area_detection(self):
        """Test agricultural area detection across different address types."""
        agricultural_addresses = [
            "123 Farm Road, Ames, IA 50010",
            "456 Ranch Lane, Des Moines, IA 50301",
            "789 Rural Route 1, Cedar Rapids, IA 52401",
            "321 Box 123, Iowa City, IA 52240"
        ]
        
        for address in agricultural_addresses:
            result = await self.service.validate_and_standardize_address(address, include_agricultural_context=True)
            
            # Should detect agricultural areas
            if result.agricultural_context:
                assert result.agricultural_context["is_agricultural"] is True
                assert result.agricultural_context["agricultural_score"] >= 0.25
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling for various edge cases."""
        # Test empty address
        result = await self.service.validate_and_standardize_address("")
        assert result.valid is False
        assert len(result.errors) > 0
        
        # Test malformed address
        result = await self.service.validate_and_standardize_address("Not an address")
        assert result.valid is False
        
        # Test address with invalid postal code
        result = await self.service.validate_and_standardize_address("123 Main St, Ames, IA 123")
        assert result.valid is False
        assert any("postal code" in error.lower() for error in result.errors)


# Performance tests
class TestAddressValidationPerformance:
    """Performance tests for address validation system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = AddressValidationService()
    
    @pytest.mark.asyncio
    async def test_single_address_performance(self):
        """Test performance of single address validation."""
        import time
        
        address = "123 Main St, Ames, IA 50010"
        
        start_time = time.time()
        result = await self.service.validate_and_standardize_address(address)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert processing_time < 2.0  # 2 seconds
        assert result.valid is True
    
    @pytest.mark.asyncio
    async def test_batch_performance(self):
        """Test performance of batch address validation."""
        import time
        
        # Create list of test addresses
        addresses = [
            f"{i} Main St, Ames, IA 50010" for i in range(1, 21)
        ]
        
        start_time = time.time()
        results = await self.service.batch_validate_addresses(addresses)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should complete within reasonable time
        assert processing_time < 10.0  # 10 seconds for 20 addresses
        assert len(results) == 20
        assert all(result.valid for result in results)


if __name__ == "__main__":
    pytest.main([__file__])
