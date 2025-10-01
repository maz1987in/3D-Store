"""
API tests for product endpoints.

This module contains API tests for product-related endpoints.
"""

import pytest
from unittest.mock import patch, Mock

from test.base_test import BaseAPITestCase


class TestProductEndpoints(BaseAPITestCase):
    """Test cases for product endpoints."""
    
    def test_get_products_success(self, db_session, sample_product):
        """Test getting products successfully."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'USER'}
            
            response = self.get('/api/products', headers=self.auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'products' in data
            assert 'total' in data
            assert 'page' in data
            assert 'per_page' in data
            assert len(data['products']) >= 1
    
    def test_get_products_with_filters(self, db_session, sample_product, sample_category):
        """Test getting products with filters."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'USER'}
            
            # Test with category filter
            response = self.get(f'/api/products?category_id={sample_category.id}', headers=self.auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'products' in data
            assert len(data['products']) >= 1
    
    def test_get_products_with_pagination(self, db_session, sample_product):
        """Test getting products with pagination."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'USER'}
            
            response = self.get('/api/products?page=1&per_page=5', headers=self.auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'products' in data
            assert 'total' in data
            assert 'page' in data
            assert 'per_page' in data
            assert data['page'] == 1
            assert data['per_page'] == 5
    
    def test_get_products_with_sorting(self, db_session, sample_product):
        """Test getting products with sorting."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'USER'}
            
            response = self.get('/api/products?sort=base_price&order=asc', headers=self.auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'products' in data
            assert len(data['products']) >= 1
    
    def test_get_products_unauthorized(self, db_session):
        """Test getting products without authentication."""
        response = self.get('/api/products')
        
        self.assert_response_unauthorized(response)
        data = self.get_json_response(response)
        
        assert 'error' in data
        assert 'token' in data['error'].lower()
    
    def test_get_product_by_id_success(self, db_session, sample_product):
        """Test getting product by ID successfully."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'USER'}
            
            response = self.get(f'/api/products/{sample_product.id}', headers=self.auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'product' in data
            assert data['product']['id'] == str(sample_product.id)
            assert data['product']['code'] == sample_product.code
            assert data['product']['sku'] == sample_product.sku
    
    def test_get_product_by_id_not_found(self, db_session):
        """Test getting non-existent product by ID."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'USER'}
            
            response = self.get('/api/products/non-existent-id', headers=self.auth_headers)
            
            self.assert_response_not_found(response)
            data = self.get_json_response(response)
            
            assert 'error' in data
            assert 'not found' in data['error'].lower()
    
    def test_get_product_by_id_unauthorized(self, db_session, sample_product):
        """Test getting product by ID without authentication."""
        response = self.get(f'/api/products/{sample_product.id}')
        
        self.assert_response_unauthorized(response)
        data = self.get_json_response(response)
        
        assert 'error' in data
        assert 'token' in data['error'].lower()
    
    def test_create_product_success(self, db_session, sample_category):
        """Test creating product successfully."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'ADMIN'}
            
            product_data = {
                'code': 'NEW_PROD',
                'sku': 'NEW-SKU-001',
                'product_type': 'service',
                'category_id': str(sample_category.id),
                'base_price': 200.00,
                'currency': 'USD',
                'is_dynamic_pricing': False
            }
            
            response = self.post('/api/products', json_data=product_data, headers=self.admin_headers)
            
            self.assert_response_success(response, 201)
            data = self.get_json_response(response)
            
            assert 'product' in data
            assert data['product']['code'] == 'NEW_PROD'
            assert data['product']['sku'] == 'NEW-SKU-001'
            assert data['product']['product_type'] == 'service'
            assert data['product']['base_price'] == 200.00
            assert data['product']['currency'] == 'USD'
    
    def test_create_product_unauthorized(self, db_session, sample_category):
        """Test creating product without authentication."""
        product_data = {
            'code': 'NEW_PROD',
            'sku': 'NEW-SKU-001',
            'product_type': 'service',
            'category_id': str(sample_category.id),
            'base_price': 200.00,
            'currency': 'USD'
        }
        
        response = self.post('/api/products', json_data=product_data)
        
        self.assert_response_unauthorized(response)
        data = self.get_json_response(response)
        
        assert 'error' in data
        assert 'token' in data['error'].lower()
    
    def test_create_product_forbidden(self, db_session, sample_category):
        """Test creating product without admin privileges."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'USER'}
            
            product_data = {
                'code': 'NEW_PROD',
                'sku': 'NEW-SKU-001',
                'product_type': 'service',
                'category_id': str(sample_category.id),
                'base_price': 200.00,
                'currency': 'USD'
            }
            
            response = self.post('/api/products', json_data=product_data, headers=self.auth_headers)
            
            self.assert_response_forbidden(response)
            data = self.get_json_response(response)
            
            assert 'error' in data
            assert 'permission' in data['error'].lower()
    
    def test_create_product_invalid_data(self, db_session, sample_category):
        """Test creating product with invalid data."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'ADMIN'}
            
            product_data = {
                'code': '',  # Invalid: empty code
                'sku': 'NEW-SKU-001',
                'product_type': 'service',
                'category_id': str(sample_category.id),
                'base_price': -100.00,  # Invalid: negative price
                'currency': 'USD'
            }
            
            response = self.post('/api/products', json_data=product_data, headers=self.admin_headers)
            
            self.assert_response_error(response, 400)
            data = self.get_json_response(response)
            
            assert 'error' in data
            assert 'validation' in data['error']
    
    def test_create_product_missing_fields(self, db_session, sample_category):
        """Test creating product with missing required fields."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'ADMIN'}
            
            product_data = {
                'code': 'NEW_PROD'
                # Missing required fields
            }
            
            response = self.post('/api/products', json_data=product_data, headers=self.admin_headers)
            
            self.assert_response_error(response, 400)
            data = self.get_json_response(response)
            
            assert 'error' in data
            assert 'validation' in data['error']
    
    def test_create_product_duplicate_code(self, db_session, sample_product, sample_category):
        """Test creating product with duplicate code."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'ADMIN'}
            
            product_data = {
                'code': sample_product.code,  # Duplicate code
                'sku': 'NEW-SKU-001',
                'product_type': 'service',
                'category_id': str(sample_category.id),
                'base_price': 200.00,
                'currency': 'USD'
            }
            
            response = self.post('/api/products', json_data=product_data, headers=self.admin_headers)
            
            self.assert_response_error(response, 400)
            data = self.get_json_response(response)
            
            assert 'error' in data
            assert 'code' in data['error'].lower()
    
    def test_update_product_success(self, db_session, sample_product):
        """Test updating product successfully."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'ADMIN'}
            
            update_data = {
                'base_price': 150.00,
                'is_dynamic_pricing': True
            }
            
            response = self.put(f'/api/products/{sample_product.id}', json_data=update_data, headers=self.admin_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'product' in data
            assert data['product']['base_price'] == 150.00
            assert data['product']['is_dynamic_pricing'] is True
    
    def test_update_product_not_found(self, db_session):
        """Test updating non-existent product."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'ADMIN'}
            
            update_data = {
                'base_price': 150.00
            }
            
            response = self.put('/api/products/non-existent-id', json_data=update_data, headers=self.admin_headers)
            
            self.assert_response_not_found(response)
            data = self.get_json_response(response)
            
            assert 'error' in data
            assert 'not found' in data['error'].lower()
    
    def test_update_product_unauthorized(self, db_session, sample_product):
        """Test updating product without authentication."""
        update_data = {
            'base_price': 150.00
        }
        
        response = self.put(f'/api/products/{sample_product.id}', json_data=update_data)
        
        self.assert_response_unauthorized(response)
        data = self.get_json_response(response)
        
        assert 'error' in data
        assert 'token' in data['error'].lower()
    
    def test_update_product_forbidden(self, db_session, sample_product):
        """Test updating product without admin privileges."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'USER'}
            
            update_data = {
                'base_price': 150.00
            }
            
            response = self.put(f'/api/products/{sample_product.id}', json_data=update_data, headers=self.auth_headers)
            
            self.assert_response_forbidden(response)
            data = self.get_json_response(response)
            
            assert 'error' in data
            assert 'permission' in data['error'].lower()
    
    def test_update_product_invalid_data(self, db_session, sample_product):
        """Test updating product with invalid data."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'ADMIN'}
            
            update_data = {
                'base_price': -100.00  # Invalid: negative price
            }
            
            response = self.put(f'/api/products/{sample_product.id}', json_data=update_data, headers=self.admin_headers)
            
            self.assert_response_error(response, 400)
            data = self.get_json_response(response)
            
            assert 'error' in data
            assert 'validation' in data['error']
    
    def test_delete_product_success(self, db_session, sample_product):
        """Test deleting product successfully."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'ADMIN'}
            
            response = self.delete(f'/api/products/{sample_product.id}', headers=self.admin_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'message' in data
            assert 'successfully' in data['message'].lower()
    
    def test_delete_product_not_found(self, db_session):
        """Test deleting non-existent product."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'ADMIN'}
            
            response = self.delete('/api/products/non-existent-id', headers=self.admin_headers)
            
            self.assert_response_not_found(response)
            data = self.get_json_response(response)
            
            assert 'error' in data
            assert 'not found' in data['error'].lower()
    
    def test_delete_product_unauthorized(self, db_session, sample_product):
        """Test deleting product without authentication."""
        response = self.delete(f'/api/products/{sample_product.id}')
        
        self.assert_response_unauthorized(response)
        data = self.get_json_response(response)
        
        assert 'error' in data
        assert 'token' in data['error'].lower()
    
    def test_delete_product_forbidden(self, db_session, sample_product):
        """Test deleting product without admin privileges."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'USER'}
            
            response = self.delete(f'/api/products/{sample_product.id}', headers=self.auth_headers)
            
            self.assert_response_forbidden(response)
            data = self.get_json_response(response)
            
            assert 'error' in data
            assert 'permission' in data['error'].lower()
    
    def test_search_products_success(self, db_session, sample_product):
        """Test searching products successfully."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'USER'}
            
            response = self.get('/api/products/search?q=TEST_PROD', headers=self.auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'products' in data
            assert 'total' in data
            assert len(data['products']) >= 1
    
    def test_search_products_empty_query(self, db_session):
        """Test searching products with empty query."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'USER'}
            
            response = self.get('/api/products/search?q=', headers=self.auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'products' in data
            assert 'total' in data
            assert data['total'] == 0
    
    def test_search_products_unauthorized(self, db_session):
        """Test searching products without authentication."""
        response = self.get('/api/products/search?q=test')
        
        self.assert_response_unauthorized(response)
        data = self.get_json_response(response)
        
        assert 'error' in data
        assert 'token' in data['error'].lower()
    
    def test_get_featured_products_success(self, db_session, sample_product):
        """Test getting featured products successfully."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'USER'}
            
            # Make product featured
            sample_product.is_featured = True
            self.db_session.commit()
            
            response = self.get('/api/products/featured', headers=self.auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'products' in data
            assert len(data['products']) >= 1
            assert all(product['is_featured'] for product in data['products'])
    
    def test_get_featured_products_unauthorized(self, db_session):
        """Test getting featured products without authentication."""
        response = self.get('/api/products/featured')
        
        self.assert_response_unauthorized(response)
        data = self.get_json_response(response)
        
        assert 'error' in data
        assert 'token' in data['error'].lower()
    
    def test_get_products_by_category_success(self, db_session, sample_product, sample_category):
        """Test getting products by category successfully."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'USER'}
            
            response = self.get(f'/api/products/category/{sample_category.id}', headers=self.auth_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'products' in data
            assert 'total' in data
            assert len(data['products']) >= 1
            assert all(product['category_id'] == str(sample_category.id) for product in data['products'])
    
    def test_get_products_by_category_not_found(self, db_session):
        """Test getting products by non-existent category."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'USER'}
            
            response = self.get('/api/products/category/non-existent-id', headers=self.auth_headers)
            
            self.assert_response_not_found(response)
            data = self.get_json_response(response)
            
            assert 'error' in data
            assert 'not found' in data['error'].lower()
    
    def test_get_products_by_category_unauthorized(self, db_session, sample_category):
        """Test getting products by category without authentication."""
        response = self.get(f'/api/products/category/{sample_category.id}')
        
        self.assert_response_unauthorized(response)
        data = self.get_json_response(response)
        
        assert 'error' in data
        assert 'token' in data['error'].lower()
    
    def test_get_product_statistics_success(self, db_session, sample_product):
        """Test getting product statistics successfully."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'ADMIN'}
            
            response = self.get('/api/products/statistics', headers=self.admin_headers)
            
            self.assert_response_success(response)
            data = self.get_json_response(response)
            
            assert 'total_products' in data
            assert 'products_by_type' in data
            assert 'products_by_category' in data
            assert 'featured_products' in data
    
    def test_get_product_statistics_unauthorized(self, db_session):
        """Test getting product statistics without authentication."""
        response = self.get('/api/products/statistics')
        
        self.assert_response_unauthorized(response)
        data = self.get_json_response(response)
        
        assert 'error' in data
        assert 'token' in data['error'].lower()
    
    def test_get_product_statistics_forbidden(self, db_session):
        """Test getting product statistics without admin privileges."""
        with patch('jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'USER'}
            
            response = self.get('/api/products/statistics', headers=self.auth_headers)
            
            self.assert_response_forbidden(response)
            data = self.get_json_response(response)
            
            assert 'error' in data
            assert 'permission' in data['error'].lower()
