"""
API tests for authentication endpoints.

This module contains API tests for authentication-related endpoints.
"""

import pytest
from unittest.mock import patch, Mock
from werkzeug.security import generate_password_hash

from test.base_test import BaseAPITestCase
from app.users.model import User
from app.common.enum import UserTypeEnum, LanguageEnum


class TestAuthEndpoints(BaseAPITestCase):
    """Test cases for authentication endpoints."""
    
    def test_login_success(self, db_session, sample_user):
        """Test successful login."""
        # Mock JWT token generation
        with patch('jwt.encode') as mock_jwt_encode:
            mock_jwt_encode.return_value = 'test_token'
            
            login_data = {
                'email': sample_user.email,
                'password': 'testpassword'
            }
            
            response = self.post('/api/auth/login', json_data=login_data)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'token' in data
            assert 'user' in data
            assert data['user']['id'] == str(sample_user.id)
            assert data['user']['email'] == sample_user.email
    
    def test_login_invalid_credentials(self, db_session):
        """Test login with invalid credentials."""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.post('/api/auth/login', json_data=login_data)
        
        self.assert_response_unauthorized(response)
        data = self.get_json_response(response)
        
        assert 'error' in data
        assert 'Invalid credentials' in data['error']
    
    def test_login_missing_fields(self, db_session):
        """Test login with missing required fields."""
        login_data = {
            'email': 'test@example.com'
            # Missing password
        }
        
        response = self.post('/api/auth/login', json_data=login_data)
        
        self.assert_response_error(response, 400)
        data = self.get_json_response(response)
        
        assert 'error' in data
        assert 'validation' in data['error']
    
    def test_register_success(self, db_session):
        """Test successful user registration."""
        with patch('jwt.encode') as mock_jwt_encode:
            mock_jwt_encode.return_value = 'test_token'
            
            register_data = {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'phone': '+1234567899',
                'password': 'newpassword',
                'user_type': 'USER',
                'language': 'ENGLISH'
            }
            
            response = self.post('/api/auth/register', json_data=register_data)
            
            self.assert_response_success(response, 201)
            data = self.get_json_response(response)
            
            assert 'token' in data
            assert 'user' in data
            assert data['user']['username'] == 'newuser'
            assert data['user']['email'] == 'newuser@example.com'
            assert data['user']['phone'] == '+1234567899'
    
    def test_register_duplicate_email(self, db_session, sample_user):
        """Test registration with duplicate email."""
        register_data = {
            'username': 'newuser',
            'email': sample_user.email,  # Duplicate email
            'phone': '+1234567899',
            'password': 'newpassword',
            'user_type': 'USER',
            'language': 'ENGLISH'
        }
        
        response = self.post('/api/auth/register', json_data=register_data)
        
        self.assert_response_error(response, 400)
        data = self.get_json_response(response)
        
        assert 'error' in data
        assert 'email' in data['error'].lower()
    
    def test_register_duplicate_phone(self, db_session, sample_user):
        """Test registration with duplicate phone."""
        register_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'phone': sample_user.phone,  # Duplicate phone
            'password': 'newpassword',
            'user_type': 'USER',
            'language': 'ENGLISH'
        }
        
        response = self.post('/api/auth/register', json_data=register_data)
        
        self.assert_response_error(response, 400)
        data = self.get_json_response(response)
        
        assert 'error' in data
        assert 'phone' in data['error'].lower()
    
    def test_register_missing_fields(self, db_session):
        """Test registration with missing required fields."""
        register_data = {
            'username': 'newuser',
            'email': 'newuser@example.com'
            # Missing phone, password, etc.
        }
        
        response = self.post('/api/auth/register', json_data=register_data)
        
        self.assert_response_error(response, 400)
        data = self.get_json_response(response)
        
        assert 'error' in data
        assert 'validation' in data['error']
    
    def test_logout_success(self, db_session, sample_user):
        """Test successful logout."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': str(sample_user.id), 'user_type': 'USER'}
            
            response = self.post('/api/auth/logout', headers=self.auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'message' in data
            assert 'successfully' in data['message'].lower()
    
    def test_logout_invalid_token(self, db_session):
        """Test logout with invalid token."""
        invalid_headers = {
            'Authorization': 'Bearer invalid_token',
            'Content-Type': 'application/json'
        }
        
        response = self.post('/api/auth/logout', headers=invalid_headers)
        
        self.assert_response_unauthorized(response)
        data = self.get_json_response(response)
        
        assert 'error' in data
        assert 'token' in data['error'].lower()
    
    def test_logout_missing_token(self, db_session):
        """Test logout without token."""
        no_auth_headers = {
            'Content-Type': 'application/json'
        }
        
        response = self.post('/api/auth/logout', headers=no_auth_headers)
        
        self.assert_response_unauthorized(response)
        data = self.get_json_response(response)
        
        assert 'error' in data
        assert 'token' in data['error'].lower()
    
    def test_get_profile_success(self, db_session, sample_user):
        """Test getting user profile successfully."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': str(sample_user.id), 'user_type': 'USER'}
            
            response = self.get('/api/auth/profile', headers=self.auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'user' in data
            assert data['user']['id'] == str(sample_user.id)
            assert data['user']['username'] == sample_user.username
            assert data['user']['email'] == sample_user.email
            assert data['user']['phone'] == sample_user.phone
    
    def test_get_profile_invalid_token(self, db_session):
        """Test getting profile with invalid token."""
        invalid_headers = {
            'Authorization': 'Bearer invalid_token',
            'Content-Type': 'application/json'
        }
        
        response = self.get('/api/auth/profile', headers=invalid_headers)
        
        self.assert_response_unauthorized(response)
        data = self.get_json_response(response)
        
        assert 'error' in data
        assert 'token' in data['error'].lower()
    
    def test_get_profile_missing_token(self, db_session):
        """Test getting profile without token."""
        no_auth_headers = {
            'Content-Type': 'application/json'
        }
        
        response = self.get('/api/auth/profile', headers=no_auth_headers)
        
        self.assert_response_unauthorized(response)
        data = self.get_json_response(response)
        
        assert 'error' in data
        assert 'token' in data['error'].lower()
    
    def test_update_profile_success(self, db_session, sample_user):
        """Test updating user profile successfully."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': str(sample_user.id), 'user_type': 'USER'}
            
            update_data = {
                'name': 'Updated Name',
                'language': 'ARABIC'
            }
            
            response = self.put('/api/auth/profile', json_data=update_data, headers=self.auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'user' in data
            assert data['user']['name'] == 'Updated Name'
            assert data['user']['language'] == 'ARABIC'
    
    def test_update_profile_invalid_data(self, db_session, sample_user):
        """Test updating profile with invalid data."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': str(sample_user.id), 'user_type': 'USER'}
            
            update_data = {
                'email': 'invalid-email'  # Invalid email format
            }
            
            response = self.put('/api/auth/profile', json_data=update_data, headers=self.auth_headers)
            
            self.assert_response_error(response, 400)
            data = self.get_json_response(response)
            
            assert 'error' in data
            assert 'validation' in data['error']
    
    def test_change_password_success(self, db_session, sample_user):
        """Test changing password successfully."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': str(sample_user.id), 'user_type': 'USER'}
            
            password_data = {
                'current_password': 'testpassword',
                'new_password': 'newpassword123'
            }
            
            response = self.post('/api/auth/change-password', json_data=password_data, headers=self.auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'message' in data
            assert 'successfully' in data['message'].lower()
    
    def test_change_password_wrong_current(self, db_session, sample_user):
        """Test changing password with wrong current password."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': str(sample_user.id), 'user_type': 'USER'}
            
            password_data = {
                'current_password': 'wrongpassword',
                'new_password': 'newpassword123'
            }
            
            response = self.post('/api/auth/change-password', json_data=password_data, headers=self.auth_headers)
            
            self.assert_response_error(response, 400)
            data = self.get_json_response(response)
            
            assert 'error' in data
            assert 'current password' in data['error'].lower()
    
    def test_change_password_weak_new(self, db_session, sample_user):
        """Test changing password with weak new password."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': str(sample_user.id), 'user_type': 'USER'}
            
            password_data = {
                'current_password': 'testpassword',
                'new_password': '123'  # Too weak
            }
            
            response = self.post('/api/auth/change-password', json_data=password_data, headers=self.auth_headers)
            
            self.assert_response_error(response, 400)
            data = self.get_json_response(response)
            
            assert 'error' in data
            assert 'password' in data['error'].lower()
    
    def test_refresh_token_success(self, db_session, sample_user):
        """Test refreshing token successfully."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': str(sample_user.id), 'user_type': 'USER'}
            
            with patch('jwt.encode') as mock_jwt_encode:
                mock_jwt_encode.return_value = 'new_token'
                
                response = self.post('/api/auth/refresh', headers=self.auth_headers)
                
                self.assert_response_success(response)
                data = self.get_json_response(response)
                
                assert 'token' in data
                assert data['token'] == 'new_token'
    
    def test_refresh_token_invalid(self, db_session):
        """Test refreshing token with invalid token."""
        invalid_headers = {
            'Authorization': 'Bearer invalid_token',
            'Content-Type': 'application/json'
        }
        
        response = self.post('/api/auth/refresh', headers=invalid_headers)
        
        self.assert_response_unauthorized(response)
        data = self.get_json_response(response)
        
        assert 'error' in data
        assert 'token' in data['error'].lower()
    
    def test_forgot_password_success(self, db_session, sample_user):
        """Test forgot password successfully."""
        with patch('app.users.service.UserService.send_password_reset_email') as mock_send_email:
            mock_send_email.return_value = True
            
            forgot_data = {
                'email': sample_user.email
            }
            
            response = self.post('/api/auth/forgot-password', json_data=forgot_data)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'message' in data
            assert 'sent' in data['message'].lower()
    
    def test_forgot_password_invalid_email(self, db_session):
        """Test forgot password with invalid email."""
        forgot_data = {
            'email': 'nonexistent@example.com'
        }
        
        response = self.post('/api/auth/forgot-password', json_data=forgot_data)
        
        self.assert_response_error(response, 404)
        data = self.get_json_response(response)
        
        assert 'error' in data
        assert 'not found' in data['error'].lower()
    
    def test_reset_password_success(self, db_session, sample_user):
        """Test resetting password successfully."""
        with patch('app.users.service.UserService.verify_password_reset_token') as mock_verify:
            mock_verify.return_value = sample_user
            
            reset_data = {
                'token': 'valid_reset_token',
                'new_password': 'newpassword123'
            }
            
            response = self.post('/api/auth/reset-password', json_data=reset_data)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'message' in data
            assert 'successfully' in data['message'].lower()
    
    def test_reset_password_invalid_token(self, db_session):
        """Test resetting password with invalid token."""
        with patch('app.users.service.UserService.verify_password_reset_token') as mock_verify:
            mock_verify.return_value = None
            
            reset_data = {
                'token': 'invalid_reset_token',
                'new_password': 'newpassword123'
            }
            
            response = self.post('/api/auth/reset-password', json_data=reset_data)
            
            self.assert_response_error(response, 400)
            data = self.get_json_response(response)
            
            assert 'error' in data
            assert 'invalid' in data['error'].lower()
    
    def test_verify_email_success(self, db_session, sample_user):
        """Test verifying email successfully."""
        with patch('app.users.service.UserService.verify_email_token') as mock_verify:
            mock_verify.return_value = sample_user
            
            verify_data = {
                'token': 'valid_verify_token'
            }
            
            response = self.post('/api/auth/verify-email', json_data=verify_data)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'message' in data
            assert 'verified' in data['message'].lower()
    
    def test_verify_email_invalid_token(self, db_session):
        """Test verifying email with invalid token."""
        with patch('app.users.service.UserService.verify_email_token') as mock_verify:
            mock_verify.return_value = None
            
            verify_data = {
                'token': 'invalid_verify_token'
            }
            
            response = self.post('/api/auth/verify-email', json_data=verify_data)
            
            self.assert_response_error(response, 400)
            data = self.get_json_response(response)
            
            assert 'error' in data
            assert 'invalid' in data['error'].lower()
    
    def test_resend_verification_success(self, db_session, sample_user):
        """Test resending verification email successfully."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': str(sample_user.id), 'user_type': 'USER'}
            
            with patch('app.users.service.UserService.send_verification_email') as mock_send_email:
                mock_send_email.return_value = True
                
                response = self.post('/api/auth/resend-verification', headers=self.auth_headers)
                
                self.assert_response_success(response)
                data = self.get_json_response(response)
                
                assert 'message' in data
                assert 'sent' in data['message'].lower()
    
    def test_resend_verification_invalid_token(self, db_session):
        """Test resending verification with invalid token."""
        invalid_headers = {
            'Authorization': 'Bearer invalid_token',
            'Content-Type': 'application/json'
        }
        
        response = self.post('/api/auth/resend-verification', headers=invalid_headers)
        
        self.assert_response_unauthorized(response)
        data = self.get_json_response(response)
        
        assert 'error' in data
        assert 'token' in data['error'].lower()
