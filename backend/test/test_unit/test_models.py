"""
Unit tests for database models.

This module contains unit tests for all database models in the application.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash

from test.base_test import BaseModelTestCase
from app.users.model import User
from app.product.model import Product
from app.category.model import Category
from app.order.model import Order
from app.customers.model import Customer
from app.inventory.model import Inventory
from app.transaction.model import Transaction
from app.branch.model import Branch
from app.company.model import Company
from app.store.model import Store
from app.expense.model import Expense, ExpenseCategory
from app.financial.model import FiscalYear, FiscalPeriod
from app.rating.model import Rating
from app.medias.model import Media
from app.address.model import ShippingAddress
from app.staff.model import Staff
from app.users.model import Role, Permission, UserRoles, RolePermission
from app.common.enum import UserTypeEnum, LanguageEnum, OrderStatusEnum, TransactionType


class TestUserModel(BaseModelTestCase):
    """Test cases for User model."""
    
    def test_user_creation(self, db_session):
        """Test creating a user."""
        user = User(
            username='testuser',
            phone='+1234567890',
            email='test@example.com',
            user_type=UserTypeEnum.USER,
            language=LanguageEnum.ENGLISH,
            password='testpassword',
            active=True
        )
        
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.username == 'testuser'
        assert user.phone == '+1234567890'
        assert user.email == 'test@example.com'
        assert user.user_type == UserTypeEnum.USER
        assert user.language == LanguageEnum.ENGLISH
        assert user.active is True
        assert user.create_date is not None
        assert user.modified_date is not None
    
    def test_user_password_hashing(self, db_session):
        """Test password hashing."""
        user = User(
            username='testuser',
            phone='+1234567890',
            password='testpassword'
        )
        
        db_session.add(user)
        db_session.commit()
        
        assert check_password_hash(user.password, 'testpassword')
        assert not check_password_hash(user.password, 'wrongpassword')
    
    def test_user_unique_constraints(self, db_session):
        """Test unique constraints on username, phone, and email."""
        # Create first user
        user1 = User(
            username='testuser',
            phone='+1234567890',
            email='test@example.com',
            password='password'
        )
        db_session.add(user1)
        db_session.commit()
        
        # Try to create user with same username
        user2 = User(
            username='testuser',
            phone='+1234567891',
            email='test2@example.com',
            password='password'
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
        
        # Try to create user with same phone
        user3 = User(
            username='testuser2',
            phone='+1234567890',
            email='test3@example.com',
            password='password'
        )
        db_session.add(user3)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
        
        # Try to create user with same email
        user4 = User(
            username='testuser3',
            phone='+1234567892',
            email='test@example.com',
            password='password'
        )
        db_session.add(user4)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_json_serialization(self, db_session):
        """Test user JSON serialization."""
        user = User(
            username='testuser',
            phone='+1234567890',
            email='test@example.com',
            user_type=UserTypeEnum.USER,
            language=LanguageEnum.ENGLISH,
            password='testpassword',
            active=True
        )
        
        db_session.add(user)
        db_session.commit()
        
        user_json = user.json()
        
        assert 'id' in user_json
        assert 'username' in user_json
        assert 'phone' in user_json
        assert 'email' in user_json
        assert 'user_type' in user_json
        assert 'language' in user_json
        assert 'active' in user_json
        assert 'create_date' in user_json
        assert 'modified_date' in user_json


class TestProductModel(BaseModelTestCase):
    """Test cases for Product model."""
    
    def test_product_creation(self, db_session, sample_category):
        """Test creating a product."""
        product = Product(
            code='TEST_PROD',
            sku='TEST-SKU-001',
            product_type='service',
            category_id=sample_category.id,
            base_price=100.00,
            currency='USD',
            is_dynamic_pricing=False
        )
        
        db_session.add(product)
        db_session.commit()
        
        assert product.id is not None
        assert product.code == 'TEST_PROD'
        assert product.sku == 'TEST-SKU-001'
        assert product.product_type == 'service'
        assert product.category_id == sample_category.id
        assert product.base_price == 100.00
        assert product.currency == 'USD'
        assert product.is_dynamic_pricing is False
    
    def test_product_unique_constraints(self, db_session, sample_category):
        """Test unique constraints on code and sku."""
        # Create first product
        product1 = Product(
            code='TEST_PROD',
            sku='TEST-SKU-001',
            product_type='service',
            category_id=sample_category.id,
            base_price=100.00,
            currency='USD'
        )
        db_session.add(product1)
        db_session.commit()
        
        # Try to create product with same code
        product2 = Product(
            code='TEST_PROD',
            sku='TEST-SKU-002',
            product_type='service',
            category_id=sample_category.id,
            base_price=200.00,
            currency='USD'
        )
        db_session.add(product2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
        
        # Try to create product with same sku
        product3 = Product(
            code='TEST_PROD2',
            sku='TEST-SKU-001',
            product_type='service',
            category_id=sample_category.id,
            base_price=300.00,
            currency='USD'
        )
        db_session.add(product3)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_product_relationships(self, db_session, sample_category):
        """Test product relationships."""
        product = Product(
            code='TEST_PROD',
            sku='TEST-SKU-001',
            product_type='service',
            category_id=sample_category.id,
            base_price=100.00,
            currency='USD'
        )
        
        db_session.add(product)
        db_session.commit()
        
        # Test category relationship
        assert product.category is not None
        assert product.category.id == sample_category.id


class TestCategoryModel(BaseModelTestCase):
    """Test cases for Category model."""
    
    def test_category_creation(self, db_session):
        """Test creating a category."""
        category = Category(
            code='TEST_CAT',
            slug='test-category',
            is_active=True,
            is_featured=False
        )
        
        db_session.add(category)
        db_session.commit()
        
        assert category.id is not None
        assert category.code == 'TEST_CAT'
        assert category.slug == 'test-category'
        assert category.is_active is True
        assert category.is_featured is False
    
    def test_category_unique_constraints(self, db_session):
        """Test unique constraints on code and slug."""
        # Create first category
        category1 = Category(
            code='TEST_CAT',
            slug='test-category',
            is_active=True
        )
        db_session.add(category1)
        db_session.commit()
        
        # Try to create category with same code
        category2 = Category(
            code='TEST_CAT',
            slug='test-category-2',
            is_active=True
        )
        db_session.add(category2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
        
        # Try to create category with same slug
        category3 = Category(
            code='TEST_CAT2',
            slug='test-category',
            is_active=True
        )
        db_session.add(category3)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_category_hierarchy(self, db_session):
        """Test category hierarchy with parent-child relationships."""
        # Create parent category
        parent_category = Category(
            code='PARENT_CAT',
            slug='parent-category',
            is_active=True
        )
        db_session.add(parent_category)
        db_session.commit()
        
        # Create child category
        child_category = Category(
            code='CHILD_CAT',
            slug='child-category',
            parent_id=parent_category.id,
            is_active=True
        )
        db_session.add(child_category)
        db_session.commit()
        
        assert child_category.parent_id == parent_category.id
        assert child_category.parent is not None
        assert child_category.parent.id == parent_category.id


class TestOrderModel(BaseModelTestCase):
    """Test cases for Order model."""
    
    def test_order_creation(self, db_session, sample_customer):
        """Test creating an order."""
        order = Order(
            order_number='ORD-001',
            customer_id=sample_customer.id,
            status=OrderStatusEnum.PENDING,
            order_type='print_service',
            subtotal=100.00,
            total_amount=100.00,
            currency='USD',
            payment_status='pending'
        )
        
        db_session.add(order)
        db_session.commit()
        
        assert order.id is not None
        assert order.order_number == 'ORD-001'
        assert order.customer_id == sample_customer.id
        assert order.status == OrderStatusEnum.PENDING
        assert order.order_type == 'print_service'
        assert order.subtotal == 100.00
        assert order.total_amount == 100.00
        assert order.currency == 'USD'
        assert order.payment_status == 'pending'
    
    def test_order_unique_constraints(self, db_session, sample_customer):
        """Test unique constraint on order_number."""
        # Create first order
        order1 = Order(
            order_number='ORD-001',
            customer_id=sample_customer.id,
            status=OrderStatusEnum.PENDING,
            order_type='print_service',
            subtotal=100.00,
            total_amount=100.00,
            currency='USD'
        )
        db_session.add(order1)
        db_session.commit()
        
        # Try to create order with same order_number
        order2 = Order(
            order_number='ORD-001',
            customer_id=sample_customer.id,
            status=OrderStatusEnum.PENDING,
            order_type='print_service',
            subtotal=200.00,
            total_amount=200.00,
            currency='USD'
        )
        db_session.add(order2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_order_relationships(self, db_session, sample_customer):
        """Test order relationships."""
        order = Order(
            order_number='ORD-001',
            customer_id=sample_customer.id,
            status=OrderStatusEnum.PENDING,
            order_type='print_service',
            subtotal=100.00,
            total_amount=100.00,
            currency='USD'
        )
        
        db_session.add(order)
        db_session.commit()
        
        # Test customer relationship
        assert order.customer is not None
        assert order.customer.id == sample_customer.id


class TestInventoryModel(BaseModelTestCase):
    """Test cases for Inventory model."""
    
    def test_inventory_creation(self, db_session, sample_product, sample_branch):
        """Test creating an inventory record."""
        inventory = Inventory(
            product_id=sample_product.id,
            branch_id=sample_branch.id,
            quantity=100,
            quantity_alert=10
        )
        
        db_session.add(inventory)
        db_session.commit()
        
        assert inventory.id is not None
        assert inventory.product_id == sample_product.id
        assert inventory.branch_id == sample_branch.id
        assert inventory.quantity == 100
        assert inventory.quantity_alert == 10
    
    def test_inventory_relationships(self, db_session, sample_product, sample_branch):
        """Test inventory relationships."""
        inventory = Inventory(
            product_id=sample_product.id,
            branch_id=sample_branch.id,
            quantity=100,
            quantity_alert=10
        )
        
        db_session.add(inventory)
        db_session.commit()
        
        # Test product relationship
        assert inventory.product is not None
        assert inventory.product.id == sample_product.id
        
        # Test branch relationship
        assert inventory.branch is not None
        assert inventory.branch.id == sample_branch.id


class TestTransactionModel(BaseModelTestCase):
    """Test cases for Transaction model."""
    
    def test_transaction_creation(self, db_session, sample_product, sample_branch):
        """Test creating a transaction."""
        transaction = Transaction(
            product_id=sample_product.id,
            from_location_id=sample_branch.id,
            to_location_id=sample_branch.id,
            quantity=10,
            transaction_type=TransactionType.IN
        )
        
        db_session.add(transaction)
        db_session.commit()
        
        assert transaction.id is not None
        assert transaction.product_id == sample_product.id
        assert transaction.from_location_id == sample_branch.id
        assert transaction.to_location_id == sample_branch.id
        assert transaction.quantity == 10
        assert transaction.transaction_type == TransactionType.IN
    
    def test_transaction_relationships(self, db_session, sample_product, sample_branch):
        """Test transaction relationships."""
        transaction = Transaction(
            product_id=sample_product.id,
            from_location_id=sample_branch.id,
            to_location_id=sample_branch.id,
            quantity=10,
            transaction_type=TransactionType.IN
        )
        
        db_session.add(transaction)
        db_session.commit()
        
        # Test product relationship
        assert transaction.product is not None
        assert transaction.product.id == sample_product.id
        
        # Test from_location relationship
        assert transaction.from_location is not None
        assert transaction.from_location.id == sample_branch.id
        
        # Test to_location relationship
        assert transaction.to_location is not None
        assert transaction.to_location.id == sample_branch.id


class TestCompanyModel(BaseModelTestCase):
    """Test cases for Company model."""
    
    def test_company_creation(self, db_session):
        """Test creating a company."""
        company = Company(
            name='Test Company',
            email='company@example.com',
            phone='+1234567890',
            country='US',
            is_active=True
        )
        
        db_session.add(company)
        db_session.commit()
        
        assert company.id is not None
        assert company.name == 'Test Company'
        assert company.email == 'company@example.com'
        assert company.phone == '+1234567890'
        assert company.country == 'US'
        assert company.is_active is True


class TestBranchModel(BaseModelTestCase):
    """Test cases for Branch model."""
    
    def test_branch_creation(self, db_session, sample_company):
        """Test creating a branch."""
        branch = Branch(
            company_id=sample_company.id,
            name='Test Branch',
            address='123 Test Street',
            city='Test City',
            country='US',
            is_active=True
        )
        
        db_session.add(branch)
        db_session.commit()
        
        assert branch.id is not None
        assert branch.company_id == sample_company.id
        assert branch.name == 'Test Branch'
        assert branch.address == '123 Test Street'
        assert branch.city == 'Test City'
        assert branch.country == 'US'
        assert branch.is_active is True
    
    def test_branch_relationships(self, db_session, sample_company):
        """Test branch relationships."""
        branch = Branch(
            company_id=sample_company.id,
            name='Test Branch',
            address='123 Test Street',
            city='Test City',
            country='US',
            is_active=True
        )
        
        db_session.add(branch)
        db_session.commit()
        
        # Test company relationship
        assert branch.company is not None
        assert branch.company.id == sample_company.id


class TestStoreModel(BaseModelTestCase):
    """Test cases for Store model."""
    
    def test_store_creation(self, db_session, sample_branch):
        """Test creating a store."""
        store = Store(
            branch_id=sample_branch.id,
            name='Test Store',
            address='456 Store Street',
            city='Store City',
            country='US',
            is_active=True
        )
        
        db_session.add(store)
        db_session.commit()
        
        assert store.id is not None
        assert store.branch_id == sample_branch.id
        assert store.name == 'Test Store'
        assert store.address == '456 Store Street'
        assert store.city == 'Store City'
        assert store.country == 'US'
        assert store.is_active is True
    
    def test_store_relationships(self, db_session, sample_branch):
        """Test store relationships."""
        store = Store(
            branch_id=sample_branch.id,
            name='Test Store',
            address='456 Store Street',
            city='Store City',
            country='US',
            is_active=True
        )
        
        db_session.add(store)
        db_session.commit()
        
        # Test branch relationship
        assert store.branch is not None
        assert store.branch.id == sample_branch.id


class TestExpenseModel(BaseModelTestCase):
    """Test cases for Expense model."""
    
    def test_expense_creation(self, db_session, sample_expense_category, sample_branch):
        """Test creating an expense."""
        expense = Expense(
            category_id=sample_expense_category.id,
            branch_id=sample_branch.id,
            amount=500.00,
            currency='USD',
            status='pending',
            description='Test expense'
        )
        
        db_session.add(expense)
        db_session.commit()
        
        assert expense.id is not None
        assert expense.category_id == sample_expense_category.id
        assert expense.branch_id == sample_branch.id
        assert expense.amount == 500.00
        assert expense.currency == 'USD'
        assert expense.status == 'pending'
        assert expense.description == 'Test expense'
    
    def test_expense_relationships(self, db_session, sample_expense_category, sample_branch):
        """Test expense relationships."""
        expense = Expense(
            category_id=sample_expense_category.id,
            branch_id=sample_branch.id,
            amount=500.00,
            currency='USD',
            status='pending',
            description='Test expense'
        )
        
        db_session.add(expense)
        db_session.commit()
        
        # Test category relationship
        assert expense.category is not None
        assert expense.category.id == sample_expense_category.id
        
        # Test branch relationship
        assert expense.branch is not None
        assert expense.branch.id == sample_branch.id


class TestFiscalYearModel(BaseModelTestCase):
    """Test cases for FiscalYear model."""
    
    def test_fiscal_year_creation(self, db_session):
        """Test creating a fiscal year."""
        fiscal_year = FiscalYear(
            name='2024',
            start_date='2024-01-01',
            end_date='2024-12-31',
            is_active=True
        )
        
        db_session.add(fiscal_year)
        db_session.commit()
        
        assert fiscal_year.id is not None
        assert fiscal_year.name == '2024'
        assert fiscal_year.start_date == '2024-01-01'
        assert fiscal_year.end_date == '2024-12-31'
        assert fiscal_year.is_active is True


class TestRatingModel(BaseModelTestCase):
    """Test cases for Rating model."""
    
    def test_rating_creation(self, db_session, sample_user, sample_product, sample_order):
        """Test creating a rating."""
        rating = Rating(
            user_id=sample_user.id,
            product_id=sample_product.id,
            order_id=sample_order.id,
            rating=5,
            comment='Great product!'
        )
        
        db_session.add(rating)
        db_session.commit()
        
        assert rating.id is not None
        assert rating.user_id == sample_user.id
        assert rating.product_id == sample_product.id
        assert rating.order_id == sample_order.id
        assert rating.rating == 5
        assert rating.comment == 'Great product!'
    
    def test_rating_relationships(self, db_session, sample_user, sample_product, sample_order):
        """Test rating relationships."""
        rating = Rating(
            user_id=sample_user.id,
            product_id=sample_product.id,
            order_id=sample_order.id,
            rating=5,
            comment='Great product!'
        )
        
        db_session.add(rating)
        db_session.commit()
        
        # Test user relationship
        assert rating.user is not None
        assert rating.user.id == sample_user.id
        
        # Test product relationship
        assert rating.product is not None
        assert rating.product.id == sample_product.id
        
        # Test order relationship
        assert rating.order is not None
        assert rating.order.id == sample_order.id


class TestRoleModel(BaseModelTestCase):
    """Test cases for Role model."""
    
    def test_role_creation(self, db_session):
        """Test creating a role."""
        role = Role(
            name='test_role',
            description='Test role for testing',
            is_active=True
        )
        
        db_session.add(role)
        db_session.commit()
        
        assert role.id is not None
        assert role.name == 'test_role'
        assert role.description == 'Test role for testing'
        assert role.is_active is True


class TestPermissionModel(BaseModelTestCase):
    """Test cases for Permission model."""
    
    def test_permission_creation(self, db_session):
        """Test creating a permission."""
        permission = Permission(
            name='test_permission',
            resource='test_resource',
            action='test_action',
            description='Test permission for testing'
        )
        
        db_session.add(permission)
        db_session.commit()
        
        assert permission.id is not None
        assert permission.name == 'test_permission'
        assert permission.resource == 'test_resource'
        assert permission.action == 'test_action'
        assert permission.description == 'Test permission for testing'
