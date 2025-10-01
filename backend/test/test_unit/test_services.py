"""
Unit tests for service layer.

This module contains unit tests for all service classes in the application.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from test.base_test import BaseServiceTestCase
from app.users.services.user_management_service import UserManagementService
from app.users.services.user_authentication_service import UserAuthenticationService
from app.users.services.user_search_service import UserSearchService
from app.users.services.user_statistics_service import UserStatisticsService
from app.product.service import ProductService
from app.order.service import OrderService
from app.inventory.service import InventoryService
from app.transaction.service import TransactionService
from app.category.service import CategoryService
from app.customers.service import CustomerService
from app.branch.service import BranchService
from app.company.service import CompanyService
from app.store.service import StoreService
from app.expense.service import ExpenseService
from app.common.enum import UserTypeEnum, LanguageEnum, OrderStatusEnum, TransactionType


class TestUserManagementService(BaseServiceTestCase):
    """Test cases for UserManagementService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = UserManagementService()
    
    def test_is_user_exist_by_phone(self, db_session, sample_user):
        """Test checking if user exists by phone."""
        # Test existing user
        result = self.service.is_user_exist(phone=sample_user.phone)
        assert result is True
        
        # Test non-existing user
        result = self.service.is_user_exist(phone='+9999999999')
        assert result is False
    
    def test_is_user_exist_by_email(self, db_session, sample_user):
        """Test checking if user exists by email."""
        # Test existing user
        result = self.service.is_user_exist(email=sample_user.email)
        assert result is True
        
        # Test non-existing user
        result = self.service.is_user_exist(email='nonexistent@example.com')
        assert result is False
    
    def test_is_user_id_exist(self, db_session, sample_user):
        """Test checking if user exists by user_id and type."""
        # Test existing user
        result = self.service.is_user_id_exist(sample_user.id, sample_user.user_type)
        assert result is True
        
        # Test non-existing user
        result = self.service.is_user_id_exist('nonexistent_id', UserTypeEnum.USER)
        assert result is False
    
    def test_create_user(self, db_session):
        """Test creating a new user."""
        user_data = {
            'username': 'newuser',
            'phone': '+1234567899',
            'email': 'newuser@example.com',
            'user_type': UserTypeEnum.USER,
            'language': LanguageEnum.ENGLISH,
            'password': 'newpassword'
        }
        
        result = self.service.create_user(**user_data)
        
        assert result is not None
        assert result['username'] == 'newuser'
        assert result['phone'] == '+1234567899'
        assert result['email'] == 'newuser@example.com'
        assert result['user_type'] == UserTypeEnum.USER
        assert result['language'] == LanguageEnum.ENGLISH
    
    def test_get_user_by_id(self, db_session, sample_user):
        """Test getting user by ID."""
        result = self.service.get_user_by_id(sample_user.id)
        
        assert result is not None
        assert result.id == sample_user.id
        assert result.username == sample_user.username
        assert result.phone == sample_user.phone
        assert result.email == sample_user.email
    
    def test_get_user_json_by_id(self, db_session, sample_user):
        """Test getting user JSON by ID."""
        result = self.service.get_user_json_by_id(sample_user.id)
        
        assert result is not None
        assert result['id'] == str(sample_user.id)
        assert result['username'] == sample_user.username
        assert result['phone'] == sample_user.phone
        assert result['email'] == sample_user.email
    
    def test_delete_user(self, db_session, sample_user):
        """Test deleting a user."""
        user_id = sample_user.id
        
        result = self.service.delete_user(user_id)
        
        assert result is True
        
        # Verify user is deleted
        deleted_user = self.service.get_user_by_id(user_id)
        assert deleted_user is None
    
    def test_disable_user(self, db_session, sample_user):
        """Test disabling a user."""
        user_id = sample_user.id
        
        result = self.service.disable_user(user_id)
        
        assert result is True
        
        # Verify user is disabled
        user = self.service.get_user_by_id(user_id)
        assert user.active is False
    
    def test_enable_user(self, db_session, sample_user):
        """Test enabling a user."""
        # First disable the user
        self.service.disable_user(sample_user.id)
        
        # Then enable it
        result = self.service.enable_user(sample_user.id)
        
        assert result is True
        
        # Verify user is enabled
        user = self.service.get_user_by_id(sample_user.id)
        assert user.active is True


class TestUserAuthenticationService(BaseServiceTestCase):
    """Test cases for UserAuthenticationService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = UserAuthenticationService()
    
    def test_get_user_by_email(self, db_session, sample_user):
        """Test getting user by email."""
        result = self.service.get_user_by_email(sample_user.email)
        
        assert result is not None
        assert result.id == sample_user.id
        assert result.email == sample_user.email
    
    def test_get_user_by_mobile(self, db_session, sample_user):
        """Test getting user by mobile phone."""
        result = self.service.get_user_by_mobile(sample_user.phone)
        
        assert result is not None
        assert result.id == sample_user.id
        assert result.phone == sample_user.phone
    
    def test_get_user_by_any_email(self, db_session, sample_user):
        """Test getting user by any identifier (email)."""
        result = self.service.get_user_by_any(sample_user.email)
        
        assert result is not None
        assert result.id == sample_user.id
        assert result.email == sample_user.email
    
    def test_get_user_by_any_phone(self, db_session, sample_user):
        """Test getting user by any identifier (phone)."""
        result = self.service.get_user_by_any(sample_user.phone)
        
        assert result is not None
        assert result.id == sample_user.id
        assert result.phone == sample_user.phone


class TestUserSearchService(BaseServiceTestCase):
    """Test cases for UserSearchService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = UserSearchService()
    
    def test_get_users(self, db_session, sample_user):
        """Test getting users with roles."""
        # Create a filter object
        filter_obj = Mock()
        filter_obj.filters = []
        filter_obj.sorters = []
        filter_obj.page = 1
        filter_obj.per_page = 10
        
        result = self.service.get_users(filter_obj)
        
        assert result is not None
        assert 'users' in result
        assert 'total' in result
        assert 'page' in result
        assert 'per_page' in result
        assert len(result['users']) >= 1
    
    def test_get_user_admin(self, db_session, sample_admin):
        """Test getting admin user."""
        result = self.service.get_user_admin(sample_admin.id)
        
        assert result is not None
        assert result.id == sample_admin.id
        assert result.user_type == UserTypeEnum.ADMIN
    
    def test_get_users_by_user_type(self, db_session, sample_user):
        """Test getting users by user type."""
        result = self.service.get_users_by_user_type(UserTypeEnum.USER)
        
        assert result is not None
        assert len(result) >= 1
        assert all(user.user_type == UserTypeEnum.USER for user in result)
    
    def test_search_user(self, db_session, sample_user):
        """Test searching users."""
        result = self.service.search_user('testuser')
        
        assert result is not None
        assert len(result) >= 1
        assert any('testuser' in user.username.lower() for user in result)


class TestUserStatisticsService(BaseServiceTestCase):
    """Test cases for UserStatisticsService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = UserStatisticsService()
    
    def test_get_users_statistics(self, db_session, sample_user):
        """Test getting user statistics."""
        result = self.service.get_users_statistics()
        
        assert result is not None
        assert 'total_users' in result
        assert 'active_users' in result
        assert 'inactive_users' in result
        assert 'users_by_type' in result
        assert 'users_by_language' in result
    
    def test_get_user_growth_analytics(self, db_session, sample_user):
        """Test getting user growth analytics."""
        result = self.service.get_user_growth_analytics()
        
        assert result is not None
        assert 'growth_data' in result
        assert 'total_growth' in result
        assert 'monthly_growth' in result
    
    def test_get_user_engagement_metrics(self, db_session, sample_user):
        """Test getting user engagement metrics."""
        result = self.service.get_user_engagement_metrics()
        
        assert result is not None
        assert 'engagement_score' in result
        assert 'active_users' in result
        assert 'inactive_users' in result
        assert 'engagement_trends' in result


class TestProductService(BaseServiceTestCase):
    """Test cases for ProductService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = ProductService()
    
    def test_get_products(self, db_session, sample_product):
        """Test getting products."""
        # Create a filter object
        filter_obj = Mock()
        filter_obj.filters = []
        filter_obj.sorters = []
        filter_obj.page = 1
        filter_obj.per_page = 10
        
        result = self.service.get_products(filter_obj)
        
        assert result is not None
        assert 'products' in result
        assert 'total' in result
        assert 'page' in result
        assert 'per_page' in result
        assert len(result['products']) >= 1
    
    def test_get_product_by_id(self, db_session, sample_product):
        """Test getting product by ID."""
        result = self.service.get_product_by_id(sample_product.id)
        
        assert result is not None
        assert result.id == sample_product.id
        assert result.code == sample_product.code
    
    def test_create_product(self, db_session, sample_category):
        """Test creating a product."""
        product_data = {
            'code': 'NEW_PROD',
            'sku': 'NEW-SKU-001',
            'product_type': 'service',
            'category_id': sample_category.id,
            'base_price': 200.00,
            'currency': 'USD',
            'is_dynamic_pricing': False
        }
        
        result = self.service.create_product(product_data)
        
        assert result is not None
        assert result['code'] == 'NEW_PROD'
        assert result['sku'] == 'NEW-SKU-001'
        assert result['product_type'] == 'service'
        assert result['base_price'] == 200.00
        assert result['currency'] == 'USD'
    
    def test_update_product(self, db_session, sample_product):
        """Test updating a product."""
        update_data = {
            'base_price': 150.00,
            'is_dynamic_pricing': True
        }
        
        result = self.service.update_product(sample_product.id, update_data)
        
        assert result is not None
        assert result['base_price'] == 150.00
        assert result['is_dynamic_pricing'] is True
    
    def test_delete_product(self, db_session, sample_product):
        """Test deleting a product."""
        product_id = sample_product.id
        
        result = self.service.delete_product(product_id)
        
        assert result is True
        
        # Verify product is deleted
        deleted_product = self.service.get_product_by_id(product_id)
        assert deleted_product is None


class TestOrderService(BaseServiceTestCase):
    """Test cases for OrderService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = OrderService()
    
    def test_get_orders(self, db_session, sample_order):
        """Test getting orders."""
        # Create a filter object
        filter_obj = Mock()
        filter_obj.filters = []
        filter_obj.sorters = []
        filter_obj.page = 1
        filter_obj.per_page = 10
        
        result = self.service.get_orders(filter_obj)
        
        assert result is not None
        assert 'orders' in result
        assert 'total' in result
        assert 'page' in result
        assert 'per_page' in result
        assert len(result['orders']) >= 1
    
    def test_get_order_by_id(self, db_session, sample_order):
        """Test getting order by ID."""
        result = self.service.get_order_by_id(sample_order.id)
        
        assert result is not None
        assert result.id == sample_order.id
        assert result.order_number == sample_order.order_number
    
    def test_create_order(self, db_session, sample_customer):
        """Test creating an order."""
        order_data = {
            'order_number': 'ORD-002',
            'customer_id': sample_customer.id,
            'status': OrderStatusEnum.PENDING,
            'order_type': 'print_service',
            'subtotal': 200.00,
            'total_amount': 200.00,
            'currency': 'USD',
            'payment_status': 'pending'
        }
        
        result = self.service.create_order(order_data)
        
        assert result is not None
        assert result['order_number'] == 'ORD-002'
        assert result['customer_id'] == sample_customer.id
        assert result['status'] == OrderStatusEnum.PENDING
        assert result['subtotal'] == 200.00
        assert result['total_amount'] == 200.00
    
    def test_update_order_status(self, db_session, sample_order):
        """Test updating order status."""
        new_status = OrderStatusEnum.PROCESSING
        
        result = self.service.update_order_status(sample_order.id, new_status)
        
        assert result is not None
        assert result['status'] == new_status
    
    def test_delete_order(self, db_session, sample_order):
        """Test deleting an order."""
        order_id = sample_order.id
        
        result = self.service.delete_order(order_id)
        
        assert result is True
        
        # Verify order is deleted
        deleted_order = self.service.get_order_by_id(order_id)
        assert deleted_order is None


class TestInventoryService(BaseServiceTestCase):
    """Test cases for InventoryService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = InventoryService()
    
    def test_get_inventory(self, db_session, sample_inventory):
        """Test getting inventory."""
        # Create a filter object
        filter_obj = Mock()
        filter_obj.filters = []
        filter_obj.sorters = []
        filter_obj.page = 1
        filter_obj.per_page = 10
        
        result = self.service.get_inventory(filter_obj)
        
        assert result is not None
        assert 'inventory' in result
        assert 'total' in result
        assert 'page' in result
        assert 'per_page' in result
        assert len(result['inventory']) >= 1
    
    def test_get_inventory_by_id(self, db_session, sample_inventory):
        """Test getting inventory by ID."""
        result = self.service.get_inventory_by_id(sample_inventory.id)
        
        assert result is not None
        assert result.id == sample_inventory.id
        assert result.product_id == sample_inventory.product_id
        assert result.branch_id == sample_inventory.branch_id
    
    def test_update_inventory_quantity(self, db_session, sample_inventory):
        """Test updating inventory quantity."""
        new_quantity = 150
        
        result = self.service.update_inventory_quantity(sample_inventory.id, new_quantity)
        
        assert result is not None
        assert result['quantity'] == new_quantity
    
    def test_get_low_stock_items(self, db_session, sample_inventory):
        """Test getting low stock items."""
        # Set quantity below alert threshold
        sample_inventory.quantity = 5
        self.db_session.commit()
        
        result = self.service.get_low_stock_items()
        
        assert result is not None
        assert len(result) >= 1
        assert any(item['quantity'] <= item['quantity_alert'] for item in result)


class TestTransactionService(BaseServiceTestCase):
    """Test cases for TransactionService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = TransactionService()
    
    def test_get_transactions(self, db_session, sample_transaction):
        """Test getting transactions."""
        # Create a filter object
        filter_obj = Mock()
        filter_obj.filters = []
        filter_obj.sorters = []
        filter_obj.page = 1
        filter_obj.per_page = 10
        
        result = self.service.get_transactions(filter_obj)
        
        assert result is not None
        assert 'transactions' in result
        assert 'total' in result
        assert 'page' in result
        assert 'per_page' in result
        assert len(result['transactions']) >= 1
    
    def test_get_transaction_by_id(self, db_session, sample_transaction):
        """Test getting transaction by ID."""
        result = self.service.get_transaction_by_id(sample_transaction.id)
        
        assert result is not None
        assert result.id == sample_transaction.id
        assert result.product_id == sample_transaction.product_id
        assert result.transaction_type == sample_transaction.transaction_type
    
    def test_create_transaction(self, db_session, sample_product, sample_branch):
        """Test creating a transaction."""
        transaction_data = {
            'product_id': sample_product.id,
            'from_location_id': sample_branch.id,
            'to_location_id': sample_branch.id,
            'quantity': 20,
            'transaction_type': TransactionType.OUT
        }
        
        result = self.service.create_transaction(transaction_data)
        
        assert result is not None
        assert result['product_id'] == sample_product.id
        assert result['from_location_id'] == sample_branch.id
        assert result['to_location_id'] == sample_branch.id
        assert result['quantity'] == 20
        assert result['transaction_type'] == TransactionType.OUT
    
    def test_get_transactions_by_product(self, db_session, sample_transaction):
        """Test getting transactions by product."""
        result = self.service.get_transactions_by_product(sample_transaction.product_id)
        
        assert result is not None
        assert len(result) >= 1
        assert all(t.product_id == sample_transaction.product_id for t in result)
    
    def test_get_transactions_by_type(self, db_session, sample_transaction):
        """Test getting transactions by type."""
        result = self.service.get_transactions_by_type(sample_transaction.transaction_type)
        
        assert result is not None
        assert len(result) >= 1
        assert all(t.transaction_type == sample_transaction.transaction_type for t in result)


class TestCategoryService(BaseServiceTestCase):
    """Test cases for CategoryService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = CategoryService()
    
    def test_get_categories(self, db_session, sample_category):
        """Test getting categories."""
        # Create a filter object
        filter_obj = Mock()
        filter_obj.filters = []
        filter_obj.sorters = []
        filter_obj.page = 1
        filter_obj.per_page = 10
        
        result = self.service.get_categories(filter_obj)
        
        assert result is not None
        assert 'categories' in result
        assert 'total' in result
        assert 'page' in result
        assert 'per_page' in result
        assert len(result['categories']) >= 1
    
    def test_get_category_by_id(self, db_session, sample_category):
        """Test getting category by ID."""
        result = self.service.get_category_by_id(sample_category.id)
        
        assert result is not None
        assert result.id == sample_category.id
        assert result.code == sample_category.code
    
    def test_create_category(self, db_session):
        """Test creating a category."""
        category_data = {
            'code': 'NEW_CAT',
            'slug': 'new-category',
            'is_active': True,
            'is_featured': False
        }
        
        result = self.service.create_category(category_data)
        
        assert result is not None
        assert result['code'] == 'NEW_CAT'
        assert result['slug'] == 'new-category'
        assert result['is_active'] is True
        assert result['is_featured'] is False
    
    def test_update_category(self, db_session, sample_category):
        """Test updating a category."""
        update_data = {
            'is_featured': True
        }
        
        result = self.service.update_category(sample_category.id, update_data)
        
        assert result is not None
        assert result['is_featured'] is True
    
    def test_delete_category(self, db_session, sample_category):
        """Test deleting a category."""
        category_id = sample_category.id
        
        result = self.service.delete_category(category_id)
        
        assert result is True
        
        # Verify category is deleted
        deleted_category = self.service.get_category_by_id(category_id)
        assert deleted_category is None


class TestCustomerService(BaseServiceTestCase):
    """Test cases for CustomerService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = CustomerService()
    
    def test_get_customers(self, db_session, sample_customer):
        """Test getting customers."""
        # Create a filter object
        filter_obj = Mock()
        filter_obj.filters = []
        filter_obj.sorters = []
        filter_obj.page = 1
        filter_obj.per_page = 10
        
        result = self.service.get_customers(filter_obj)
        
        assert result is not None
        assert 'customers' in result
        assert 'total' in result
        assert 'page' in result
        assert 'per_page' in result
        assert len(result['customers']) >= 1
    
    def test_get_customer_by_id(self, db_session, sample_customer):
        """Test getting customer by ID."""
        result = self.service.get_customer_by_id(sample_customer.id)
        
        assert result is not None
        assert result.id == sample_customer.id
        assert result.email == sample_customer.email
    
    def test_create_customer(self, db_session, sample_user):
        """Test creating a customer."""
        customer_data = {
            'user_id': sample_user.id,
            'email': 'newcustomer@example.com',
            'mobile': '+1234567899',
            'customer_type': 'individual',
            'status': 'active'
        }
        
        result = self.service.create_customer(customer_data)
        
        assert result is not None
        assert result['user_id'] == sample_user.id
        assert result['email'] == 'newcustomer@example.com'
        assert result['mobile'] == '+1234567899'
        assert result['customer_type'] == 'individual'
        assert result['status'] == 'active'
    
    def test_update_customer(self, db_session, sample_customer):
        """Test updating a customer."""
        update_data = {
            'status': 'inactive'
        }
        
        result = self.service.update_customer(sample_customer.id, update_data)
        
        assert result is not None
        assert result['status'] == 'inactive'
    
    def test_delete_customer(self, db_session, sample_customer):
        """Test deleting a customer."""
        customer_id = sample_customer.id
        
        result = self.service.delete_customer(customer_id)
        
        assert result is True
        
        # Verify customer is deleted
        deleted_customer = self.service.get_customer_by_id(customer_id)
        assert deleted_customer is None
