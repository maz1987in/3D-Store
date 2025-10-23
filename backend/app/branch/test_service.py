"""
Unit tests for Branch Service and Repository.

Tests all business logic in branch/service.py and branch/repository.py including:
- Branch CRUD operations
- Branch repository custom queries
- Company-branch relationships
- Multi-location hierarchies
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
from app.branch.service import BranchService
from app.branch.repository import BranchRepository
from app.branch.model import Branch
from app.common.error_handling import ResourceNotFoundError


class TestBranchService(BaseServiceTestCase):
    """Test cases for BranchService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = BranchService()
    
    # ========== CRUD Operations Tests ==========
    
    def test_create_branch_success(self, db_session, sample_company):
        """Test creating a branch successfully."""
        branch_data = {
            'name': json.dumps({'en': 'Main Branch', 'ar': 'الفرع الرئيسي'}),
            'location': 'Downtown Office',
            'manager': 'Jane Doe',
            'company_id': sample_company.id
        }
        
        result, status = self.service.create_branch(branch_data)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify branch was created
        branch = db_session.query(Branch).first()
        assert branch is not None
        assert branch.location == 'Downtown Office'
        assert branch.manager == 'Jane Doe'
    
    def test_get_branches_with_pagination(self, db_session, sample_company):
        """Test getting branches with pagination."""
        # Create multiple branches
        for i in range(12):
            branch_data = {
                'name': json.dumps({'en': f'Branch {i}', 'ar': f'فرع {i}'}),
                'location': f'Location {i}',
                'manager': f'Manager {i}',
                'company_id': sample_company.id
            }
            self.service.create_branch(branch_data)
        
        filter_obj = create_mock_filter(page=1, per_page=10)
        result, status = self.service.get_branchs(None, filter_obj)
        
        assert status == 200
        assert 'branchs' in result
        assert 'filters' in result
    
    def test_get_branch_by_id(self, db_session, sample_company):
        """Test getting a specific branch by ID."""
        branch_data = {
            'name': json.dumps({'en': 'Test Branch', 'ar': 'فرع اختبار'}),
            'location': 'Test Location',
            'manager': 'Test Manager',
            'company_id': sample_company.id
        }
        self.service.create_branch(branch_data)
        
        branch = db_session.query(Branch).first()
        filter_obj = create_mock_filter()
        
        result, status = self.service.get_branchs(branch.id, filter_obj)
        
        assert status == 200
        assert 'branchs' in result
    
    def test_update_branch_success(self, db_session, sample_company):
        """Test updating a branch."""
        # Create branch
        branch_data = {
            'name': json.dumps({'en': 'Original Branch', 'ar': 'فرع أصلي'}),
            'location': 'Old Location',
            'manager': 'Old Manager',
            'company_id': sample_company.id
        }
        self.service.create_branch(branch_data)
        
        branch = db_session.query(Branch).first()
        
        # Update branch
        update_data = {
            'location': 'New Location',
            'manager': 'New Manager'
        }
        
        result, status = self.service.update_branch(branch.id, update_data)
        
        assert status == 200
        assert 'Updated' in result
        
        db_session.refresh(branch)
        assert branch.location == 'New Location'
        assert branch.manager == 'New Manager'
    
    def test_delete_branch_success(self, db_session, sample_company):
        """Test deleting a branch."""
        branch_data = {
            'name': json.dumps({'en': 'Delete Branch', 'ar': 'حذف فرع'}),
            'location': 'Delete Location',
            'manager': 'Delete Manager',
            'company_id': sample_company.id
        }
        self.service.create_branch(branch_data)
        
        branch = db_session.query(Branch).first()
        branch_id = branch.id
        
        result, status = self.service.delete_branch(branch_id)
        
        assert status == 200
        assert 'deleted' in result.lower()
        
        deleted_branch = db_session.query(Branch).filter_by(id=branch_id).first()
        assert deleted_branch is None
    
    # ========== Company-Branch Relationship Tests ==========
    
    def test_multiple_branches_same_company(self, db_session, sample_company):
        """Test creating multiple branches for the same company."""
        for i in range(5):
            branch_data = {
                'name': json.dumps({'en': f'Branch {i}', 'ar': f'فرع {i}'}),
                'location': f'Location {i}',
                'manager': f'Manager {i}',
                'company_id': sample_company.id
            }
            result, status = self.service.create_branch(branch_data)
            assert status == 201
        
        # Verify all branches belong to same company
        branches = db_session.query(Branch).filter(Branch.company_id == sample_company.id).all()
        assert len(branches) >= 5
    
    # ========== Error Handling Tests ==========
    
    def test_create_branch_missing_required_fields(self, db_session):
        """Test creating branch with missing required fields."""
        incomplete_data = {
            'location': 'Test Location'
            # Missing name and manager
        }
        
        with pytest.raises(Exception):
            self.service.create_branch(incomplete_data)
    
    def test_get_branch_not_found(self, db_session):
        """Test getting a non-existent branch."""
        non_existent_id = uuid.uuid4()
        filter_obj = create_mock_filter()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.get_branchs(non_existent_id, filter_obj)
    
    def test_update_branch_not_found(self, db_session):
        """Test updating a non-existent branch."""
        non_existent_id = uuid.uuid4()
        update_data = {'location': 'New Location'}
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_branch(non_existent_id, update_data)
    
    def test_delete_branch_not_found(self, db_session):
        """Test deleting a non-existent branch."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_branch(non_existent_id)
    
    def test_get_branches_empty_database(self, db_session):
        """Test getting branches when database is empty."""
        filter_obj = create_mock_filter()
        result, status = self.service.get_branchs(None, filter_obj)
        
        assert status == 200
        assert 'branchs' in result


class TestBranchRepository(BaseServiceTestCase):
    """Test cases for BranchRepository."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.repository = BranchRepository()
    
    # ========== Repository Query Tests ==========
    
    def test_get_branch_by_location(self, db_session, sample_company):
        """Test getting branch by location."""
        # Create branch
        branch_data = {
            'name': json.dumps({'en': 'Location Branch', 'ar': 'فرع الموقع'}),
            'location': 'Unique Location 123',
            'manager': 'Manager',
            'company_id': sample_company.id
        }
        service = BranchService()
        service.create_branch(branch_data)
        
        # Query by location
        branch = self.repository.get_branch_by_location('Unique Location 123', db_session)
        
        assert branch is not None
        assert branch.location == 'Unique Location 123'
    
    def test_get_branch_by_manager(self, db_session, sample_company):
        """Test getting branch by manager name."""
        # Create branch
        branch_data = {
            'name': json.dumps({'en': 'Manager Branch', 'ar': 'فرع المدير'}),
            'location': 'Test Location',
            'manager': 'Unique Manager Name',
            'company_id': sample_company.id
        }
        service = BranchService()
        service.create_branch(branch_data)
        
        # Query by manager
        branch = self.repository.get_branch_by_manager('Unique Manager Name', db_session)
        
        assert branch is not None
        assert branch.manager == 'Unique Manager Name'
    
    def test_get_branch_by_company(self, db_session, sample_company):
        """Test getting all branches for a company."""
        service = BranchService()
        
        # Create multiple branches for company
        for i in range(3):
            branch_data = {
                'name': json.dumps({'en': f'Company Branch {i}', 'ar': f'فرع شركة {i}'}),
                'location': f'Location {i}',
                'manager': f'Manager {i}',
                'company_id': sample_company.id
            }
            service.create_branch(branch_data)
        
        # Query by company
        branches = self.repository.get_branches_by_company(sample_company.id, db_session)
        
        assert len(branches) >= 3
        assert all(b.company_id == sample_company.id for b in branches)
    
    def test_get_active_branches(self, db_session, sample_company):
        """Test getting only active branches."""
        service = BranchService()
        
        # Create mix of active and inactive branches
        for i in range(4):
            branch_data = {
                'name': json.dumps({'en': f'Branch {i}', 'ar': f'فرع {i}'}),
                'location': f'Location {i}',
                'manager': f'Manager {i}',
                'company_id': sample_company.id,
                'is_active': (i % 2 == 0)  # Even indices active
            }
            service.create_branch(branch_data)
        
        # Query active only
        active_branches = self.repository.get_active_branches(db_session)
        
        assert len(active_branches) >= 2
        assert all(b.is_active for b in active_branches)
    
    # ========== Edge Cases Tests ==========
    
    def test_repository_get_by_location_not_found(self, db_session):
        """Test repository query with non-existent location."""
        branch = self.repository.get_branch_by_location('NonExistent Location', db_session)
        
        assert branch is None
    
    def test_repository_get_by_manager_not_found(self, db_session):
        """Test repository query with non-existent manager."""
        branch = self.repository.get_branch_by_manager('NonExistent Manager', db_session)
        
        assert branch is None
    
    def test_repository_get_by_company_empty(self, db_session):
        """Test repository query for company with no branches."""
        from app.company.model import Company
        
        # Create company without branches
        company = Company(
            name='No Branches Company',
            is_active=True
        )
        db_session.add(company)
        db_session.commit()
        
        branches = self.repository.get_branches_by_company(company.id, db_session)
        
        assert len(branches) == 0

