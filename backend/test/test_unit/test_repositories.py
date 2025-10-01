"""
Unit tests for repository layer.

This module contains unit tests for all repository classes in the application.
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from test.base_test import BaseRepositoryTestCase
from app.repositories.base import BaseRepository
from app.product.repository import ProductRepository
from app.order.repository import OrderRepository
from app.users.repository import UserRepository
from app.category.repository import CategoryRepository
from app.customers.repository import CustomerRepository
from app.inventory.repository import InventoryRepository
from app.transaction.repository import TransactionRepository
from app.branch.repository import BranchRepository
from app.company.repository import CompanyRepository
from app.store.repository import StoreRepository
from app.expense.repository import ExpenseRepository
from app.common.enum import UserTypeEnum, LanguageEnum, OrderStatusEnum, TransactionType


class TestBaseRepository(BaseRepositoryTestCase):
    """Test cases for BaseRepository."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.repository = BaseRepository()
    
    def test_repository_initialization(self):
        """Test repository initialization."""
        assert self.repository is not None
        assert hasattr(self.repository, 'model_class')
        assert hasattr(self.repository, 'get_by_id')
        assert hasattr(self.repository, 'get_all')
        assert hasattr(self.repository, 'create')
        assert hasattr(self.repository, 'update')
        assert hasattr(self.repository, 'delete')
        assert hasattr(self.repository, 'exists')
        assert hasattr(self.repository, 'count')
        assert hasattr(self.repository, 'bulk_create')
        assert hasattr(self.repository, 'bulk_update')
        assert hasattr(self.repository, 'bulk_delete')


class TestUserRepository(BaseRepositoryTestCase):
    """Test cases for UserRepository."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.repository = UserRepository()
    
    def test_get_user_by_email(self, db_session, sample_user):
        """Test getting user by email."""
        result = self.repository.get_user_by_email(sample_user.email)
        
        assert result is not None
        assert result.id == sample_user.id
        assert result.email == sample_user.email
    
    def test_get_user_by_phone(self, db_session, sample_user):
        """Test getting user by phone."""
        result = self.repository.get_user_by_phone(sample_user.phone)
        
        assert result is not None
        assert result.id == sample_user.id
        assert result.phone == sample_user.phone
    
    def test_get_user_by_email_or_phone_email(self, db_session, sample_user):
        """Test getting user by email or phone (email)."""
        result = self.repository.get_user_by_email_or_phone(sample_user.email)
        
        assert result is not None
        assert result.id == sample_user.id
        assert result.email == sample_user.email
    
    def test_get_user_by_email_or_phone_phone(self, db_session, sample_user):
        """Test getting user by email or phone (phone)."""
        result = self.repository.get_user_by_email_or_phone(sample_user.phone)
        
        assert result is not None
        assert result.id == sample_user.id
        assert result.phone == sample_user.phone
    
    def test_get_user_by_user_id_and_type(self, db_session, sample_user):
        """Test getting user by user_id and type."""
        result = self.repository.get_user_by_user_id_and_type(sample_user.id, sample_user.user_type)
        
        assert result is not None
        assert result.id == sample_user.id
        assert result.user_type == sample_user.user_type
    
    def test_get_users_by_type(self, db_session, sample_user):
        """Test getting users by type."""
        result = self.repository.get_users_by_type(UserTypeEnum.USER)
        
        assert result is not None
        assert len(result) >= 1
        assert all(user.user_type == UserTypeEnum.USER for user in result)
    
    def test_get_users_by_role(self, db_session, sample_user, sample_role):
        """Test getting users by role."""
        # Add role to user
        sample_user.roles.append(sample_role)
        self.db_session.commit()
        
        result = self.repository.get_users_by_role(sample_role.id)
        
        assert result is not None
        assert len(result) >= 1
        assert any(user.id == sample_user.id for user in result)
    
    def test_get_user_with_roles(self, db_session, sample_user, sample_role):
        """Test getting user with roles."""
        # Add role to user
        sample_user.roles.append(sample_role)
        self.db_session.commit()
        
        result = self.repository.get_user_with_roles(sample_user.id)
        
        assert result is not None
        assert result.id == sample_user.id
        assert len(result.roles) >= 1
        assert any(role.id == sample_role.id for role in result.roles)
    
    def test_search_users(self, db_session, sample_user):
        """Test searching users."""
        result = self.repository.search_users('testuser')
        
        assert result is not None
        assert len(result) >= 1
        assert any('testuser' in user.username.lower() for user in result)
    
    def test_get_user_statistics(self, db_session, sample_user):
        """Test getting user statistics."""
        result = self.repository.get_user_statistics()
        
        assert result is not None
        assert 'total_users' in result
        assert 'active_users' in result
        assert 'inactive_users' in result
        assert 'users_by_type' in result
        assert 'users_by_language' in result
    
    def test_get_user_growth_analytics(self, db_session, sample_user):
        """Test getting user growth analytics."""
        result = self.repository.get_user_growth_analytics()
        
        assert result is not None
        assert 'growth_data' in result
        assert 'total_growth' in result
        assert 'monthly_growth' in result
    
    def test_get_user_engagement_metrics(self, db_session, sample_user):
        """Test getting user engagement metrics."""
        result = self.repository.get_user_engagement_metrics()
        
        assert result is not None
        assert 'engagement_score' in result
        assert 'active_users' in result
        assert 'inactive_users' in result
        assert 'engagement_trends' in result


class TestProductRepository(BaseRepositoryTestCase):
    """Test cases for ProductRepository."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.repository = ProductRepository()
    
    def test_get_products_with_category(self, db_session, sample_product, sample_category):
        """Test getting products with category."""
        # Create a filter object
        filter_obj = Mock()
        filter_obj.filters = []
        filter_obj.sorters = []
        filter_obj.page = 1
        filter_obj.per_page = 10
        
        result = self.repository.get_products_with_category(filter_obj)
        
        assert result is not None
        assert 'products' in result
        assert 'total' in result
        assert 'page' in result
        assert 'per_page' in result
        assert len(result['products']) >= 1
    
    def test_get_product_with_details(self, db_session, sample_product):
        """Test getting product with details."""
        result = self.repository.get_product_with_details(sample_product.id)
        
        assert result is not None
        assert result.id == sample_product.id
        assert result.code == sample_product.code
    
    def test_get_products_by_category(self, db_session, sample_product, sample_category):
        """Test getting products by category."""
        result = self.repository.get_products_by_category(sample_category.id)
        
        assert result is not None
        assert len(result) >= 1
        assert all(product.category_id == sample_category.id for product in result)
    
    def test_get_products_by_type(self, db_session, sample_product):
        """Test getting products by type."""
        result = self.repository.get_products_by_type(sample_product.product_type)
        
        assert result is not None
        assert len(result) >= 1
        assert all(product.product_type == sample_product.product_type for product in result)
    
    def test_search_products(self, db_session, sample_product):
        """Test searching products."""
        result = self.repository.search_products('TEST_PROD')
        
        assert result is not None
        assert len(result) >= 1
        assert any('TEST_PROD' in product.code for product in result)
    
    def test_get_featured_products(self, db_session, sample_product):
        """Test getting featured products."""
        # Make product featured
        sample_product.is_featured = True
        self.db_session.commit()
        
        result = self.repository.get_featured_products()
        
        assert result is not None
        assert len(result) >= 1
        assert all(product.is_featured for product in result)
    
    def test_get_products_by_price_range(self, db_session, sample_product):
        """Test getting products by price range."""
        result = self.repository.get_products_by_price_range(50.00, 150.00)
        
        assert result is not None
        assert len(result) >= 1
        assert all(50.00 <= product.base_price <= 150.00 for product in result)


class TestOrderRepository(BaseRepositoryTestCase):
    """Test cases for OrderRepository."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.repository = OrderRepository()
    
    def test_get_orders_with_customer(self, db_session, sample_order, sample_customer):
        """Test getting orders with customer."""
        # Create a filter object
        filter_obj = Mock()
        filter_obj.filters = []
        filter_obj.sorters = []
        filter_obj.page = 1
        filter_obj.per_page = 10
        
        result = self.repository.get_orders_with_customer(filter_obj)
        
        assert result is not None
        assert 'orders' in result
        assert 'total' in result
        assert 'page' in result
        assert 'per_page' in result
        assert len(result['orders']) >= 1
    
    def test_get_order_with_details(self, db_session, sample_order):
        """Test getting order with details."""
        result = self.repository.get_order_with_details(sample_order.id)
        
        assert result is not None
        assert result.id == sample_order.id
        assert result.order_number == sample_order.order_number
    
    def test_get_orders_by_customer(self, db_session, sample_order, sample_customer):
        """Test getting orders by customer."""
        result = self.repository.get_orders_by_customer(sample_customer.id)
        
        assert result is not None
        assert len(result) >= 1
        assert all(order.customer_id == sample_customer.id for order in result)
    
    def test_get_orders_by_status(self, db_session, sample_order):
        """Test getting orders by status."""
        result = self.repository.get_orders_by_status(sample_order.status)
        
        assert result is not None
        assert len(result) >= 1
        assert all(order.status == sample_order.status for order in result)
    
    def test_get_orders_by_date_range(self, db_session, sample_order):
        """Test getting orders by date range."""
        from datetime import datetime, timezone, timedelta
        
        start_date = datetime.now(timezone.utc) - timedelta(days=30)
        end_date = datetime.now(timezone.utc) + timedelta(days=30)
        
        result = self.repository.get_orders_by_date_range(start_date, end_date)
        
        assert result is not None
        assert len(result) >= 1
        assert all(start_date <= order.order_date <= end_date for order in result)
    
    def test_get_orders_by_payment_status(self, db_session, sample_order):
        """Test getting orders by payment status."""
        result = self.repository.get_orders_by_payment_status(sample_order.payment_status)
        
        assert result is not None
        assert len(result) >= 1
        assert all(order.payment_status == sample_order.payment_status for order in result)
    
    def test_search_orders(self, db_session, sample_order):
        """Test searching orders."""
        result = self.repository.search_orders('ORD-001')
        
        assert result is not None
        assert len(result) >= 1
        assert any('ORD-001' in order.order_number for order in result)


class TestCategoryRepository(BaseRepositoryTestCase):
    """Test cases for CategoryRepository."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.repository = CategoryRepository()
    
    def test_get_categories_with_products(self, db_session, sample_category, sample_product):
        """Test getting categories with products."""
        # Create a filter object
        filter_obj = Mock()
        filter_obj.filters = []
        filter_obj.sorters = []
        filter_obj.page = 1
        filter_obj.per_page = 10
        
        result = self.repository.get_categories_with_products(filter_obj)
        
        assert result is not None
        assert 'categories' in result
        assert 'total' in result
        assert 'page' in result
        assert 'per_page' in result
        assert len(result['categories']) >= 1
    
    def test_get_category_with_products(self, db_session, sample_category, sample_product):
        """Test getting category with products."""
        result = self.repository.get_category_with_products(sample_category.id)
        
        assert result is not None
        assert result.id == sample_category.id
        assert result.code == sample_category.code
    
    def test_get_active_categories(self, db_session, sample_category):
        """Test getting active categories."""
        result = self.repository.get_active_categories()
        
        assert result is not None
        assert len(result) >= 1
        assert all(category.is_active for category in result)
    
    def test_get_featured_categories(self, db_session, sample_category):
        """Test getting featured categories."""
        # Make category featured
        sample_category.is_featured = True
        self.db_session.commit()
        
        result = self.repository.get_featured_categories()
        
        assert result is not None
        assert len(result) >= 1
        assert all(category.is_featured for category in result)
    
    def test_get_categories_by_parent(self, db_session, sample_category):
        """Test getting categories by parent."""
        # Create child category
        child_category = self.repository.model_class(
            code='CHILD_CAT',
            slug='child-category',
            parent_id=sample_category.id,
            is_active=True
        )
        self.db_session.add(child_category)
        self.db_session.commit()
        
        result = self.repository.get_categories_by_parent(sample_category.id)
        
        assert result is not None
        assert len(result) >= 1
        assert all(category.parent_id == sample_category.id for category in result)
    
    def test_search_categories(self, db_session, sample_category):
        """Test searching categories."""
        result = self.repository.search_categories('TEST_CAT')
        
        assert result is not None
        assert len(result) >= 1
        assert any('TEST_CAT' in category.code for category in result)


class TestCustomerRepository(BaseRepositoryTestCase):
    """Test cases for CustomerRepository."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.repository = CustomerRepository()
    
    def test_get_customers_with_user(self, db_session, sample_customer, sample_user):
        """Test getting customers with user."""
        # Create a filter object
        filter_obj = Mock()
        filter_obj.filters = []
        filter_obj.sorters = []
        filter_obj.page = 1
        filter_obj.per_page = 10
        
        result = self.repository.get_customers_with_user(filter_obj)
        
        assert result is not None
        assert 'customers' in result
        assert 'total' in result
        assert 'page' in result
        assert 'per_page' in result
        assert len(result['customers']) >= 1
    
    def test_get_customer_with_user(self, db_session, sample_customer):
        """Test getting customer with user."""
        result = self.repository.get_customer_with_user(sample_customer.id)
        
        assert result is not None
        assert result.id == sample_customer.id
        assert result.email == sample_customer.email
    
    def test_get_customers_by_type(self, db_session, sample_customer):
        """Test getting customers by type."""
        result = self.repository.get_customers_by_type(sample_customer.customer_type)
        
        assert result is not None
        assert len(result) >= 1
        assert all(customer.customer_type == sample_customer.customer_type for customer in result)
    
    def test_get_customers_by_status(self, db_session, sample_customer):
        """Test getting customers by status."""
        result = self.repository.get_customers_by_status(sample_customer.status)
        
        assert result is not None
        assert len(result) >= 1
        assert all(customer.status == sample_customer.status for customer in result)
    
    def test_get_customers_by_city(self, db_session, sample_customer):
        """Test getting customers by city."""
        sample_customer.city = 'Test City'
        self.db_session.commit()
        
        result = self.repository.get_customers_by_city('Test City')
        
        assert result is not None
        assert len(result) >= 1
        assert all(customer.city == 'Test City' for customer in result)
    
    def test_search_customers(self, db_session, sample_customer):
        """Test searching customers."""
        result = self.repository.search_customers('customer@example.com')
        
        assert result is not None
        assert len(result) >= 1
        assert any('customer@example.com' in customer.email for customer in result)


class TestInventoryRepository(BaseRepositoryTestCase):
    """Test cases for InventoryRepository."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.repository = InventoryRepository()
    
    def test_get_inventory_with_details(self, db_session, sample_inventory, sample_product, sample_branch):
        """Test getting inventory with details."""
        # Create a filter object
        filter_obj = Mock()
        filter_obj.filters = []
        filter_obj.sorters = []
        filter_obj.page = 1
        filter_obj.per_page = 10
        
        result = self.repository.get_inventory_with_details(filter_obj)
        
        assert result is not None
        assert 'inventory' in result
        assert 'total' in result
        assert 'page' in result
        assert 'per_page' in result
        assert len(result['inventory']) >= 1
    
    def test_get_inventory_by_product(self, db_session, sample_inventory, sample_product):
        """Test getting inventory by product."""
        result = self.repository.get_inventory_by_product(sample_product.id)
        
        assert result is not None
        assert len(result) >= 1
        assert all(inv.product_id == sample_product.id for inv in result)
    
    def test_get_inventory_by_branch(self, db_session, sample_inventory, sample_branch):
        """Test getting inventory by branch."""
        result = self.repository.get_inventory_by_branch(sample_branch.id)
        
        assert result is not None
        assert len(result) >= 1
        assert all(inv.branch_id == sample_branch.id for inv in result)
    
    def test_get_low_stock_items(self, db_session, sample_inventory):
        """Test getting low stock items."""
        # Set quantity below alert threshold
        sample_inventory.quantity = 5
        self.db_session.commit()
        
        result = self.repository.get_low_stock_items()
        
        assert result is not None
        assert len(result) >= 1
        assert all(inv.quantity <= inv.quantity_alert for inv in result)
    
    def test_get_inventory_by_product_and_branch(self, db_session, sample_inventory, sample_product, sample_branch):
        """Test getting inventory by product and branch."""
        result = self.repository.get_inventory_by_product_and_branch(sample_product.id, sample_branch.id)
        
        assert result is not None
        assert result.product_id == sample_product.id
        assert result.branch_id == sample_branch.id
    
    def test_update_inventory_quantity(self, db_session, sample_inventory):
        """Test updating inventory quantity."""
        new_quantity = 150
        
        result = self.repository.update_inventory_quantity(sample_inventory.id, new_quantity)
        
        assert result is not None
        assert result.quantity == new_quantity
        
        # Verify in database
        updated_inventory = self.repository.get_by_id(sample_inventory.id)
        assert updated_inventory.quantity == new_quantity


class TestTransactionRepository(BaseRepositoryTestCase):
    """Test cases for TransactionRepository."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.repository = TransactionRepository()
    
    def test_get_transactions_with_details(self, db_session, sample_transaction, sample_product, sample_branch):
        """Test getting transactions with details."""
        # Create a filter object
        filter_obj = Mock()
        filter_obj.filters = []
        filter_obj.sorters = []
        filter_obj.page = 1
        filter_obj.per_page = 10
        
        result = self.repository.get_transactions_with_details(filter_obj)
        
        assert result is not None
        assert 'transactions' in result
        assert 'total' in result
        assert 'page' in result
        assert 'per_page' in result
        assert len(result['transactions']) >= 1
    
    def test_get_transactions_by_product(self, db_session, sample_transaction, sample_product):
        """Test getting transactions by product."""
        result = self.repository.get_transactions_by_product(sample_product.id)
        
        assert result is not None
        assert len(result) >= 1
        assert all(t.product_id == sample_product.id for t in result)
    
    def test_get_transactions_by_type(self, db_session, sample_transaction):
        """Test getting transactions by type."""
        result = self.repository.get_transactions_by_type(sample_transaction.transaction_type)
        
        assert result is not None
        assert len(result) >= 1
        assert all(t.transaction_type == sample_transaction.transaction_type for t in result)
    
    def test_get_transactions_by_location(self, db_session, sample_transaction, sample_branch):
        """Test getting transactions by location."""
        result = self.repository.get_transactions_by_location(sample_branch.id)
        
        assert result is not None
        assert len(result) >= 1
        assert all(t.from_location_id == sample_branch.id or t.to_location_id == sample_branch.id for t in result)
    
    def test_get_transactions_by_date_range(self, db_session, sample_transaction):
        """Test getting transactions by date range."""
        from datetime import datetime, timezone, timedelta
        
        start_date = datetime.now(timezone.utc) - timedelta(days=30)
        end_date = datetime.now(timezone.utc) + timedelta(days=30)
        
        result = self.repository.get_transactions_by_date_range(start_date, end_date)
        
        assert result is not None
        assert len(result) >= 1
        assert all(start_date <= t.transaction_date <= end_date for t in result)
    
    def test_get_transaction_summary(self, db_session, sample_transaction):
        """Test getting transaction summary."""
        result = self.repository.get_transaction_summary()
        
        assert result is not None
        assert 'total_transactions' in result
        assert 'transactions_by_type' in result
        assert 'total_quantity' in result


class TestBranchRepository(BaseRepositoryTestCase):
    """Test cases for BranchRepository."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.repository = BranchRepository()
    
    def test_get_branches_with_company(self, db_session, sample_branch, sample_company):
        """Test getting branches with company."""
        # Create a filter object
        filter_obj = Mock()
        filter_obj.filters = []
        filter_obj.sorters = []
        filter_obj.page = 1
        filter_obj.per_page = 10
        
        result = self.repository.get_branches_with_company(filter_obj)
        
        assert result is not None
        assert 'branches' in result
        assert 'total' in result
        assert 'page' in result
        assert 'per_page' in result
        assert len(result['branches']) >= 1
    
    def test_get_branch_with_company(self, db_session, sample_branch):
        """Test getting branch with company."""
        result = self.repository.get_branch_with_company(sample_branch.id)
        
        assert result is not None
        assert result.id == sample_branch.id
        assert result.name == sample_branch.name
    
    def test_get_branches_by_company(self, db_session, sample_branch, sample_company):
        """Test getting branches by company."""
        result = self.repository.get_branches_by_company(sample_company.id)
        
        assert result is not None
        assert len(result) >= 1
        assert all(branch.company_id == sample_company.id for branch in result)
    
    def test_get_active_branches(self, db_session, sample_branch):
        """Test getting active branches."""
        result = self.repository.get_active_branches()
        
        assert result is not None
        assert len(result) >= 1
        assert all(branch.is_active for branch in result)
    
    def test_get_branches_by_city(self, db_session, sample_branch):
        """Test getting branches by city."""
        sample_branch.city = 'Test City'
        self.db_session.commit()
        
        result = self.repository.get_branches_by_city('Test City')
        
        assert result is not None
        assert len(result) >= 1
        assert all(branch.city == 'Test City' for branch in result)
    
    def test_search_branches(self, db_session, sample_branch):
        """Test searching branches."""
        result = self.repository.search_branches('Test Branch')
        
        assert result is not None
        assert len(result) >= 1
        assert any('Test Branch' in branch.name for branch in result)


class TestCompanyRepository(BaseRepositoryTestCase):
    """Test cases for CompanyRepository."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.repository = CompanyRepository()
    
    def test_get_companies_with_branches(self, db_session, sample_company, sample_branch):
        """Test getting companies with branches."""
        # Create a filter object
        filter_obj = Mock()
        filter_obj.filters = []
        filter_obj.sorters = []
        filter_obj.page = 1
        filter_obj.per_page = 10
        
        result = self.repository.get_companies_with_branches(filter_obj)
        
        assert result is not None
        assert 'companies' in result
        assert 'total' in result
        assert 'page' in result
        assert 'per_page' in result
        assert len(result['companies']) >= 1
    
    def test_get_company_with_branches(self, db_session, sample_company):
        """Test getting company with branches."""
        result = self.repository.get_company_with_branches(sample_company.id)
        
        assert result is not None
        assert result.id == sample_company.id
        assert result.name == sample_company.name
    
    def test_get_active_companies(self, db_session, sample_company):
        """Test getting active companies."""
        result = self.repository.get_active_companies()
        
        assert result is not None
        assert len(result) >= 1
        assert all(company.is_active for company in result)
    
    def test_get_companies_by_country(self, db_session, sample_company):
        """Test getting companies by country."""
        result = self.repository.get_companies_by_country(sample_company.country)
        
        assert result is not None
        assert len(result) >= 1
        assert all(company.country == sample_company.country for company in result)
    
    def test_search_companies(self, db_session, sample_company):
        """Test searching companies."""
        result = self.repository.search_companies('Test Company')
        
        assert result is not None
        assert len(result) >= 1
        assert any('Test Company' in company.name for company in result)


class TestStoreRepository(BaseRepositoryTestCase):
    """Test cases for StoreRepository."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.repository = StoreRepository()
    
    def test_get_stores_with_branch(self, db_session, sample_store, sample_branch):
        """Test getting stores with branch."""
        # Create a filter object
        filter_obj = Mock()
        filter_obj.filters = []
        filter_obj.sorters = []
        filter_obj.page = 1
        filter_obj.per_page = 10
        
        result = self.repository.get_stores_with_branch(filter_obj)
        
        assert result is not None
        assert 'stores' in result
        assert 'total' in result
        assert 'page' in result
        assert 'per_page' in result
        assert len(result['stores']) >= 1
    
    def test_get_store_with_branch(self, db_session, sample_store):
        """Test getting store with branch."""
        result = self.repository.get_store_with_branch(sample_store.id)
        
        assert result is not None
        assert result.id == sample_store.id
        assert result.name == sample_store.name
    
    def test_get_stores_by_branch(self, db_session, sample_store, sample_branch):
        """Test getting stores by branch."""
        result = self.repository.get_stores_by_branch(sample_branch.id)
        
        assert result is not None
        assert len(result) >= 1
        assert all(store.branch_id == sample_branch.id for store in result)
    
    def test_get_active_stores(self, db_session, sample_store):
        """Test getting active stores."""
        result = self.repository.get_active_stores()
        
        assert result is not None
        assert len(result) >= 1
        assert all(store.is_active for store in result)
    
    def test_get_stores_by_city(self, db_session, sample_store):
        """Test getting stores by city."""
        sample_store.city = 'Store City'
        self.db_session.commit()
        
        result = self.repository.get_stores_by_city('Store City')
        
        assert result is not None
        assert len(result) >= 1
        assert all(store.city == 'Store City' for store in result)
    
    def test_search_stores(self, db_session, sample_store):
        """Test searching stores."""
        result = self.repository.search_stores('Test Store')
        
        assert result is not None
        assert len(result) >= 1
        assert any('Test Store' in store.name for store in result)


class TestExpenseRepository(BaseRepositoryTestCase):
    """Test cases for ExpenseRepository."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.repository = ExpenseRepository()
    
    def test_get_expenses_with_details(self, db_session, sample_expense, sample_expense_category, sample_branch):
        """Test getting expenses with details."""
        # Create a filter object
        filter_obj = Mock()
        filter_obj.filters = []
        filter_obj.sorters = []
        filter_obj.page = 1
        filter_obj.per_page = 10
        
        result = self.repository.get_expenses_with_details(filter_obj)
        
        assert result is not None
        assert 'expenses' in result
        assert 'total' in result
        assert 'page' in result
        assert 'per_page' in result
        assert len(result['expenses']) >= 1
    
    def test_get_expense_with_details(self, db_session, sample_expense):
        """Test getting expense with details."""
        result = self.repository.get_expense_with_details(sample_expense.id)
        
        assert result is not None
        assert result.id == sample_expense.id
        assert result.amount == sample_expense.amount
    
    def test_get_expenses_by_category(self, db_session, sample_expense, sample_expense_category):
        """Test getting expenses by category."""
        result = self.repository.get_expenses_by_category(sample_expense_category.id)
        
        assert result is not None
        assert len(result) >= 1
        assert all(expense.category_id == sample_expense_category.id for expense in result)
    
    def test_get_expenses_by_branch(self, db_session, sample_expense, sample_branch):
        """Test getting expenses by branch."""
        result = self.repository.get_expenses_by_branch(sample_branch.id)
        
        assert result is not None
        assert len(result) >= 1
        assert all(expense.branch_id == sample_branch.id for expense in result)
    
    def test_get_expenses_by_status(self, db_session, sample_expense):
        """Test getting expenses by status."""
        result = self.repository.get_expenses_by_status(sample_expense.status)
        
        assert result is not None
        assert len(result) >= 1
        assert all(expense.status == sample_expense.status for expense in result)
    
    def test_get_expenses_by_amount_range(self, db_session, sample_expense):
        """Test getting expenses by amount range."""
        result = self.repository.get_expenses_by_amount_range(400.00, 600.00)
        
        assert result is not None
        assert len(result) >= 1
        assert all(400.00 <= expense.amount <= 600.00 for expense in result)
    
    def test_get_expense_summary(self, db_session, sample_expense):
        """Test getting expense summary."""
        result = self.repository.get_expense_summary()
        
        assert result is not None
        assert 'total_expenses' in result
        assert 'expenses_by_category' in result
        assert 'expenses_by_status' in result
        assert 'total_amount' in result
