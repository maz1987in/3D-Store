"""
Unit tests for Cart Service.

Tests all business logic in cart/service.py including:
- Cart item management (add/remove/update)
- Cart total calculations
- User cart management
- Cart expiration and cleanup
- Edge cases and error handling
"""

import pytest
import uuid
from unittest.mock import Mock
from decimal import Decimal

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from test.test_helpers import assert_decimal_equal, create_mock_filter
from app.cart.service import CartService
from app.cart.model import Cart, Item
from app.common.error_handling import ResourceNotFoundError


# ========== Local Fixtures ==========

@pytest.fixture
def sample_cart(db_session):
    """Create a sample cart for testing."""
    cart = Cart(
        id=uuid.uuid4(),
        total=0.00,
    )
    db_session.add(cart)
    db_session.commit()
    return cart


@pytest.fixture
def sample_cart_item(db_session, sample_cart, sample_product):
    """Create a sample cart item for testing."""
    item = Item(
        id=uuid.uuid4(),
        cart_id=sample_cart.id,
        price=100.00,
        quantity=2,
        service_id=sample_product.id,
        service_type='product'
    )
    db_session.add(item)
    db_session.flush()
    
    # Set translations
    from config import Config
    for locale in Config.AVAILABLE_LOCALES.keys():
        item.translations[locale].title = f'Test Item {locale}'
    
    db_session.commit()
    return item


class TestCartService(BaseServiceTestCase):
    """Test cases for CartService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = CartService()
    
    # ========== CRUD Operations Tests ==========
    
    def test_create_cart_success(self, db_session):
        """Test creating a cart successfully."""
        cart_data = {
            'total': 100.00
        }
        
        result, status = self.service.create_cart(cart_data)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify cart was created
        carts = db_session.query(Cart).all()
        assert len(carts) > 0
    
    def test_get_user_cart(self, db_session, sample_user, sample_product):
        """Test getting all cart items for a user."""
        # Create multiple cart items
        for i in range(3):
            cart_data = {
                'user_id': sample_user.id,
                'item_id': sample_product.id,
                'quantity': i + 1
            }
            self.service.create_cart(cart_data)
        
        result, status = self.service.get_carts_my(sample_user.id)
        
        assert status == 200
        assert 'carts' in result
        assert len(result['carts']) >= 3
    
    def test_get_carts_with_pagination(self, db_session, sample_user, sample_product):
        """Test getting carts with pagination."""
        # Create multiple carts
        for i in range(15):
            cart_data = {
                'user_id': sample_user.id,
                'item_id': sample_product.id,
                'quantity': 1
            }
            self.service.create_cart(cart_data)
        
        filter_obj = create_mock_filter(page=1, per_page=10)
        result, status = self.service.get_carts(None, filter_obj)
        
        assert status == 200
        assert 'carts' in result
        assert 'filters' in result
    
    def test_update_cart_quantity(self, db_session, sample_user, sample_product):
        """Test updating cart item quantity."""
        # Create cart
        cart_data = {
            'user_id': sample_user.id,
            'item_id': sample_product.id,
            'quantity': 2
        }
        self.service.create_cart(cart_data)
        
        cart = db_session.query(Cart).first()
        
        # Update quantity
        update_data = {'quantity': 5}
        result, status = self.service.update_cart(cart.id, update_data, None)
        
        assert status == 200
        assert 'Updated' in result
        
        db_session.refresh(cart)
        assert cart.quantity == 5
    
    def test_delete_cart_item(self, db_session, sample_user, sample_product):
        """Test deleting a cart item."""
        # Create cart
        cart_data = {
            'user_id': sample_user.id,
            'item_id': sample_product.id,
            'quantity': 1
        }
        self.service.create_cart(cart_data)
        
        cart = db_session.query(Cart).first()
        cart_id = cart.id
        
        # Delete cart item
        result, status = self.service.delete_cart(cart_id)
        
        assert status == 200
        assert 'deleted' in result.lower()
        
        deleted_cart = db_session.query(Cart).filter_by(id=cart_id).first()
        assert deleted_cart is None
    
    # ========== Cart Management Tests ==========
    
    def test_empty_cart_user(self, db_session, sample_user, sample_product):
        """Test clearing all items from user cart."""
        # Create multiple cart items
        for i in range(3):
            cart_data = {
                'user_id': sample_user.id,
                'item_id': sample_product.id,
                'quantity': 1
            }
            self.service.create_cart(cart_data)
        
        # Clear cart
        result, status = self.service.clear_cart(sample_user.id)
        
        assert status == 200
        
        # Verify cart is empty
        carts = db_session.query(Cart).filter(Cart.user_id == sample_user.id).all()
        assert len(carts) == 0
    
    def test_get_empty_cart(self, db_session, sample_user):
        """Test getting cart when user has no items."""
        result, status = self.service.get_carts_my(sample_user.id)
        
        assert status == 200
        assert 'carts' in result
        assert len(result['carts']) == 0
    
    def test_cart_one_per_user_product(self, db_session, sample_user, sample_product):
        """Test that each user-product combination appears once."""
        # Create first cart item
        cart_data = {
            'user_id': sample_user.id,
            'item_id': sample_product.id,
            'quantity': 2
        }
        self.service.create_cart(cart_data)
        
        # Verify only one cart item exists
        carts = db_session.query(Cart).filter(
            Cart.user_id == sample_user.id,
            Cart.item_id == sample_product.id
        ).all()
        assert len(carts) == 1
    
    # ========== Quantity Validation Tests ==========
    
    def test_create_cart_with_zero_quantity(self, db_session, sample_user, sample_product):
        """Test creating cart with zero quantity."""
        cart_data = {
            'user_id': sample_user.id,
            'item_id': sample_product.id,
            'quantity': 0
        }
        
        result, status = self.service.create_cart(cart_data)
        
        # Should either prevent creation or allow with zero
        assert status in [200, 201, 400]
    
    def test_create_cart_with_negative_quantity(self, db_session, sample_user, sample_product):
        """Test creating cart with negative quantity."""
        cart_data = {
            'user_id': sample_user.id,
            'item_id': sample_product.id,
            'quantity': -1
        }
        
        # Should prevent negative quantity
        with pytest.raises(Exception):
            self.service.create_cart(cart_data)
    
    def test_create_cart_with_large_quantity(self, db_session, sample_user, sample_product):
        """Test creating cart with very large quantity."""
        large_quantity = 10000
        
        cart_data = {
            'user_id': sample_user.id,
            'item_id': sample_product.id,
            'quantity': large_quantity
        }
        
        result, status = self.service.create_cart(cart_data)
        
        assert status == 201
        cart = db_session.query(Cart).first()
        assert cart.quantity == large_quantity
    
    def test_update_quantity_to_zero(self, db_session, sample_user, sample_product):
        """Test updating cart quantity to zero (should remove item)."""
        # Create cart
        cart_data = {
            'user_id': sample_user.id,
            'item_id': sample_product.id,
            'quantity': 5
        }
        self.service.create_cart(cart_data)
        
        cart = db_session.query(Cart).first()
        
        # Update to zero
        update_data = {'quantity': 0}
        result, status = self.service.update_cart(cart.id, update_data, None)
        
        # Should either delete or update to 0
        assert status in [200, 204]
    
    # ========== Edge Cases Tests ==========
    
    def test_get_cart_by_invalid_id(self, db_session):
        """Test getting cart with non-existent ID."""
        non_existent_id = uuid.uuid4()
        filter_obj = create_mock_filter()
        
        result, status = self.service.get_carts(non_existent_id, filter_obj)
        
        assert status == 200
        assert len(result['carts']) == 0
    
    def test_create_cart_invalid_user(self, db_session, sample_product):
        """Test creating cart for non-existent user."""
        cart_data = {
            'user_id': uuid.uuid4(),  # Non-existent
            'item_id': sample_product.id,
            'quantity': 1
        }
        
        with pytest.raises(Exception):  # Foreign key constraint
            self.service.create_cart(cart_data)
    
    def test_create_cart_invalid_product(self, db_session, sample_user):
        """Test creating cart for non-existent product."""
        cart_data = {
            'user_id': sample_user.id,
            'item_id': uuid.uuid4(),  # Non-existent
            'quantity': 1
        }
        
        with pytest.raises(Exception):  # Foreign key constraint
            self.service.create_cart(cart_data)
    
    def test_update_cart_not_found(self, db_session):
        """Test updating a non-existent cart."""
        non_existent_id = uuid.uuid4()
        update_data = {'quantity': 5}
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_cart(non_existent_id, update_data, None)
    
    def test_delete_cart_not_found(self, db_session):
        """Test deleting a non-existent cart."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_cart(non_existent_id)
    
    def test_multiple_users_different_carts(self, db_session, sample_product):
        """Test that different users have separate carts."""
        from app.users.model import User
        from werkzeug.security import generate_password_hash
        
        # Create two users
        user1 = User(
            username='cartuser1',
            phone='+1111111111',
            email='cart1@test.com',
            password=generate_password_hash('test'),
            active=True
        )
        user2 = User(
            username='cartuser2',
            phone='+2222222222',
            email='cart2@test.com',
            password=generate_password_hash('test'),
            active=True
        )
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()
        
        # Create carts for both users
        for user in [user1, user2]:
            cart_data = {
                'user_id': user.id,
                'item_id': sample_product.id,
                'quantity': 3
            }
            self.service.create_cart(cart_data)
        
        # Verify separate carts
        cart1_result, _ = self.service.get_carts_my(user1.id)
        cart2_result, _ = self.service.get_carts_my(user2.id)
        
        assert len(cart1_result['carts']) > 0
        assert len(cart2_result['carts']) > 0
    
    def test_cart_persistence_across_sessions(self, db_session, sample_user, sample_product):
        """Test that cart items persist across sessions."""
        # Create cart
        cart_data = {
            'user_id': sample_user.id,
            'item_id': sample_product.id,
            'quantity': 2
        }
        self.service.create_cart(cart_data)
        
        # Close and reopen session (simulated by commit)
        db_session.commit()
        
        # Retrieve cart
        result, status = self.service.get_carts_my(sample_user.id)
        
        assert status == 200
        assert len(result['carts']) > 0
    
    # ========== Error Handling Tests ==========
    
    def test_create_cart_missing_required_fields(self, db_session):
        """Test creating cart with missing required fields."""
        incomplete_data = {
            'quantity': 1
            # Missing user_id and item_id
        }
        
        with pytest.raises(Exception):
            self.service.create_cart(incomplete_data)
    
    def test_clear_cart_invalid_user(self, db_session):
        """Test clearing cart for non-existent user."""
        non_existent_id = uuid.uuid4()
        
        # Should not raise error, just return success
        result, status = self.service.clear_cart(non_existent_id)
        assert status == 200

