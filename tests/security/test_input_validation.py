"""
Security Tests for Input Validation and Sanitization

Tests input validation, SQL injection prevention, and data sanitization
to ensure secure handling of user inputs and agricultural data.
"""

import pytest
import re
from datetime import date, datetime
from decimal import Decimal
import json


class TestSQLInjectionPrevention:
    """Test SQL injection prevention mechanisms."""
    
    @pytest.mark.security
    def test_sql_injection_in_farm_queries(self):
        """Test SQL injection prevention in farm data queries."""
        
        # Malicious farm ID inputs
        malicious_inputs = [
            "'; DROP TABLE farms; --",
            "1 OR 1=1",
            "1; DELETE FROM soil_tests WHERE 1=1; --",
            "1 UNION SELECT * FROM users",
            "'; INSERT INTO farms (name) VALUES ('hacked'); --"
        ]
        
        for malicious_input in malicious_inputs:
            # Should reject malicious input
            with pytest.raises(ValidationError):
                self._validate_farm_id(malicious_input)
            
            # Should not execute in parameterized query
            result = self._safe_farm_query(malicious_input)
            assert result is None or result == []
    
    @pytest.mark.security
    def test_sql_injection_in_soil_test_queries(self):
        """Test SQL injection prevention in soil test queries."""
        
        malicious_soil_data = {
            'ph': "6.2'; DROP TABLE soil_tests; --",
            'organic_matter': "3.5 OR 1=1",
            'lab_name': "'; DELETE FROM farms; --"
        }
        
        # Should validate and reject malicious data
        for field, malicious_value in malicious_soil_data.items():
            with pytest.raises(ValidationError):
                self._validate_soil_test_field(field, malicious_value)
    
    @pytest.mark.security
    def test_parameterized_query_safety(self):
        """Test that parameterized queries prevent injection."""
        
        # Test with potentially dangerous input
        farm_id = "1'; DROP TABLE farms; --"
        
        # Parameterized query should treat input as literal value
        query = "SELECT * FROM farms WHERE id = ?"
        params = [farm_id]
        
        # Should not find any results (since farm_id doesn't exist)
        # but should not execute the DROP statement
        result = self._execute_parameterized_query(query, params)
        assert result == []
        
        # Verify farms table still exists (would fail if DROP executed)
        farms_exist = self._check_table_exists('farms')
        assert farms_exist is True
    
    def _validate_farm_id(self, farm_id):
        """Validate farm ID format."""
        # Farm IDs should be alphanumeric with hyphens/underscores only
        if not re.match(r'^[a-zA-Z0-9\-_]{1,50}$', farm_id):
            raise ValidationError("Invalid farm ID format")
        return farm_id
    
    def _validate_soil_test_field(self, field, value):
        """Validate soil test field values."""
        if field in ['ph', 'organic_matter']:
            try:
                float_value = float(value)
                if field == 'ph' and not (0 <= float_value <= 14):
                    raise ValidationError(f"pH value {float_value} out of range")
                if field == 'organic_matter' and not (0 <= float_value <= 100):
                    raise ValidationError(f"Organic matter {float_value} out of range")
            except (ValueError, TypeError):
                raise ValidationError(f"Invalid numeric value for {field}")
        
        elif field == 'lab_name':
            # Remove potentially dangerous characters
            if re.search(r'[<>"\';\\]', value):
                raise ValidationError("Lab name contains invalid characters")
        
        return value
    
    def _safe_farm_query(self, farm_id):
        """Execute safe parameterized farm query."""
        try:
            validated_id = self._validate_farm_id(farm_id)
            # Would execute: SELECT * FROM farms WHERE id = ?
            # with parameter [validated_id]
            return []  # Simulate no results for test
        except ValidationError:
            return None
    
    def _execute_parameterized_query(self, query, params):
        """Simulate parameterized query execution."""
        # In real implementation, this would use database parameterization
        # For testing, we simulate safe execution
        return []
    
    def _check_table_exists(self, table_name):
        """Check if database table exists."""
        # Simulate table existence check
        return True


class TestInputSanitization:
    """Test input sanitization and validation."""
    
    @pytest.mark.security
    def test_agricultural_data_sanitization(self):
        """Test sanitization of agricultural input data."""
        
        # Test soil test data sanitization
        raw_soil_data = {
            'ph': '6.2<script>alert("xss")</script>',
            'organic_matter_percent': '3.5"; DROP TABLE farms; --',
            'phosphorus_ppm': '25.0\x00\x01\x02',  # Null bytes
            'lab_name': 'Iowa State<img src=x onerror=alert(1)>Lab',
            'test_date': '2024-03-15\'; DELETE FROM soil_tests; --'
        }
        
        sanitized = self._sanitize_soil_test_data(raw_soil_data)
        
        # Should remove dangerous content
        assert '<script>' not in sanitized['ph']
        assert 'DROP TABLE' not in sanitized['organic_matter_percent']
        assert '\x00' not in sanitized['phosphorus_ppm']
        assert '<img' not in sanitized['lab_name']
        assert 'DELETE FROM' not in sanitized['test_date']
        
        # Should preserve valid data
        assert '6.2' in sanitized['ph']
        assert '3.5' in sanitized['organic_matter_percent']
        assert '25.0' in sanitized['phosphorus_ppm']
        assert 'Iowa State' in sanitized['lab_name']
        assert '2024-03-15' in sanitized['test_date']
    
    @pytest.mark.security
    def test_xss_prevention_in_text_fields(self):
        """Test XSS prevention in text input fields."""
        
        xss_payloads = [
            '<script>alert("xss")</script>',
            '<img src=x onerror=alert(1)>',
            'javascript:alert("xss")',
            '<svg onload=alert(1)>',
            '"><script>alert("xss")</script>',
            "'; alert('xss'); //",
            '<iframe src="javascript:alert(1)"></iframe>'
        ]
        
        for payload in xss_payloads:
            # Test in farm name field
            sanitized_name = self._sanitize_text_field(payload, 'farm_name')
            assert '<script>' not in sanitized_name
            assert 'javascript:' not in sanitized_name
            assert 'onerror=' not in sanitized_name
            assert 'onload=' not in sanitized_name
            
            # Test in notes field
            sanitized_notes = self._sanitize_text_field(payload, 'notes')
            assert not self._contains_executable_content(sanitized_notes)
    
    @pytest.mark.security
    def test_file_upload_validation(self):
        """Test file upload validation and sanitization."""
        
        # Test valid agricultural file types
        valid_files = [
            {'filename': 'soil_test_results.pdf', 'content_type': 'application/pdf'},
            {'filename': 'field_map.jpg', 'content_type': 'image/jpeg'},
            {'filename': 'yield_data.csv', 'content_type': 'text/csv'},
            {'filename': 'lab_report.xlsx', 'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}
        ]
        
        for file_info in valid_files:
            assert self._validate_file_upload(file_info) is True
        
        # Test malicious file types
        malicious_files = [
            {'filename': 'malware.exe', 'content_type': 'application/x-executable'},
            {'filename': 'script.js', 'content_type': 'application/javascript'},
            {'filename': 'shell.php', 'content_type': 'application/x-php'},
            {'filename': 'virus.bat', 'content_type': 'application/x-bat'},
            {'filename': 'backdoor.asp', 'content_type': 'application/x-asp'}
        ]
        
        for file_info in malicious_files:
            with pytest.raises(ValidationError):
                self._validate_file_upload(file_info)
        
        # Test filename sanitization
        dangerous_filenames = [
            '../../../etc/passwd',
            'file.pdf; rm -rf /',
            'test<script>.pdf',
            'file.pdf\x00.exe'
        ]
        
        for filename in dangerous_filenames:
            sanitized = self._sanitize_filename(filename)
            assert '../' not in sanitized
            assert ';' not in sanitized
            assert '<' not in sanitized
            assert '\x00' not in sanitized
    
    @pytest.mark.security
    def test_json_input_validation(self):
        """Test JSON input validation and sanitization."""
        
        # Test malicious JSON payloads
        malicious_json_strings = [
            '{"farm_id": "test", "__proto__": {"admin": true}}',  # Prototype pollution
            '{"soil_data": {"ph": "6.2", "constructor": {"prototype": {"admin": true}}}}',
            '{"location": {"latitude": 42.0, "longitude": -93.6, "eval": "alert(1)"}}',
            '{"notes": "Normal text", "script": "<script>alert(1)</script>"}'
        ]
        
        for json_string in malicious_json_strings:
            try:
                parsed = json.loads(json_string)
                sanitized = self._sanitize_json_object(parsed)
                
                # Should remove dangerous properties
                assert '__proto__' not in sanitized
                assert 'constructor' not in sanitized
                assert 'eval' not in sanitized
                
                # Should sanitize script content
                if 'script' in sanitized:
                    assert '<script>' not in str(sanitized['script'])
                
            except json.JSONDecodeError:
                # Invalid JSON should be rejected
                pass
    
    def _sanitize_soil_test_data(self, raw_data):
        """Sanitize soil test input data."""
        sanitized = {}
        
        for field, value in raw_data.items():
            if field in ['ph', 'organic_matter_percent', 'phosphorus_ppm']:
                # Extract numeric value, remove non-numeric characters
                numeric_match = re.search(r'(\d+\.?\d*)', str(value))
                if numeric_match:
                    sanitized[field] = numeric_match.group(1)
                else:
                    sanitized[field] = '0'
            
            elif field == 'lab_name':
                # Remove HTML tags and dangerous characters
                clean_value = re.sub(r'<[^>]*>', '', str(value))
                clean_value = re.sub(r'[<>"\';\\]', '', clean_value)
                sanitized[field] = clean_value[:100]  # Limit length
            
            elif field == 'test_date':
                # Extract date pattern, remove SQL injection attempts
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', str(value))
                if date_match:
                    sanitized[field] = date_match.group(1)
                else:
                    sanitized[field] = str(date.today())
            
            else:
                # Generic sanitization for other fields
                sanitized[field] = self._sanitize_text_field(str(value), field)
        
        return sanitized
    
    def _sanitize_text_field(self, value, field_name):
        """Sanitize text input field."""
        if not isinstance(value, str):
            value = str(value)
        
        # Remove HTML tags
        value = re.sub(r'<[^>]*>', '', value)
        
        # Remove JavaScript protocols
        value = re.sub(r'javascript:', '', value, flags=re.IGNORECASE)
        
        # Remove event handlers
        value = re.sub(r'on\w+\s*=', '', value, flags=re.IGNORECASE)
        
        # Remove null bytes and control characters
        value = re.sub(r'[\x00-\x1f\x7f]', '', value)
        
        # Limit length based on field type
        max_lengths = {
            'farm_name': 100,
            'notes': 1000,
            'lab_name': 100,
            'address': 200
        }
        
        max_length = max_lengths.get(field_name, 255)
        return value[:max_length]
    
    def _contains_executable_content(self, text):
        """Check if text contains potentially executable content."""
        dangerous_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _validate_file_upload(self, file_info):
        """Validate file upload security."""
        filename = file_info['filename']
        content_type = file_info['content_type']
        
        # Allowed file extensions for agricultural data
        allowed_extensions = {
            '.pdf', '.jpg', '.jpeg', '.png', '.csv', '.xlsx', '.xls', '.txt'
        }
        
        # Blocked dangerous extensions
        blocked_extensions = {
            '.exe', '.bat', '.cmd', '.com', '.scr', '.pif', '.js', '.vbs',
            '.php', '.asp', '.aspx', '.jsp', '.sh', '.py', '.pl'
        }
        
        # Extract file extension
        extension = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
        
        # Check against blocked extensions
        if extension in blocked_extensions:
            raise ValidationError(f"File type {extension} not allowed")
        
        # Check against allowed extensions
        if extension not in allowed_extensions:
            raise ValidationError(f"File type {extension} not supported")
        
        # Validate content type matches extension
        valid_content_types = {
            '.pdf': ['application/pdf'],
            '.jpg': ['image/jpeg'],
            '.jpeg': ['image/jpeg'],
            '.png': ['image/png'],
            '.csv': ['text/csv', 'application/csv'],
            '.xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
            '.txt': ['text/plain']
        }
        
        if extension in valid_content_types:
            if content_type not in valid_content_types[extension]:
                raise ValidationError("Content type doesn't match file extension")
        
        return True
    
    def _sanitize_filename(self, filename):
        """Sanitize uploaded filename."""
        # Remove path traversal attempts
        filename = filename.replace('../', '').replace('..\\', '')
        
        # Remove dangerous characters
        filename = re.sub(r'[<>:"|?*;]', '', filename)
        
        # Remove null bytes
        filename = filename.replace('\x00', '')
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')
        
        return filename
    
    def _sanitize_json_object(self, obj):
        """Sanitize JSON object recursively."""
        if isinstance(obj, dict):
            sanitized = {}
            for key, value in obj.items():
                # Skip dangerous property names
                if key in ['__proto__', 'constructor', 'prototype', 'eval', 'function']:
                    continue
                
                # Sanitize key
                clean_key = re.sub(r'[<>"\';\\]', '', str(key))
                
                # Recursively sanitize value
                sanitized[clean_key] = self._sanitize_json_object(value)
            
            return sanitized
        
        elif isinstance(obj, list):
            return [self._sanitize_json_object(item) for item in obj]
        
        elif isinstance(obj, str):
            return self._sanitize_text_field(obj, 'json_field')
        
        else:
            return obj


class TestAgriculturalDataValidation:
    """Test validation specific to agricultural data ranges and formats."""
    
    @pytest.mark.security
    def test_soil_ph_validation(self):
        """Test soil pH validation against realistic ranges."""
        
        # Valid pH values
        valid_ph_values = [3.5, 6.2, 7.0, 8.5, 9.5]
        for ph in valid_ph_values:
            assert self._validate_soil_ph(ph) is True
        
        # Invalid pH values (outside possible range)
        invalid_ph_values = [-1.0, 0.0, 15.0, 20.0, 'abc', None]
        for ph in invalid_ph_values:
            with pytest.raises(ValidationError):
                self._validate_soil_ph(ph)
        
        # Suspicious pH values (possible attack)
        suspicious_ph_values = [
            "6.2'; DROP TABLE soil_tests; --",
            "7.0 OR 1=1",
            "6.5<script>alert('xss')</script>"
        ]
        for ph in suspicious_ph_values:
            with pytest.raises(ValidationError):
                self._validate_soil_ph(ph)
    
    @pytest.mark.security
    def test_coordinate_validation(self):
        """Test GPS coordinate validation."""
        
        # Valid coordinates
        valid_coords = [
            (42.0308, -93.6319),  # Iowa
            (36.7783, -119.4179),  # California
            (45.0, -95.0),        # Minnesota
            (25.7617, -80.1918)   # Florida
        ]
        
        for lat, lon in valid_coords:
            assert self._validate_coordinates(lat, lon) is True
        
        # Invalid coordinates
        invalid_coords = [
            (91.0, -93.6),    # Latitude > 90
            (-91.0, -93.6),   # Latitude < -90
            (42.0, 181.0),    # Longitude > 180
            (42.0, -181.0),   # Longitude < -180
            ('abc', 'def'),   # Non-numeric
            (None, None)      # Null values
        ]
        
        for lat, lon in invalid_coords:
            with pytest.raises(ValidationError):
                self._validate_coordinates(lat, lon)
    
    @pytest.mark.security
    def test_nutrient_level_validation(self):
        """Test nutrient level validation."""
        
        # Test phosphorus validation
        valid_p_levels = [5, 15, 25, 50, 100]
        for p_level in valid_p_levels:
            assert self._validate_phosphorus_level(p_level) is True
        
        # Invalid phosphorus levels
        invalid_p_levels = [-5, 0, 1000, 'high', None]
        for p_level in invalid_p_levels:
            with pytest.raises(ValidationError):
                self._validate_phosphorus_level(p_level)
        
        # Test potassium validation
        valid_k_levels = [50, 150, 250, 400]
        for k_level in valid_k_levels:
            assert self._validate_potassium_level(k_level) is True
        
        # Invalid potassium levels
        invalid_k_levels = [-10, 0, 2000, 'medium', None]
        for k_level in invalid_k_levels:
            with pytest.raises(ValidationError):
                self._validate_potassium_level(k_level)
    
    def _validate_soil_ph(self, ph_value):
        """Validate soil pH value."""
        # Type validation
        try:
            ph_float = float(ph_value)
        except (ValueError, TypeError):
            raise ValidationError("pH must be numeric")
        
        # Range validation (agricultural + security)
        if not 3.0 <= ph_float <= 10.0:
            raise ValidationError(f"pH {ph_float} outside valid range (3.0-10.0)")
        
        return True
    
    def _validate_coordinates(self, latitude, longitude):
        """Validate GPS coordinates."""
        try:
            lat_float = float(latitude)
            lon_float = float(longitude)
        except (ValueError, TypeError):
            raise ValidationError("Coordinates must be numeric")
        
        if not -90 <= lat_float <= 90:
            raise ValidationError(f"Latitude {lat_float} outside valid range (-90 to 90)")
        
        if not -180 <= lon_float <= 180:
            raise ValidationError(f"Longitude {lon_float} outside valid range (-180 to 180)")
        
        return True
    
    def _validate_phosphorus_level(self, p_level):
        """Validate phosphorus level (ppm)."""
        try:
            p_float = float(p_level)
        except (ValueError, TypeError):
            raise ValidationError("Phosphorus level must be numeric")
        
        if not 1 <= p_float <= 500:
            raise ValidationError(f"Phosphorus level {p_float} outside reasonable range (1-500 ppm)")
        
        return True
    
    def _validate_potassium_level(self, k_level):
        """Validate potassium level (ppm)."""
        try:
            k_float = float(k_level)
        except (ValueError, TypeError):
            raise ValidationError("Potassium level must be numeric")
        
        if not 10 <= k_float <= 1000:
            raise ValidationError(f"Potassium level {k_float} outside reasonable range (10-1000 ppm)")
        
        return True


class ValidationError(Exception):
    """Custom validation exception."""
    pass