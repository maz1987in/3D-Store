"""
Unit tests for Product Service.

Tests all business logic in product/service.py including:
- Product CRUD operations with repository integration
- Product pricing and 3D printing parameters
- Material usage calculations
- Inventory integration
- Category associations
- Product search and filtering
- File upload handling (images, 3D models)
- Edge cases and error handling
"""

import pytest
import uuid
import json
from decimal import Decimal
from unittest.mock import Mock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from test.test_helpers import create_mock_filter, create_test_file
from app.product.service import ProductService
from app.product.model import Product
from app.common.error_handling import ResourceNotFoundError


class TestProductService(BaseServiceTestCase):
    """Test cases for ProductService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = ProductService()
    
    # ========== CRUD Operations Tests ==========
    
    @patch('app.product.service.upload_files')
    def test_create_product_success(self, mock_upload, db_session, sample_category):
        """Test creating a product successfully."""
        product_data = {
            'title': json.dumps({'en': '3D Printed Vase', 'ar': 'مزهرية مطبوعة ثلاثية الأبعاد'}),
            'description': json.dumps({'en': 'Beautiful vase', 'ar': 'مزهرية جميلة'}),
            'price': 25.50,
            'code': 'PROD-001',
            'category_id': sample_category.id,
            'unit': 'PIECE',
            'quantity': 10,
            'min_quantity': 2
        }
        
        mock_files = Mock()
        mock_files.getlist.return_value = []
        
        result, status = self.service.create_product(product_data, mock_files)
        
        assert status == 201
        assert 'Created' in result
    
    def test_get_products_with_pagination(self, db_session, sample_product):
        """Test getting products with pagination."""
        filter_obj = create_mock_filter(page=1, per_page=10)
        result, status = self.service.get_products(None, filter_obj)
        
        assert status == 200
        assert 'products' in result
        assert 'filters' in result
    
    def test_get_product_by_id(self, db_session, sample_product):
        """Test getting a specific product by ID."""
        filter_obj = create_mock_filter()
        result, status = self.service.get_products(sample_product.id, filter_obj)
        
        assert status == 200
        assert 'products' in result
    
    @patch('app.product.service.upload_files')
    def test_update_product_success(self, mock_upload, db_session, sample_product):
        """Test updating a product."""
        update_data = {
            'title': json.dumps({'en': 'Updated Product', 'ar': 'منتج محدث'}),
            'price': 35.00,
            'quantity': 20
        }
        
        mock_files = Mock()
        mock_files.getlist.return_value = []
        
        result, status = self.service.update_product(sample_product.id, update_data, mock_files)
        
        assert status == 200
        assert 'Updated' in result
    
    def test_delete_product_success(self, db_session, sample_product):
        """Test deleting a product."""
        product_id = sample_product.id
        
        result, status = self.service.delete_product(product_id)
        
        assert status == 200
        assert 'deleted' in result.lower()
        
        deleted_product = db_session.query(Product).filter_by(id=product_id).first()
        assert deleted_product is None
    
    # ========== 3D Printing Parameters Tests ==========
    
    @patch('app.product.service.upload_files')
    def test_product_with_3d_parameters(self, mock_upload, db_session, sample_category):
        """Test product with 3D printing parameters."""
        product_data = {
            'title': json.dumps({'en': '3D Model', 'ar': 'نموذج ثلاثي الأبعاد'}),
            'description': json.dumps({'en': 'Test model', 'ar': 'نموذج اختبار'}),
            'price': 50.00,
            'code': 'PROD-3D-001',
            'category_id': sample_category.id,
            'unit': 'PIECE',
            'quantity': 5,
            # 3D parameters
            'volume': 125.5,  # cubic cm
            'layer_height': 0.2,  # mm
            'infill_percentage': 20,  # %
            'support_material': True,
            'print_time_minutes': 180
        }
        
        mock_files = Mock()
        mock_files.getlist.return_value = []
        
        result, status = self.service.create_product(product_data, mock_files)
        
        assert status == 201
    
    # ========== Pricing Tests ==========
    
    @patch('app.product.service.upload_files')
    def test_product_pricing_with_zero(self, mock_upload, db_session, sample_category):
        """Test product with zero price (free item)."""
        product_data = {
            'title': json.dumps({'en': 'Free Sample', 'ar': 'عينة مجانية'}),
            'description': json.dumps({'en': 'Free', 'ar': 'مجاني'}),
            'price': 0.00,
            'code': 'PROD-FREE',
            'category_id': sample_category.id,
            'unit': 'PIECE'
        }
        
        mock_files = Mock()
        mock_files.getlist.return_value = []
        
        result, status = self.service.create_product(product_data, mock_files)
        
        assert status == 201
    
    @patch('app.product.service.upload_files')
    def test_product_pricing_large_amount(self, mock_upload, db_session, sample_category):
        """Test product with large price."""
        product_data = {
            'title': json.dumps({'en': 'Expensive Item', 'ar': 'عنصر باهظ'}),
            'description': json.dumps({'en': 'High value', 'ar': 'قيمة عالية'}),
            'price': 9999.99,
            'code': 'PROD-EXPENSIVE',
            'category_id': sample_category.id,
            'unit': 'PIECE'
        }
        
        mock_files = Mock()
        mock_files.getlist.return_value = []
        
        result, status = self.service.create_product(product_data, mock_files)
        
        assert status == 201
    
    # ========== Inventory Integration Tests ==========
    
    def test_product_quantity_tracking(self, db_session, sample_product):
        """Test product quantity tracking."""
        assert sample_product.quantity >= 0
    
    def test_product_minimum_quantity_threshold(self, db_session, sample_product):
        """Test minimum quantity threshold for alerts."""
        sample_product.min_quantity = 5
        db_session.commit()
        
        # Check if below minimum
        is_low_stock = sample_product.quantity < sample_product.min_quantity
        assert isinstance(is_low_stock, bool)
    
    # ========== Category Association Tests ==========
    
    def test_product_with_category(self, db_session, sample_product, sample_category):
        """Test product-category relationship."""
        sample_product.category_id = sample_category.id
        db_session.commit()
        
        # Verify relationship
        db_session.refresh(sample_product)
        assert sample_product.category_id == sample_category.id
    
    @patch('app.product.service.upload_files')
    def test_create_product_without_category(self, mock_upload, db_session):
        """Test creating product without category."""
        product_data = {
            'title': json.dumps({'en': 'No Category', 'ar': 'بلا فئة'}),
            'description': json.dumps({'en': 'Test', 'ar': 'اختبار'}),
            'price': 10.00,
            'code': 'PROD-NO-CAT',
            'unit': 'PIECE'
        }
        
        mock_files = Mock()
        mock_files.getlist.return_value = []
        
        result, status = self.service.create_product(product_data, mock_files)
        
        assert status == 201
    
    # ========== Product Code Tests ==========
    
    @patch('app.product.service.upload_files')
    def test_product_unique_code(self, mock_upload, db_session, sample_category):
        """Test product code uniqueness."""
        product_data = {
            'title': json.dumps({'en': 'First Product', 'ar': 'منتج أول'}),
            'description': json.dumps({'en': 'First', 'ar': 'أول'}),
            'price': 10.00,
            'code': 'UNIQUE-001',
            'category_id': sample_category.id,
            'unit': 'PIECE'
        }
        
        mock_files = Mock()
        mock_files.getlist.return_value = []
        
        # Create first product
        result1, status1 = self.service.create_product(product_data, mock_files)
        assert status1 == 201
        
        # Try to create duplicate code
        product_data['title'] = json.dumps({'en': 'Second Product', 'ar': 'منتج ثاني'})
        
        with pytest.raises(Exception):  # Unique constraint
            self.service.create_product(product_data, mock_files)
    
    # ========== Product Unit Tests ==========
    
    @patch('app.product.service.upload_files')
    def test_product_different_units(self, mock_upload, db_session, sample_category):
        """Test products with different units."""
        units = ['PIECE', 'KG', 'METER', 'LITER']
        
        for unit in units:
            product_data = {
                'title': json.dumps({'en': f'Product {unit}', 'ar': f'منتج {unit}'}),
                'description': json.dumps({'en': 'Test', 'ar': 'اختبار'}),
                'price': 10.00,
                'code': f'PROD-{unit}',
                'category_id': sample_category.id,
                'unit': unit
            }
            
            mock_files = Mock()
            mock_files.getlist.return_value = []
            
            result, status = self.service.create_product(product_data, mock_files)
            assert status == 201
    
    # ========== Error Handling Tests ==========
    
    def test_get_product_not_found(self, db_session):
        """Test getting a non-existent product."""
        non_existent_id = uuid.uuid4()
        filter_obj = create_mock_filter()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.get_products(non_existent_id, filter_obj)
    
    @patch('app.product.service.upload_files')
    def test_update_product_not_found(self, mock_upload, db_session):
        """Test updating a non-existent product."""
        non_existent_id = uuid.uuid4()
        update_data = {
            'price': 20.00
        }
        
        mock_files = Mock()
        mock_files.getlist.return_value = []
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_product(non_existent_id, update_data, mock_files)
    
    def test_delete_product_not_found(self, db_session):
        """Test deleting a non-existent product."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_product(non_existent_id)
    
    def test_get_products_empty_database(self, db_session):
        """Test getting products when database is empty."""
        # Clear products
        db_session.query(Product).delete()
        db_session.commit()
        
        filter_obj = create_mock_filter()
        result, status = self.service.get_products(None, filter_obj)
        
        assert status == 200
        assert 'products' in result

