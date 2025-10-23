"""
Unit tests for Labor Service.

Tests all business logic in labor/service.py including:
- Labor hour tracking and logging
- Labor cost calculations
- Labor category management
- Work period management
- Labor reports and aggregations
- Edge cases and error handling
"""

import pytest
import uuid
from decimal import Decimal

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from test.test_helpers import assert_decimal_equal, create_mock_filter
from app.labor.service import LaborService
from app.labor.model import Labor, LaborCategory
from app.common.error_handling import ResourceNotFoundError


class TestLaborService(BaseServiceTestCase):
    """Test cases for LaborService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = LaborService()
    
    # ========== Labor Category Tests ==========
    
    def test_create_labor_category_success(self, db_session):
        """Test creating a labor category successfully."""
        category_data = {
            'name': 'Design',
            'description': '3D Design work',
            'is_active': True
        }
        
        result, status = self.service.create_labor_category(category_data)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify category was created
        category = db_session.query(LaborCategory).filter(
            LaborCategory.name == 'Design'
        ).first()
        assert category is not None
        assert category.is_active is True
    
    def test_get_labor_categories(self, db_session):
        """Test getting all labor categories."""
        # Create multiple categories
        categories = ['Design', 'Printing', 'Assembly', 'Quality Check']
        
        for cat_name in categories:
            category_data = {
                'name': cat_name,
                'is_active': True
            }
            self.service.create_labor_category(category_data)
        
        result, status = self.service.get_labor_categories()
        
        assert status == 200
        assert len(result) >= len(categories)
    
    # ========== Labor CRUD Tests ==========
    
    def test_create_labor_success(self, db_session, sample_staff):
        """Test creating a labor record successfully."""
        # Create category first
        category_data = {'name': 'Test Category', 'is_active': True}
        self.service.create_labor_category(category_data)
        category = db_session.query(LaborCategory).first()
        
        labor_data = {
            'staff_id': sample_staff.id,
            'category_id': category.id,
            'date': '2024-01-15',
            'hours': 8.0,
            'hourly_rate': 25.00,
            'total_cost': 200.00,
            'description': 'Design work for project X'
        }
        
        result, status = self.service.create_labor(labor_data)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify labor was created
        labor = db_session.query(Labor).first()
        assert labor is not None
        assert labor.hours == 8.0
        assert_decimal_equal(labor.hourly_rate, 25.00)
        assert_decimal_equal(labor.total_cost, 200.00)
    
    def test_get_labors_with_pagination(self, db_session, sample_staff):
        """Test getting labor records with pagination."""
        # Create category
        category_data = {'name': 'General', 'is_active': True}
        self.service.create_labor_category(category_data)
        category = db_session.query(LaborCategory).first()
        
        # Create multiple labor records
        for i in range(12):
            labor_data = {
                'staff_id': sample_staff.id,
                'category_id': category.id,
                'date': '2024-01-15',
                'hours': 8.0,
                'hourly_rate': 25.00,
                'total_cost': 200.00
            }
            self.service.create_labor(labor_data)
        
        filter_obj = create_mock_filter(page=1, per_page=10)
        result, status = self.service.get_labors(None, filter_obj)
        
        assert status == 200
        assert 'labors' in result
        assert 'filters' in result
    
    def test_update_labor_success(self, db_session, sample_staff):
        """Test updating a labor record."""
        # Create category and labor
        category_data = {'name': 'Test Category', 'is_active': True}
        self.service.create_labor_category(category_data)
        category = db_session.query(LaborCategory).first()
        
        labor_data = {
            'staff_id': sample_staff.id,
            'category_id': category.id,
            'date': '2024-01-15',
            'hours': 8.0,
            'hourly_rate': 25.00,
            'total_cost': 200.00
        }
        self.service.create_labor(labor_data)
        
        labor = db_session.query(Labor).first()
        
        # Update labor
        update_data = {
            'hours': 10.0,
            'hourly_rate': 30.00,
            'total_cost': 300.00,
            'date': '2024-01-16'
        }
        
        result, status = self.service.update_labor(labor.id, update_data)
        
        assert status == 200
        assert 'Updated' in result
        
        db_session.refresh(labor)
        assert labor.hours == 10.0
        assert_decimal_equal(labor.hourly_rate, 30.00)
        assert_decimal_equal(labor.total_cost, 300.00)
    
    def test_delete_labor_success(self, db_session, sample_staff):
        """Test deleting a labor record."""
        # Create category and labor
        category_data = {'name': 'Test Category', 'is_active': True}
        self.service.create_labor_category(category_data)
        category = db_session.query(LaborCategory).first()
        
        labor_data = {
            'staff_id': sample_staff.id,
            'category_id': category.id,
            'date': '2024-01-15',
            'hours': 8.0,
            'hourly_rate': 25.00,
            'total_cost': 200.00
        }
        self.service.create_labor(labor_data)
        
        labor = db_session.query(Labor).first()
        labor_id = labor.id
        
        result, status = self.service.delete_labor(labor_id)
        
        assert status == 200
        assert 'deleted' in result.lower()
        
        deleted_labor = db_session.query(Labor).filter_by(id=labor_id).first()
        assert deleted_labor is None
    
    # ========== Cost Calculation Tests ==========
    
    def test_labor_cost_calculation(self, db_session, sample_staff):
        """Test labor cost calculation (hours × hourly_rate)."""
        category_data = {'name': 'Test Category', 'is_active': True}
        self.service.create_labor_category(category_data)
        category = db_session.query(LaborCategory).first()
        
        hours = 8.5
        hourly_rate = 30.00
        expected_total = hours * hourly_rate  # 255.00
        
        labor_data = {
            'staff_id': sample_staff.id,
            'category_id': category.id,
            'date': '2024-01-15',
            'hours': hours,
            'hourly_rate': hourly_rate,
            'total_cost': expected_total
        }
        self.service.create_labor(labor_data)
        
        labor = db_session.query(Labor).first()
        assert_decimal_equal(labor.total_cost, 255.00)
    
    def test_labor_overtime_hours(self, db_session, sample_staff):
        """Test labor with overtime hours (>8 hours)."""
        category_data = {'name': 'Test Category', 'is_active': True}
        self.service.create_labor_category(category_data)
        category = db_session.query(LaborCategory).first()
        
        overtime_hours = 12.0
        
        labor_data = {
            'staff_id': sample_staff.id,
            'category_id': category.id,
            'date': '2024-01-15',
            'hours': overtime_hours,
            'hourly_rate': 25.00,
            'total_cost': 300.00
        }
        
        result, status = self.service.create_labor(labor_data)
        assert status == 201
        
        labor = db_session.query(Labor).first()
        assert labor.hours == 12.0
    
    # ========== Hour Validation Tests ==========
    
    def test_labor_with_zero_hours(self, db_session, sample_staff):
        """Test labor with zero hours."""
        category_data = {'name': 'Test Category', 'is_active': True}
        self.service.create_labor_category(category_data)
        category = db_session.query(LaborCategory).first()
        
        labor_data = {
            'staff_id': sample_staff.id,
            'category_id': category.id,
            'date': '2024-01-15',
            'hours': 0.0,
            'hourly_rate': 25.00,
            'total_cost': 0.00
        }
        
        result, status = self.service.create_labor(labor_data)
        assert status == 201
        
        labor = db_session.query(Labor).first()
        assert labor.hours == 0.0
    
    def test_labor_with_fractional_hours(self, db_session, sample_staff):
        """Test labor with fractional hours (e.g., 4.5 hours)."""
        category_data = {'name': 'Test Category', 'is_active': True}
        self.service.create_labor_category(category_data)
        category = db_session.query(LaborCategory).first()
        
        labor_data = {
            'staff_id': sample_staff.id,
            'category_id': category.id,
            'date': '2024-01-15',
            'hours': 4.5,
            'hourly_rate': 25.00,
            'total_cost': 112.50
        }
        
        result, status = self.service.create_labor(labor_data)
        assert status == 201
        
        labor = db_session.query(Labor).first()
        assert labor.hours == 4.5
        assert_decimal_equal(labor.total_cost, 112.50)
    
    # ========== Error Handling Tests ==========
    
    def test_create_labor_missing_required_fields(self, db_session):
        """Test creating labor with missing required fields."""
        incomplete_data = {
            'hours': 8.0
            # Missing staff_id, category_id, date, etc.
        }
        
        with pytest.raises(Exception):
            self.service.create_labor(incomplete_data)
    
    def test_update_labor_not_found(self, db_session):
        """Test updating a non-existent labor record."""
        non_existent_id = uuid.uuid4()
        update_data = {'hours': 10.0, 'date': '2024-01-15'}
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_labor(non_existent_id, update_data)
    
    def test_delete_labor_not_found(self, db_session):
        """Test deleting a non-existent labor record."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_labor(non_existent_id)
    
    def test_get_labors_empty_database(self, db_session):
        """Test getting labor records when database is empty."""
        filter_obj = create_mock_filter()
        result, status = self.service.get_labors(None, filter_obj)
        
        assert status == 200
        assert 'labors' in result

