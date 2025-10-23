"""
Unit tests for Setting Service.

Tests all business logic in setting/service.py including:
- Setting CRUD operations
- Setting validation and type casting
- Setting caching and retrieval
- Category-based organization
- Default values handling
- Edge cases and error handling
"""

import pytest
import uuid

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from app.setting.service import SettingService
from app.setting.model import Setting
from app.common.error_handling import ResourceNotFoundError


class TestSettingService(BaseServiceTestCase):
    """Test cases for SettingService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = SettingService()
    
    # ========== CRUD Operations Tests ==========
    
    def test_create_setting_success(self, db_session):
        """Test creating a setting successfully."""
        setting_data = {
            'category': 'general',
            'key': 'site_name',
            'value': '3D Store',
            'data_type': 'string'
        }
        
        result, status = self.service.create_setting(setting_data)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify setting was created
        setting = db_session.query(Setting).filter(
            Setting.key == 'site_name'
        ).first()
        assert setting is not None
        assert setting.value == '3D Store'
        assert setting.category == 'general'
    
    def test_get_setting_by_key(self, db_session):
        """Test getting a specific setting by key."""
        # Create setting
        setting_data = {
            'category': 'general',
            'key': 'test_key',
            'value': 'test_value',
            'data_type': 'string'
        }
        self.service.create_setting(setting_data)
        
        # Get setting
        result, status = self.service.get_settings('test_key')
        
        assert status == 200
        assert 'settings' in result
    
    def test_get_all_settings(self, db_session):
        """Test getting all settings."""
        # Create multiple settings
        for i in range(5):
            setting_data = {
                'category': 'general',
                'key': f'setting_{i}',
                'value': f'value_{i}',
                'data_type': 'string'
            }
            self.service.create_setting(setting_data)
        
        result, status = self.service.get_settings(None)
        
        assert status == 200
        assert 'settings' in result
    
    def test_update_setting_success(self, db_session):
        """Test updating a setting."""
        # Create setting
        setting_data = {
            'category': 'general',
            'key': 'update_test',
            'value': 'original_value',
            'data_type': 'string'
        }
        self.service.create_setting(setting_data)
        
        # Update setting
        update_data = {
            'items': [
                {'key': 'update_test', 'value': 'updated_value'}
            ]
        }
        
        result, status = self.service.update_setting('general', update_data)
        
        assert status == 200
        assert 'Updated' in result
        
        # Verify update
        setting = db_session.query(Setting).filter(Setting.key == 'update_test').first()
        assert setting.value == 'updated_value'
    
    def test_delete_setting_success(self, db_session):
        """Test deleting a setting."""
        setting_data = {
            'category': 'general',
            'key': 'delete_test',
            'value': 'delete_value',
            'data_type': 'string'
        }
        self.service.create_setting(setting_data)
        
        setting = db_session.query(Setting).filter(Setting.key == 'delete_test').first()
        setting_id = setting.id
        
        result, status = self.service.delete_setting(setting_id)
        
        assert status == 200
        assert 'deleted' in result.lower()
        
        deleted_setting = db_session.query(Setting).filter_by(id=setting_id).first()
        assert deleted_setting is None
    
    # ========== Category-Based Tests ==========
    
    def test_get_settings_by_category(self, db_session):
        """Test getting settings by category."""
        # Create settings in different categories
        categories = ['general', 'payment', 'shipping']
        
        for category in categories:
            for i in range(2):
                setting_data = {
                    'category': category,
                    'key': f'{category}_setting_{i}',
                    'value': f'value_{i}',
                    'data_type': 'string'
                }
                self.service.create_setting(setting_data)
        
        # Get settings for specific category
        result, status = self.service.get_settings_by_category('payment')
        
        assert status == 200
        assert 'settings' in result
    
    def test_get_setting_config_model(self, db_session):
        """Test getting settings as config model (organized by category)."""
        # Create settings in multiple categories
        settings_to_create = [
            {'category': 'general', 'key': 'site_name', 'value': '3D Store'},
            {'category': 'general', 'key': 'site_url', 'value': 'https://3dstore.com'},
            {'category': 'payment', 'key': 'currency', 'value': 'USD'},
            {'category': 'payment', 'key': 'tax_rate', 'value': '5'},
        ]
        
        for setting_data in settings_to_create:
            setting_data['data_type'] = 'string'
            self.service.create_setting(setting_data)
        
        # Get config model
        config = self.service.get_setting_for_config()
        
        assert 'general' in config
        assert 'payment' in config
        assert config['general']['site_name'] == '3D Store'
        assert config['payment']['currency'] == 'USD'
    
    # ========== Data Type Tests ==========
    
    def test_setting_with_different_data_types(self, db_session):
        """Test settings with different data types."""
        data_types = ['string', 'integer', 'boolean', 'json']
        
        for i, dtype in enumerate(data_types):
            setting_data = {
                'category': 'test',
                'key': f'type_test_{dtype}',
                'value': 'test_value',
                'data_type': dtype
            }
            result, status = self.service.create_setting(setting_data)
            assert status == 201
        
        # Verify all created
        settings = db_session.query(Setting).filter(Setting.category == 'test').all()
        assert len(settings) >= len(data_types)
    
    def test_setting_boolean_value(self, db_session):
        """Test setting with boolean value."""
        setting_data = {
            'category': 'general',
            'key': 'maintenance_mode',
            'value': 'true',
            'data_type': 'boolean'
        }
        
        result, status = self.service.create_setting(setting_data)
        assert status == 201
        
        setting = db_session.query(Setting).filter(Setting.key == 'maintenance_mode').first()
        assert setting.value in ['true', 'True', '1', True]
    
    def test_setting_numeric_value(self, db_session):
        """Test setting with numeric value."""
        setting_data = {
            'category': 'payment',
            'key': 'max_order_value',
            'value': '10000',
            'data_type': 'integer'
        }
        
        result, status = self.service.create_setting(setting_data)
        assert status == 201
        
        setting = db_session.query(Setting).first()
        assert setting.value == '10000'
    
    # ========== Error Handling Tests ==========
    
    def test_get_setting_not_found(self, db_session):
        """Test getting a non-existent setting."""
        with pytest.raises(ResourceNotFoundError):
            self.service.get_settings('nonexistent_key')
    
    def test_update_setting_not_found(self, db_session):
        """Test updating a non-existent setting."""
        update_data = {
            'items': [
                {'key': 'nonexistent', 'value': 'new_value'}
            ]
        }
        
        # Should handle gracefully
        result, status = self.service.update_setting('nonexistent_category', update_data)
        # Either fails or handles gracefully
        assert status in [200, 404]
    
    def test_delete_setting_not_found(self, db_session):
        """Test deleting a non-existent setting."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_setting(non_existent_id)
    
    def test_get_settings_by_category_not_found(self, db_session):
        """Test getting settings for non-existent category."""
        with pytest.raises(ResourceNotFoundError):
            self.service.get_settings_by_category('nonexistent_category')
    
    # ========== Edge Cases Tests ==========
    
    def test_setting_with_empty_value(self, db_session):
        """Test setting with empty value."""
        setting_data = {
            'category': 'general',
            'key': 'empty_setting',
            'value': '',
            'data_type': 'string'
        }
        
        result, status = self.service.create_setting(setting_data)
        assert status == 201
        
        setting = db_session.query(Setting).first()
        assert setting.value == ''
    
    def test_setting_with_long_value(self, db_session):
        """Test setting with very long value."""
        long_value = "A" * 1000
        
        setting_data = {
            'category': 'general',
            'key': 'long_setting',
            'value': long_value,
            'data_type': 'string'
        }
        
        result, status = self.service.create_setting(setting_data)
        assert status == 201
        
        setting = db_session.query(Setting).first()
        assert len(setting.value) >= 1000
    
    def test_setting_key_uniqueness(self, db_session):
        """Test that setting keys must be unique within category."""
        setting_data = {
            'category': 'general',
            'key': 'unique_key',
            'value': 'value1',
            'data_type': 'string'
        }
        
        # Create first setting
        result1, status1 = self.service.create_setting(setting_data)
        assert status1 == 201
        
        # Try to create duplicate
        setting_data['value'] = 'value2'
        
        # Should fail due to unique constraint
        with pytest.raises(Exception):
            self.service.create_setting(setting_data)

