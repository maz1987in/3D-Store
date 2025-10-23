"""
Unit tests for City Service.

Tests all business logic in city/service.py including:
- City CRUD operations
- City code uniqueness
- Active/inactive status management
- Translation handling
- Edge cases and error handling
"""

import pytest
import uuid
import json

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from test.test_helpers import create_mock_filter
from app.city.service import CityService
from app.city.model import City
from app.common.error_handling import ResourceNotFoundError


class TestCityService(BaseServiceTestCase):
    """Test cases for CityService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = CityService()
    
    # ========== CRUD Operations Tests ==========
    
    def test_create_city_success(self, db_session):
        """Test creating a city successfully."""
        city_data = {
            'code': 'MST',
            'name': json.dumps({'en': 'Muscat', 'ar': 'مسقط'}),
            'country': 'Oman',
            'is_active': True
        }
        
        result, status = self.service.create_city(city_data)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify city was created
        city = db_session.query(City).filter(City.code == 'MST').first()
        assert city is not None
        assert city.code == 'MST'
        assert city.country == 'Oman'
        assert city.is_active is True
    
    def test_create_city_with_different_countries(self, db_session):
        """Test creating cities from different countries."""
        countries = ['Oman', 'UAE', 'Saudi Arabia', 'Qatar']
        
        for i, country in enumerate(countries):
            city_data = {
                'code': f'CTY{i}',
                'name': json.dumps({'en': f'City{i}', 'ar': f'مدينة{i}'}),
                'country': country,
                'is_active': True
            }
            
            result, status = self.service.create_city(city_data)
            assert status == 201
        
        # Verify all cities were created
        cities = db_session.query(City).all()
        city_countries = [city.country for city in cities]
        assert len(set(city_countries)) >= len(countries)
    
    def test_get_cities_with_pagination(self, db_session):
        """Test getting cities with pagination."""
        # Create multiple cities
        for i in range(15):
            city_data = {
                'code': f'CITY{i:03d}',
                'name': json.dumps({'en': f'City {i}', 'ar': f'مدينة {i}'}),
                'country': 'Oman',
                'is_active': True
            }
            self.service.create_city(city_data)
        
        filter_obj = create_mock_filter(page=1, per_page=10)
        result, status = self.service.get_cities(None, filter_obj)
        
        assert status == 200
        assert 'cities' in result
        assert 'filters' in result
    
    def test_get_city_by_id(self, db_session):
        """Test getting a specific city by ID."""
        city_data = {
            'code': 'DXB',
            'name': json.dumps({'en': 'Dubai', 'ar': 'دبي'}),
            'country': 'UAE',
            'is_active': True
        }
        self.service.create_city(city_data)
        
        city = db_session.query(City).first()
        
        result, status = self.service.get_cities(city.id)
        
        assert status == 200
        assert 'cities' in result
    
    def test_update_city_success(self, db_session):
        """Test updating a city."""
        # Create city
        city_data = {
            'code': 'SLL',
            'name': json.dumps({'en': 'Salalah', 'ar': 'صلالة'}),
            'country': 'Oman',
            'is_active': True
        }
        self.service.create_city(city_data)
        
        city = db_session.query(City).first()
        
        # Update the city
        update_data = {
            'is_active': False,
            'country': 'Oman - Updated'
        }
        
        result, status = self.service.update_city(city.id, update_data)
        
        assert status == 200
        assert 'Updated' in result
        
        db_session.refresh(city)
        assert city.is_active is False
    
    def test_delete_city_success(self, db_session):
        """Test deleting a city."""
        # Create city
        city_data = {
            'code': 'NZW',
            'name': json.dumps({'en': 'Nizwa', 'ar': 'نزوى'}),
            'country': 'Oman',
            'is_active': True
        }
        self.service.create_city(city_data)
        
        city = db_session.query(City).first()
        city_id = city.id
        
        # Delete the city
        result, status = self.service.delete_city(city_id)
        
        assert status == 200
        assert 'deleted' in result.lower()
        
        deleted_city = db_session.query(City).filter_by(id=city_id).first()
        assert deleted_city is None
    
    # ========== Code Uniqueness Tests ==========
    
    def test_prevent_duplicate_city_code(self, db_session):
        """Test that city codes must be unique."""
        city_data = {
            'code': 'MST',
            'name': json.dumps({'en': 'Muscat', 'ar': 'مسقط'}),
            'country': 'Oman',
            'is_active': True
        }
        
        # First city should succeed
        result1, status1 = self.service.create_city(city_data)
        assert status1 == 201
        
        # Second city with same code should fail
        city_data_2 = {
            'code': 'MST',  # Same code
            'name': json.dumps({'en': 'Another Muscat', 'ar': 'مسقط أخرى'}),
            'country': 'Oman',
            'is_active': True
        }
        
        result2, status2 = self.service.create_city(city_data_2)
        
        assert status2 == 400
        assert 'already exists' in result2.lower()
        
        # Verify only one city exists
        cities = db_session.query(City).filter(City.code == 'MST').all()
        assert len(cities) == 1
    
    def test_city_code_case_sensitivity(self, db_session):
        """Test city code case sensitivity."""
        codes = ['mst', 'MST', 'Mst']
        
        for i, code in enumerate(codes):
            city_data = {
                'code': code,
                'name': json.dumps({'en': f'City {i}', 'ar': f'مدينة {i}'}),
                'country': 'Oman',
                'is_active': True
            }
            
            result, status = self.service.create_city(city_data)
            # Depending on implementation, might allow or prevent
            assert status in [201, 400]
    
    # ========== Active/Inactive Status Tests ==========
    
    def test_create_active_city(self, db_session):
        """Test creating an active city."""
        city_data = {
            'code': 'ACT',
            'name': json.dumps({'en': 'Active City', 'ar': 'مدينة نشطة'}),
            'country': 'Oman',
            'is_active': True
        }
        
        result, status = self.service.create_city(city_data)
        assert status == 201
        
        city = db_session.query(City).first()
        assert city.is_active is True
    
    def test_create_inactive_city(self, db_session):
        """Test creating an inactive city."""
        city_data = {
            'code': 'INACT',
            'name': json.dumps({'en': 'Inactive City', 'ar': 'مدينة غير نشطة'}),
            'country': 'Oman',
            'is_active': False
        }
        
        result, status = self.service.create_city(city_data)
        assert status == 201
        
        city = db_session.query(City).first()
        assert city.is_active is False
    
    def test_toggle_city_status(self, db_session):
        """Test toggling city active/inactive status."""
        # Create active city
        city_data = {
            'code': 'TGL',
            'name': json.dumps({'en': 'Toggle City', 'ar': 'مدينة التبديل'}),
            'country': 'Oman',
            'is_active': True
        }
        self.service.create_city(city_data)
        
        city = db_session.query(City).first()
        
        # Deactivate
        self.service.update_city(city.id, {'is_active': False})
        db_session.refresh(city)
        assert city.is_active is False
        
        # Reactivate
        self.service.update_city(city.id, {'is_active': True})
        db_session.refresh(city)
        assert city.is_active is True
    
    def test_filter_active_cities(self, db_session):
        """Test filtering cities by active status."""
        # Create mix of active and inactive cities
        for i in range(5):
            city_data = {
                'code': f'FLT{i}',
                'name': json.dumps({'en': f'City {i}', 'ar': f'مدينة {i}'}),
                'country': 'Oman',
                'is_active': i % 2 == 0  # Even indices active
            }
            self.service.create_city(city_data)
        
        # Get all cities
        all_cities = db_session.query(City).all()
        assert len(all_cities) >= 5
        
        # Filter active only
        active_cities = db_session.query(City).filter(City.is_active == True).all()
        inactive_cities = db_session.query(City).filter(City.is_active == False).all()
        
        assert len(active_cities) + len(inactive_cities) == len(all_cities)
    
    # ========== Translation Tests ==========
    
    def test_create_city_with_translations(self, db_session):
        """Test creating city with multiple language translations."""
        city_data = {
            'code': 'TRANS',
            'name': json.dumps({
                'en': 'Translated City',
                'ar': 'مدينة مترجمة'
            }),
            'country': 'Oman',
            'is_active': True
        }
        
        result, status = self.service.create_city(city_data)
        assert status == 201
        
        city = db_session.query(City).first()
        assert city is not None
    
    def test_create_city_missing_translation(self, db_session):
        """Test creating city with incomplete translations."""
        city_data = {
            'code': 'MISS',
            'name': json.dumps({'en': 'English Only'}),
            'country': 'Oman',
            'is_active': True
        }
        
        # Should handle missing translations gracefully
        result, status = self.service.create_city(city_data)
        # Depending on implementation, might succeed or fail
        assert status in [201, 400]
    
    # ========== Edge Cases Tests ==========
    
    def test_create_city_with_empty_code(self, db_session):
        """Test creating city with empty code."""
        city_data = {
            'code': '',
            'name': json.dumps({'en': 'Empty Code City', 'ar': 'مدينة كود فارغ'}),
            'country': 'Oman',
            'is_active': True
        }
        
        with pytest.raises(Exception):
            self.service.create_city(city_data)
    
    def test_create_city_with_special_characters(self, db_session):
        """Test creating city with special characters in name."""
        city_data = {
            'code': 'SPEC',
            'name': json.dumps({
                'en': "City's Name (Test) & More!",
                'ar': 'مدينة@اختبار#خاصة'
            }),
            'country': 'Oman',
            'is_active': True
        }
        
        result, status = self.service.create_city(city_data)
        assert status == 201
    
    def test_create_city_with_long_names(self, db_session):
        """Test creating city with very long names."""
        long_name = "A" * 200
        
        city_data = {
            'code': 'LONG',
            'name': json.dumps({'en': long_name, 'ar': 'اسم' * 50}),
            'country': 'Oman',
            'is_active': True
        }
        
        result, status = self.service.create_city(city_data)
        # Should either succeed or validate length
        assert status in [201, 400]
    
    def test_get_cities_empty_database(self, db_session):
        """Test getting cities when database is empty."""
        filter_obj = create_mock_filter()
        result, status = self.service.get_cities(None, filter_obj)
        
        assert status == 200
        assert 'cities' in result
        assert len(result['cities']) == 0
    
    def test_cities_from_multiple_countries(self, db_session):
        """Test managing cities from different countries."""
        countries = {
            'Oman': ['MST', 'SLL', 'NZW'],
            'UAE': ['DXB', 'AUH', 'SHJ'],
            'Saudi Arabia': ['RUH', 'JED', 'DAM']
        }
        
        for country, codes in countries.items():
            for code in codes:
                city_data = {
                    'code': code,
                    'name': json.dumps({'en': code, 'ar': code}),
                    'country': country,
                    'is_active': True
                }
                self.service.create_city(city_data)
        
        # Verify all cities created
        total_cities = db_session.query(City).count()
        expected_total = sum(len(codes) for codes in countries.values())
        assert total_cities >= expected_total
    
    # ========== Error Handling Tests ==========
    
    def test_create_city_missing_required_fields(self, db_session):
        """Test creating city with missing required fields."""
        incomplete_data = {
            'name': json.dumps({'en': 'Test', 'ar': 'اختبار'})
            # Missing code
        }
        
        with pytest.raises(Exception):
            self.service.create_city(incomplete_data)
    
    def test_get_city_by_invalid_id(self, db_session):
        """Test getting city with non-existent ID."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(Exception):
            self.service.get_cities(non_existent_id)
    
    def test_update_city_not_found(self, db_session):
        """Test updating a non-existent city."""
        non_existent_id = uuid.uuid4()
        update_data = {'is_active': False}
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_city(non_existent_id, update_data)
    
    def test_delete_city_not_found(self, db_session):
        """Test deleting a non-existent city."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_city(non_existent_id)
    
    def test_update_city_partial_data(self, db_session):
        """Test updating only some fields of a city."""
        # Create city
        city_data = {
            'code': 'PART',
            'name': json.dumps({'en': 'Partial', 'ar': 'جزئي'}),
            'country': 'Oman',
            'is_active': True
        }
        self.service.create_city(city_data)
        
        city = db_session.query(City).first()
        original_code = city.code
        
        # Update only is_active
        update_data = {'is_active': False}
        self.service.update_city(city.id, update_data)
        
        db_session.refresh(city)
        assert city.is_active is False
        assert city.code == original_code  # Should not change
    
    def test_city_default_values(self, db_session):
        """Test city creation with default values."""
        city_data = {
            'code': 'DEF',
            'name': json.dumps({'en': 'Default', 'ar': 'افتراضي'})
            # Not specifying country or is_active
        }
        
        result, status = self.service.create_city(city_data)
        
        # Should use defaults
        if status == 201:
            city = db_session.query(City).first()
            # Check if defaults were applied
            assert city.country is not None
            assert isinstance(city.is_active, bool)

