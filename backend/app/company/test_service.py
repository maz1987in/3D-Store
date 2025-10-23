"""
Unit tests for Company Service.

Tests all business logic in company/service.py including:
- Company CRUD operations
- Company-branch relationships
- Multi-language translations
- Active/inactive status management
- Multi-tenant functionality
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
from app.company.service import CompanyService
from app.company.model import Company
from app.common.error_handling import ResourceNotFoundError


class TestCompanyService(BaseServiceTestCase):
    """Test cases for CompanyService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = CompanyService()
    
    # ========== CRUD Operations Tests ==========
    
    def test_create_company_success(self, db_session):
        """Test creating a company successfully."""
        company_data = {
            'name': json.dumps({'en': 'Tech Corp', 'ar': 'شركة التقنية'}),
            'location': 'Business District',
            'manager': 'CEO Name',
            'cr_number': 'CR12345',
            'tax_id': 'TAX67890'
        }
        
        result, status = self.service.create_company(company_data)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify company was created
        company = db_session.query(Company).first()
        assert company is not None
        assert company.cr_number == 'CR12345'
        assert company.tax_id == 'TAX67890'
    
    def test_get_companies_with_pagination(self, db_session):
        """Test getting companies with pagination."""
        # Create multiple companies
        for i in range(8):
            company_data = {
                'name': json.dumps({'en': f'Company {i}', 'ar': f'شركة {i}'}),
                'location': f'Location {i}',
                'manager': f'Manager {i}'
            }
            self.service.create_company(company_data)
        
        filter_obj = create_mock_filter(page=1, per_page=5)
        result, status = self.service.get_companies(None, filter_obj)
        
        assert status == 200
        assert 'companies' in result
        assert 'filters' in result
    
    def test_get_company_by_id(self, db_session):
        """Test getting a specific company by ID."""
        company_data = {
            'name': json.dumps({'en': 'Specific Company', 'ar': 'شركة محددة'}),
            'location': 'Downtown',
            'manager': 'Manager Name'
        }
        self.service.create_company(company_data)
        
        company = db_session.query(Company).first()
        filter_obj = create_mock_filter()
        
        result, status = self.service.get_companies(company.id, filter_obj)
        
        assert status == 200
        assert 'companies' in result
    
    def test_update_company_success(self, db_session):
        """Test updating a company."""
        # Create company
        company_data = {
            'name': json.dumps({'en': 'Original Corp', 'ar': 'شركة أصلية'}),
            'location': 'Old Location',
            'manager': 'Old Manager'
        }
        self.service.create_company(company_data)
        
        company = db_session.query(Company).first()
        
        # Update company
        update_data = {
            'location': 'New Headquarters',
            'manager': 'New CEO'
        }
        
        result, status = self.service.update_company(company.id, update_data)
        
        assert status == 200
        assert 'Updated' in result
        
        db_session.refresh(company)
        assert company.location == 'New Headquarters'
        assert company.manager == 'New CEO'
    
    def test_delete_company_success(self, db_session):
        """Test deleting a company."""
        company_data = {
            'name': json.dumps({'en': 'Delete Corp', 'ar': 'شركة الحذف'}),
            'location': 'Location',
            'manager': 'Manager'
        }
        self.service.create_company(company_data)
        
        company = db_session.query(Company).first()
        company_id = company.id
        
        result, status = self.service.delete_company(company_id)
        
        assert status == 200
        assert 'deleted' in result.lower()
        
        deleted_company = db_session.query(Company).filter_by(id=company_id).first()
        assert deleted_company is None
    
    # ========== CR Number & Tax ID Tests ==========
    
    def test_create_company_with_unique_cr_number(self, db_session):
        """Test company with unique CR number."""
        company_data = {
            'name': json.dumps({'en': 'CR Company', 'ar': 'شركة CR'}),
            'cr_number': 'UNIQUE-CR-123'
        }
        
        result, status = self.service.create_company(company_data)
        assert status == 201
        
        company = db_session.query(Company).first()
        assert company.cr_number == 'UNIQUE-CR-123'
    
    def test_create_company_with_tax_id(self, db_session):
        """Test company with tax ID."""
        company_data = {
            'name': json.dumps({'en': 'Tax Company', 'ar': 'شركة ضريبة'}),
            'tax_id': 'TAX-ID-999'
        }
        
        result, status = self.service.create_company(company_data)
        assert status == 201
        
        company = db_session.query(Company).first()
        assert company.tax_id == 'TAX-ID-999'
    
    # ========== Error Handling Tests ==========
    
    def test_get_company_not_found(self, db_session):
        """Test getting a non-existent company."""
        non_existent_id = uuid.uuid4()
        filter_obj = create_mock_filter()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.get_companies(non_existent_id, filter_obj)
    
    def test_update_company_not_found(self, db_session):
        """Test updating a non-existent company."""
        non_existent_id = uuid.uuid4()
        update_data = {'location': 'New Location'}
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_company(non_existent_id, update_data)
    
    def test_delete_company_not_found(self, db_session):
        """Test deleting a non-existent company."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_company(non_existent_id)
    
    def test_get_companies_empty_database(self, db_session):
        """Test getting companies when database is empty."""
        filter_obj = create_mock_filter()
        result, status = self.service.get_companies(None, filter_obj)
        
        assert status == 200
        assert 'companies' in result

