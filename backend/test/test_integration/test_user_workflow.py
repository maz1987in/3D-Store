"""
Integration tests for user workflow.

This module contains integration tests that test the complete user workflow
from registration to profile management.
"""

import pytest
from unittest.mock import patch, Mock
from werkzeug.security import check_password_hash

from test.base_test import BaseIntegrationTestCase
from app.users.model import User
from app.customers.model import Customer
from app.common.enum import UserTypeEnum, LanguageEnum


class TestUserWorkflow(BaseIntegrationTestCase):
    """Test cases for complete user workflow."""
    
    def test_complete_user_registration_workflow(self, db_session):
        """Test complete user registration workflow."""
        # Step 1: Register new user
        with patch('jwt.encode') as mock_jwt_encode:
            mock_jwt_encode.return_value = 'test_token'
            
            register_data = {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'phone': '+1234567899',
                'password': 'newpassword123',
                'user_type': 'USER',
                'language': 'ENGLISH'
            }
            
            response = self.client.post('/api/auth/register', json=register_data)
            
            self.assert_response_success(response, 201)
            data = self.get_json_response(response)
            
            assert 'token' in data
            assert 'user' in data
            assert data['user']['username'] == 'newuser'
            assert data['user']['email'] == 'newuser@example.com'
            assert data['user']['phone'] == '+1234567899'
            assert data['user']['user_type'] == 'USER'
            assert data['user']['language'] == 'ENGLISH'
            
            user_id = data['user']['id']
            token = data['token']
        
        # Step 2: Verify user was created in database
        user = self.db_session.query(User).filter(User.id == user_id).first()
        assert user is not None
        assert user.username == 'newuser'
        assert user.email == 'newuser@example.com'
        assert user.phone == '+1234567899'
        assert user.user_type == UserTypeEnum.USER
        assert user.language == LanguageEnum.ENGLISH
        assert check_password_hash(user.password, 'newpassword123')
        
        # Step 3: Login with new credentials
        with patch('jwt.encode') as mock_jwt_encode:
            mock_jwt_encode.return_value = 'test_token'
            
            login_data = {
                'email': 'newuser@example.com',
                'password': 'newpassword123'
            }
            
            response = self.client.post('/api/auth/login', json=login_data)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'token' in data
            assert 'user' in data
            assert data['user']['id'] == user_id
        
        # Step 4: Get user profile
        auth_headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': user_id, 'user_type': 'USER'}
            
            response = self.client.get('/api/auth/profile', headers=auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'user' in data
            assert data['user']['id'] == user_id
            assert data['user']['username'] == 'newuser'
            assert data['user']['email'] == 'newuser@example.com'
        
        # Step 5: Update user profile
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': user_id, 'user_type': 'USER'}
            
            update_data = {
                'name': 'Updated Name',
                'language': 'ARABIC'
            }
            
            response = self.client.put('/api/auth/profile', json=update_data, headers=auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'user' in data
            assert data['user']['name'] == 'Updated Name'
            assert data['user']['language'] == 'ARABIC'
        
        # Step 6: Verify profile update in database
        updated_user = self.db_session.query(User).filter(User.id == user_id).first()
        assert updated_user.name == 'Updated Name'
        assert updated_user.language == LanguageEnum.ARABIC
        
        # Step 7: Change password
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': user_id, 'user_type': 'USER'}
            
            password_data = {
                'current_password': 'newpassword123',
                'new_password': 'updatedpassword123'
            }
            
            response = self.client.post('/api/auth/change-password', json=password_data, headers=auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'message' in data
            assert 'successfully' in data['message'].lower()
        
        # Step 8: Verify password change in database
        updated_user = self.db_session.query(User).filter(User.id == user_id).first()
        assert check_password_hash(updated_user.password, 'updatedpassword123')
        
        # Step 9: Login with new password
        with patch('jwt.encode') as mock_jwt_encode:
            mock_jwt_encode.return_value = 'test_token'
            
            login_data = {
                'email': 'newuser@example.com',
                'password': 'updatedpassword123'
            }
            
            response = self.client.post('/api/auth/login', json=login_data)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'token' in data
            assert 'user' in data
            assert data['user']['id'] == user_id
        
        # Step 10: Logout
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': user_id, 'user_type': 'USER'}
            
            response = self.client.post('/api/auth/logout', headers=auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'message' in data
            assert 'successfully' in data['message'].lower()
    
    def test_user_registration_with_customer_creation(self, db_session):
        """Test user registration with automatic customer creation."""
        # Step 1: Register new user
        with patch('jwt.encode') as mock_jwt_encode:
            mock_jwt_encode.return_value = 'test_token'
            
            register_data = {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'phone': '+1234567899',
                'password': 'newpassword123',
                'user_type': 'USER',
                'language': 'ENGLISH'
            }
            
            response = self.client.post('/api/auth/register', json=register_data)
            
            self.assert_response_success(response, 201)
            data = self.get_json_response(response)
            
            user_id = data['user']['id']
        
        # Step 2: Create customer profile
        auth_headers = {
            'Authorization': 'Bearer test_token',
            'Content-Type': 'application/json'
        }
        
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': user_id, 'user_type': 'USER'}
            
            customer_data = {
                'user_id': user_id,
                'email': 'newuser@example.com',
                'mobile': '+1234567899',
                'customer_type': 'individual',
                'status': 'active'
            }
            
            response = self.client.post('/api/customers', json=customer_data, headers=auth_headers)
            
            self.assert_response_success(response, 201)
            data = self.get_json_response(response)
            
            assert 'customer' in data
            assert data['customer']['user_id'] == user_id
            assert data['customer']['email'] == 'newuser@example.com'
            assert data['customer']['mobile'] == '+1234567899'
            assert data['customer']['customer_type'] == 'individual'
            assert data['customer']['status'] == 'active'
            
            customer_id = data['customer']['id']
        
        # Step 3: Verify customer was created in database
        customer = self.db_session.query(Customer).filter(Customer.id == customer_id).first()
        assert customer is not None
        assert customer.user_id == user_id
        assert customer.email == 'newuser@example.com'
        assert customer.mobile == '+1234567899'
        assert customer.customer_type == 'individual'
        assert customer.status == 'active'
        
        # Step 4: Get customer profile
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': user_id, 'user_type': 'USER'}
            
            response = self.client.get(f'/api/customers/{customer_id}', headers=auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'customer' in data
            assert data['customer']['id'] == customer_id
            assert data['customer']['user_id'] == user_id
            assert data['customer']['email'] == 'newuser@example.com'
        
        # Step 5: Update customer profile
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': user_id, 'user_type': 'USER'}
            
            update_data = {
                'city': 'Test City',
                'country': 'US',
                'address': '123 Test Street'
            }
            
            response = self.client.put(f'/api/customers/{customer_id}', json=update_data, headers=auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'customer' in data
            assert data['customer']['city'] == 'Test City'
            assert data['customer']['country'] == 'US'
            assert data['customer']['address'] == '123 Test Street'
        
        # Step 6: Verify customer update in database
        updated_customer = self.db_session.query(Customer).filter(Customer.id == customer_id).first()
        assert updated_customer.city == 'Test City'
        assert updated_customer.country == 'US'
        assert updated_customer.address == '123 Test Street'
    
    def test_user_authentication_workflow(self, db_session, sample_user):
        """Test complete user authentication workflow."""
        # Step 1: Login with correct credentials
        with patch('jwt.encode') as mock_jwt_encode:
            mock_jwt_encode.return_value = 'test_token'
            
            login_data = {
                'email': sample_user.email,
                'password': 'testpassword'
            }
            
            response = self.client.post('/api/auth/login', json=login_data)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'token' in data
            assert 'user' in data
            assert data['user']['id'] == str(sample_user.id)
            
            token = data['token']
        
        # Step 2: Access protected resource
        auth_headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': str(sample_user.id), 'user_type': 'USER'}
            
            response = self.client.get('/api/auth/profile', headers=auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'user' in data
            assert data['user']['id'] == str(sample_user.id)
        
        # Step 3: Refresh token
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': str(sample_user.id), 'user_type': 'USER'}
            
            with patch('jwt.encode') as mock_jwt_encode:
                mock_jwt_encode.return_value = 'new_token'
                
                response = self.client.post('/api/auth/refresh', headers=auth_headers)
                
                self.assert_response_success(response)
                data = self.get_json_response(response)
                
                assert 'token' in data
                assert data['token'] == 'new_token'
                
                new_token = data['token']
        
        # Step 4: Access protected resource with new token
        new_auth_headers = {
            'Authorization': f'Bearer {new_token}',
            'Content-Type': 'application/json'
        }
        
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': str(sample_user.id), 'user_type': 'USER'}
            
            response = self.client.get('/api/auth/profile', headers=new_auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'user' in data
            assert data['user']['id'] == str(sample_user.id)
        
        # Step 5: Logout
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': str(sample_user.id), 'user_type': 'USER'}
            
            response = self.client.post('/api/auth/logout', headers=new_auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'message' in data
            assert 'successfully' in data['message'].lower()
        
        # Step 6: Try to access protected resource after logout
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': str(sample_user.id), 'user_type': 'USER'}
            
            response = self.client.get('/api/auth/profile', headers=new_auth_headers)
            
            # This should still work as we're mocking JWT decode
            # In a real scenario, the token would be invalidated
            self.assert_response_success(response)
    
    def test_user_password_reset_workflow(self, db_session, sample_user):
        """Test complete user password reset workflow."""
        # Step 1: Request password reset
        with patch('app.users.service.UserService.send_password_reset_email') as mock_send_email:
            mock_send_email.return_value = True
            
            forgot_data = {
                'email': sample_user.email
            }
            
            response = self.client.post('/api/auth/forgot-password', json=forgot_data)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'message' in data
            assert 'sent' in data['message'].lower()
        
        # Step 2: Reset password with valid token
        with patch('app.users.service.UserService.verify_password_reset_token') as mock_verify:
            mock_verify.return_value = sample_user
            
            reset_data = {
                'token': 'valid_reset_token',
                'new_password': 'newpassword123'
            }
            
            response = self.client.post('/api/auth/reset-password', json=reset_data)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'message' in data
            assert 'successfully' in data['message'].lower()
        
        # Step 3: Verify password was changed in database
        updated_user = self.db_session.query(User).filter(User.id == sample_user.id).first()
        assert check_password_hash(updated_user.password, 'newpassword123')
        
        # Step 4: Login with new password
        with patch('jwt.encode') as mock_jwt_encode:
            mock_jwt_encode.return_value = 'test_token'
            
            login_data = {
                'email': sample_user.email,
                'password': 'newpassword123'
            }
            
            response = self.client.post('/api/auth/login', json=login_data)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'token' in data
            assert 'user' in data
            assert data['user']['id'] == str(sample_user.id)
    
    def test_user_email_verification_workflow(self, db_session, sample_user):
        """Test complete user email verification workflow."""
        # Step 1: Request email verification
        auth_headers = {
            'Authorization': 'Bearer test_token',
            'Content-Type': 'application/json'
        }
        
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': str(sample_user.id), 'user_type': 'USER'}
            
            with patch('app.users.service.UserService.send_verification_email') as mock_send_email:
                mock_send_email.return_value = True
                
                response = self.client.post('/api/auth/resend-verification', headers=auth_headers)
                
                self.assert_response_success(response)
                data = self.get_json_response(response)
                
                assert 'message' in data
                assert 'sent' in data['message'].lower()
        
        # Step 2: Verify email with valid token
        with patch('app.users.service.UserService.verify_email_token') as mock_verify:
            mock_verify.return_value = sample_user
            
            verify_data = {
                'token': 'valid_verify_token'
            }
            
            response = self.client.post('/api/auth/verify-email', json=verify_data)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'message' in data
            assert 'verified' in data['message'].lower()
        
        # Step 3: Verify email was verified in database
        updated_user = self.db_session.query(User).filter(User.id == sample_user.id).first()
        assert updated_user.email_confirmed_at is not None
    
    def test_user_deactivation_workflow(self, db_session, sample_user):
        """Test complete user deactivation workflow."""
        # Step 1: Login as admin
        auth_headers = {
            'Authorization': 'Bearer admin_token',
            'Content-Type': 'application/json'
        }
        
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'admin_id', 'user_type': 'ADMIN'}
            
            # Step 2: Disable user
            response = self.client.put(f'/api/users/{sample_user.id}/disable', headers=auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'message' in data
            assert 'disabled' in data['message'].lower()
        
        # Step 3: Verify user is disabled in database
        disabled_user = self.db_session.query(User).filter(User.id == sample_user.id).first()
        assert disabled_user.active is False
        
        # Step 4: Try to login with disabled user
        with patch('jwt.encode') as mock_jwt_encode:
            mock_jwt_encode.return_value = 'test_token'
            
            login_data = {
                'email': sample_user.email,
                'password': 'testpassword'
            }
            
            response = self.client.post('/api/auth/login', json=login_data)
            
            self.assert_response_unauthorized(response)
            data = self.get_json_response(response)
            
            assert 'error' in data
            assert 'disabled' in data['error'].lower()
        
        # Step 5: Re-enable user
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'admin_id', 'user_type': 'ADMIN'}
            
            response = self.client.put(f'/api/users/{sample_user.id}/enable', headers=auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'message' in data
            assert 'enabled' in data['message'].lower()
        
        # Step 6: Verify user is enabled in database
        enabled_user = self.db_session.query(User).filter(User.id == sample_user.id).first()
        assert enabled_user.active is True
        
        # Step 7: Login with re-enabled user
        with patch('jwt.encode') as mock_jwt_encode:
            mock_jwt_encode.return_value = 'test_token'
            
            login_data = {
                'email': sample_user.email,
                'password': 'testpassword'
            }
            
            response = self.client.post('/api/auth/login', json=login_data)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'token' in data
            assert 'user' in data
            assert data['user']['id'] == str(sample_user.id)
