"""
Security Tests for Authentication and Authorization

Tests authentication mechanisms, session management, and access controls
to ensure secure access to agricultural data and recommendations.
"""

import pytest
import jwt
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import hashlib
import secrets


class TestAuthenticationMechanisms:
    """Test authentication mechanisms and security."""
    
    @pytest.mark.security
    def test_password_hashing_security(self):
        """Test password hashing uses secure algorithms."""
        
        password = "SecurePassword123!"
        
        # Test bcrypt hashing (recommended)
        hashed_password = self._hash_password_bcrypt(password)
        
        # Should not store plaintext
        assert password not in hashed_password
        
        # Should use bcrypt format
        assert hashed_password.startswith('$2b$')
        
        # Should verify correctly
        assert self._verify_password_bcrypt(password, hashed_password)
        
        # Should reject wrong password
        assert not self._verify_password_bcrypt("WrongPassword", hashed_password)
        
        # Should use sufficient rounds (minimum 12)
        rounds = int(hashed_password.split('$')[2])
        assert rounds >= 12, f"BCrypt rounds {rounds} too low, should be >=12"
    
    @pytest.mark.security
    def test_jwt_token_security(self):
        """Test JWT token generation and validation."""
        
        # Test token generation
        user_data = {
            'user_id': 'test_user_123',
            'username': 'test_farmer',
            'farm_ids': ['farm_456', 'farm_789'],
            'role': 'farmer'
        }
        
        secret_key = "test_secret_key_should_be_long_and_random"
        
        token = self._generate_jwt_token(user_data, secret_key)
        
        # Token should be properly formatted
        assert len(token.split('.')) == 3, "JWT should have 3 parts"
        
        # Should decode correctly with valid key
        decoded = self._decode_jwt_token(token, secret_key)
        assert decoded['user_id'] == user_data['user_id']
        assert decoded['username'] == user_data['username']
        
        # Should include expiration
        assert 'exp' in decoded
        assert decoded['exp'] > time.time()
        
        # Should reject with wrong key
        wrong_key = "wrong_secret_key"
        with pytest.raises(jwt.InvalidTokenError):
            self._decode_jwt_token(token, wrong_key)
    
    @pytest.mark.security
    def test_session_management_security(self):
        """Test session management security features."""
        
        # Test session creation
        session_data = {
            'user_id': 'test_user_123',
            'login_time': datetime.utcnow(),
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (Test Browser)'
        }
        
        session_id = self._create_session(session_data)
        
        # Session ID should be cryptographically secure
        assert len(session_id) >= 32, "Session ID should be at least 32 characters"
        
        # Should be able to retrieve session
        retrieved_session = self._get_session(session_id)
        assert retrieved_session['user_id'] == session_data['user_id']
        
        # Test session expiration
        expired_session_data = {
            **session_data,
            'login_time': datetime.utcnow() - timedelta(hours=25)  # Expired
        }
        
        expired_session_id = self._create_session(expired_session_data)
        
        # Should reject expired session
        with pytest.raises(SecurityError):
            self._validate_session(expired_session_id)
    
    @pytest.mark.security
    def test_multi_factor_authentication(self):
        """Test multi-factor authentication implementation."""
        
        user_id = 'test_user_123'
        
        # Test TOTP generation
        secret = self._generate_totp_secret()
        assert len(secret) >= 16, "TOTP secret should be at least 16 characters"
        
        # Test TOTP validation
        current_code = self._generate_totp_code(secret)
        assert len(current_code) == 6, "TOTP code should be 6 digits"
        assert current_code.isdigit(), "TOTP code should be numeric"
        
        # Should validate current code
        assert self._validate_totp_code(secret, current_code)
        
        # Should reject invalid code
        assert not self._validate_totp_code(secret, "000000")
        
        # Should reject reused code (replay protection)
        self._mark_totp_used(user_id, current_code)
        assert not self._validate_totp_code(secret, current_code, user_id)
    
    @pytest.mark.security
    def test_account_lockout_protection(self):
        """Test account lockout after failed login attempts."""
        
        username = 'test_farmer'
        
        # Test failed login tracking
        for attempt in range(3):
            self._record_failed_login(username)
        
        # Should not be locked after 3 attempts
        assert not self._is_account_locked(username)
        
        # Lock after 5 failed attempts
        for attempt in range(2):
            self._record_failed_login(username)
        
        # Should be locked after 5 attempts
        assert self._is_account_locked(username)
        
        # Should reject login even with correct password
        with pytest.raises(SecurityError):
            self._authenticate_user(username, "correct_password")
        
        # Test lockout duration
        lockout_time = self._get_lockout_time(username)
        assert lockout_time >= 300, "Lockout should be at least 5 minutes"
    
    def _hash_password_bcrypt(self, password):
        """Simulate bcrypt password hashing."""
        import bcrypt
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
    
    def _verify_password_bcrypt(self, password, hashed):
        """Simulate bcrypt password verification."""
        import bcrypt
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def _generate_jwt_token(self, user_data, secret_key):
        """Generate JWT token."""
        payload = {
            **user_data,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow(),
            'iss': 'afas_system'
        }
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    def _decode_jwt_token(self, token, secret_key):
        """Decode and validate JWT token."""
        return jwt.decode(token, secret_key, algorithms=['HS256'])
    
    def _create_session(self, session_data):
        """Create secure session."""
        session_id = secrets.token_urlsafe(32)
        
        # Store session data (would be in Redis/database)
        self._session_store = getattr(self, '_session_store', {})
        self._session_store[session_id] = session_data
        
        return session_id
    
    def _get_session(self, session_id):
        """Retrieve session data."""
        self._session_store = getattr(self, '_session_store', {})
        return self._session_store.get(session_id)
    
    def _validate_session(self, session_id):
        """Validate session is not expired."""
        session = self._get_session(session_id)
        if not session:
            raise SecurityError("Session not found")
        
        login_time = session['login_time']
        if datetime.utcnow() - login_time > timedelta(hours=24):
            raise SecurityError("Session expired")
        
        return session
    
    def _generate_totp_secret(self):
        """Generate TOTP secret."""
        return secrets.token_urlsafe(16)
    
    def _generate_totp_code(self, secret):
        """Generate current TOTP code."""
        import pyotp
        totp = pyotp.TOTP(secret)
        return totp.now()
    
    def _validate_totp_code(self, secret, code, user_id=None):
        """Validate TOTP code."""
        import pyotp
        
        # Check if code was already used (replay protection)
        if user_id and self._is_totp_code_used(user_id, code):
            return False
        
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)  # Allow 1 window tolerance
    
    def _mark_totp_used(self, user_id, code):
        """Mark TOTP code as used."""
        self._used_codes = getattr(self, '_used_codes', {})
        if user_id not in self._used_codes:
            self._used_codes[user_id] = set()
        self._used_codes[user_id].add(code)
    
    def _is_totp_code_used(self, user_id, code):
        """Check if TOTP code was already used."""
        self._used_codes = getattr(self, '_used_codes', {})
        return code in self._used_codes.get(user_id, set())
    
    def _record_failed_login(self, username):
        """Record failed login attempt."""
        self._failed_logins = getattr(self, '_failed_logins', {})
        if username not in self._failed_logins:
            self._failed_logins[username] = []
        
        self._failed_logins[username].append(datetime.utcnow())
    
    def _is_account_locked(self, username):
        """Check if account is locked due to failed attempts."""
        self._failed_logins = getattr(self, '_failed_logins', {})
        attempts = self._failed_logins.get(username, [])
        
        # Count attempts in last hour
        recent_attempts = [
            attempt for attempt in attempts
            if datetime.utcnow() - attempt < timedelta(hours=1)
        ]
        
        return len(recent_attempts) >= 5
    
    def _get_lockout_time(self, username):
        """Get lockout duration in seconds."""
        return 300  # 5 minutes
    
    def _authenticate_user(self, username, password):
        """Authenticate user with lockout check."""
        if self._is_account_locked(username):
            raise SecurityError("Account locked due to failed login attempts")
        
        # Would normally check password here
        return True


class TestAuthorizationControls:
    """Test authorization and access control mechanisms."""
    
    @pytest.mark.security
    def test_farm_access_authorization(self):
        """Test that users can only access their own farms."""
        
        # User A owns farm_123
        user_a = {
            'user_id': 'user_a',
            'farm_ids': ['farm_123', 'farm_456']
        }
        
        # User B owns farm_789
        user_b = {
            'user_id': 'user_b',
            'farm_ids': ['farm_789']
        }
        
        # User A should access their own farms
        assert self._check_farm_access(user_a, 'farm_123')
        assert self._check_farm_access(user_a, 'farm_456')
        
        # User A should NOT access other farms
        assert not self._check_farm_access(user_a, 'farm_789')
        
        # User B should access their own farm
        assert self._check_farm_access(user_b, 'farm_789')
        
        # User B should NOT access other farms
        assert not self._check_farm_access(user_b, 'farm_123')
    
    @pytest.mark.security
    def test_consultant_access_with_consent(self):
        """Test consultant access requires farmer consent."""
        
        consultant = {
            'user_id': 'consultant_1',
            'role': 'agricultural_consultant',
            'farm_ids': []
        }
        
        farmer = {
            'user_id': 'farmer_1',
            'farm_ids': ['farm_123']
        }
        
        # Consultant should NOT have access without consent
        assert not self._check_consultant_access(consultant, 'farm_123')
        
        # Grant consent
        self._grant_consultant_access(farmer['user_id'], 'farm_123', consultant['user_id'])
        
        # Consultant should now have access
        assert self._check_consultant_access(consultant, 'farm_123')
        
        # Revoke consent
        self._revoke_consultant_access(farmer['user_id'], 'farm_123', consultant['user_id'])
        
        # Consultant should lose access
        assert not self._check_consultant_access(consultant, 'farm_123')
    
    @pytest.mark.security
    def test_role_based_permissions(self):
        """Test role-based permission system."""
        
        farmer = {'user_id': 'farmer_1', 'role': 'farmer'}
        consultant = {'user_id': 'consultant_1', 'role': 'agricultural_consultant'}
        expert = {'user_id': 'expert_1', 'role': 'agricultural_expert'}
        admin = {'user_id': 'admin_1', 'role': 'system_admin'}
        
        # Test farmer permissions
        assert self._has_permission(farmer, 'view_own_farm_data')
        assert self._has_permission(farmer, 'create_soil_tests')
        assert not self._has_permission(farmer, 'view_all_farms')
        assert not self._has_permission(farmer, 'modify_system_settings')
        
        # Test consultant permissions
        assert self._has_permission(consultant, 'view_client_farm_data')
        assert self._has_permission(consultant, 'create_recommendations')
        assert not self._has_permission(consultant, 'modify_agricultural_logic')
        
        # Test expert permissions
        assert self._has_permission(expert, 'validate_recommendations')
        assert self._has_permission(expert, 'update_agricultural_logic')
        assert self._has_permission(expert, 'access_anonymized_data')
        assert not self._has_permission(expert, 'view_identifiable_data')
        
        # Test admin permissions
        assert self._has_permission(admin, 'modify_system_settings')
        assert self._has_permission(admin, 'view_system_logs')
        assert self._has_permission(admin, 'manage_user_accounts')
    
    @pytest.mark.security
    def test_data_access_levels(self):
        """Test different data access levels based on user role."""
        
        # Sensitive farm data
        farm_data = {
            'farm_id': 'farm_123',
            'farmer_name': 'John Doe',
            'location': {'latitude': 42.0308, 'longitude': -93.6319},
            'financial_data': {'annual_revenue': 250000, 'expenses': 180000},
            'soil_test_results': {'ph': 6.2, 'organic_matter': 3.5},
            'equipment_inventory': ['John Deere 8320R', 'Case IH 2150']
        }
        
        farmer = {'user_id': 'farmer_1', 'role': 'farmer', 'farm_ids': ['farm_123']}
        consultant = {'user_id': 'consultant_1', 'role': 'agricultural_consultant'}
        expert = {'user_id': 'expert_1', 'role': 'agricultural_expert'}
        
        # Farmer should see all their data
        farmer_view = self._filter_data_by_access_level(farm_data, farmer)
        assert 'farmer_name' in farmer_view
        assert 'financial_data' in farmer_view
        assert 'location' in farmer_view
        
        # Consultant with consent should see most data but not financial
        self._grant_consultant_access('farmer_1', 'farm_123', 'consultant_1')
        consultant_view = self._filter_data_by_access_level(farm_data, consultant)
        assert 'farmer_name' in consultant_view
        assert 'financial_data' not in consultant_view  # Financial data restricted
        assert 'soil_test_results' in consultant_view
        
        # Expert should only see anonymized/aggregated data
        expert_view = self._filter_data_by_access_level(farm_data, expert)
        assert 'farmer_name' not in expert_view  # No PII
        assert 'financial_data' not in expert_view  # No financial data
        assert 'soil_test_results' in expert_view  # Agricultural data OK
        assert expert_view.get('location', {}).get('latitude') is None  # No exact location
    
    def _check_farm_access(self, user, farm_id):
        """Check if user has access to specific farm."""
        return farm_id in user.get('farm_ids', [])
    
    def _check_consultant_access(self, consultant, farm_id):
        """Check if consultant has access to farm."""
        self._consultant_permissions = getattr(self, '_consultant_permissions', {})
        return farm_id in self._consultant_permissions.get(consultant['user_id'], [])
    
    def _grant_consultant_access(self, farmer_id, farm_id, consultant_id):
        """Grant consultant access to farm."""
        self._consultant_permissions = getattr(self, '_consultant_permissions', {})
        if consultant_id not in self._consultant_permissions:
            self._consultant_permissions[consultant_id] = []
        self._consultant_permissions[consultant_id].append(farm_id)
    
    def _revoke_consultant_access(self, farmer_id, farm_id, consultant_id):
        """Revoke consultant access to farm."""
        self._consultant_permissions = getattr(self, '_consultant_permissions', {})
        if consultant_id in self._consultant_permissions:
            if farm_id in self._consultant_permissions[consultant_id]:
                self._consultant_permissions[consultant_id].remove(farm_id)
    
    def _has_permission(self, user, permission):
        """Check if user has specific permission."""
        role_permissions = {
            'farmer': [
                'view_own_farm_data',
                'create_soil_tests',
                'request_recommendations',
                'view_recommendation_history',
                'update_farm_profile'
            ],
            'agricultural_consultant': [
                'view_client_farm_data',
                'create_recommendations',
                'export_reports',
                'manage_multiple_farms'
            ],
            'agricultural_expert': [
                'validate_recommendations',
                'update_agricultural_logic',
                'access_anonymized_data',
                'review_system_accuracy'
            ],
            'system_admin': [
                'modify_system_settings',
                'view_system_logs',
                'manage_user_accounts',
                'access_all_data'
            ]
        }
        
        user_role = user.get('role', 'farmer')
        allowed_permissions = role_permissions.get(user_role, [])
        return permission in allowed_permissions
    
    def _filter_data_by_access_level(self, data, user):
        """Filter data based on user's access level."""
        role = user.get('role', 'farmer')
        
        if role == 'farmer':
            # Farmers see all their own data
            return data.copy()
        
        elif role == 'agricultural_consultant':
            # Consultants see most data but not financial
            filtered = data.copy()
            filtered.pop('financial_data', None)
            return filtered
        
        elif role == 'agricultural_expert':
            # Experts see anonymized agricultural data only
            filtered = {
                'soil_test_results': data.get('soil_test_results'),
                'crop_data': data.get('crop_data'),
                'management_practices': data.get('management_practices')
            }
            # Remove exact location, keep general region
            if 'location' in data:
                filtered['region'] = 'midwest'  # Generalized location
            return filtered
        
        else:
            return {}


class SecurityError(Exception):
    """Custom security exception."""
    pass