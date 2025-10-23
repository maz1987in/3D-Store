"""
Unit tests for Favorite Service.

Tests all business logic in favorite/service.py including:
- Favorite product management
- Duplicate prevention
- User favorites list
- Polymorphic model associations
- Edge cases and error handling
"""

import pytest
import uuid

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from app.favorite.service import FavoriteService
from app.favorite.model import Favorite
from app.common.error_handling import ResourceNotFoundError


class TestFavoriteService(BaseServiceTestCase):
    """Test cases for FavoriteService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = FavoriteService()
    
    # ========== CRUD Operations Tests ==========
    
    def test_create_favorite_success(self, db_session, sample_user, sample_product):
        """Test adding a product to favorites successfully."""
        favorite_data = {
            'user_id': sample_user.id,
            'model_type': 'product',
            'model_id': sample_product.id
        }
        
        result, status = self.service.create_favorite(favorite_data)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify favorite was created
        favorite = db_session.query(Favorite).filter(
            Favorite.user_id == sample_user.id,
            Favorite.model_id == sample_product.id
        ).first()
        assert favorite is not None
        assert favorite.model_type == 'product'
    
    def test_get_all_favorites(self, db_session, sample_user, sample_product):
        """Test getting all favorites."""
        # Create multiple favorites
        for i in range(3):
            favorite_data = {
                'user_id': sample_user.id,
                'model_type': 'product',
                'model_id': sample_product.id
            }
            self.service.create_favorite(favorite_data)
        
        result = self.service.get_all_favorites(None)
        
        assert len(result) >= 3
    
    def test_get_user_favorites(self, db_session, sample_user, sample_product):
        """Test getting favorites for a specific user."""
        # Create favorites
        favorite_data = {
            'user_id': sample_user.id,
            'model_type': 'product',
            'model_id': sample_product.id
        }
        self.service.create_favorite(favorite_data)
        
        result, status = self.service.get_user_favorites(
            model_type='product',
            model_id=None,
            user_id=sample_user.id
        )
        
        assert status == 200
        assert len(result) > 0
        assert all(fav['user_id'] == str(sample_user.id) for fav in result)
    
    def test_get_favorites_by_model_type(self, db_session, sample_user, sample_product):
        """Test filtering favorites by model type."""
        # Create product favorite
        favorite_data = {
            'user_id': sample_user.id,
            'model_type': 'product',
            'model_id': sample_product.id
        }
        self.service.create_favorite(favorite_data)
        
        result, status = self.service.get_user_favorites(
            model_type='product',
            model_id=None,
            user_id=sample_user.id
        )
        
        assert status == 200
        assert all(fav['model_type'] == 'product' for fav in result)
    
    def test_delete_favorite_success(self, db_session, sample_user, sample_product):
        """Test removing a product from favorites."""
        # Create favorite
        favorite_data = {
            'user_id': sample_user.id,
            'model_type': 'product',
            'model_id': sample_product.id
        }
        self.service.create_favorite(favorite_data)
        
        favorite = db_session.query(Favorite).first()
        favorite_id = favorite.id
        
        # Delete favorite
        result, status = self.service.delete_favorite(favorite_id)
        
        assert status == 200
        assert 'Deleted' in result
        
        deleted_favorite = db_session.query(Favorite).filter_by(id=favorite_id).first()
        assert deleted_favorite is None
    
    # ========== Duplicate Prevention Tests ==========
    
    def test_prevent_duplicate_favorite(self, db_session, sample_user, sample_product):
        """Test that user cannot favorite same product twice."""
        favorite_data = {
            'user_id': sample_user.id,
            'model_type': 'product',
            'model_id': sample_product.id
        }
        
        # First favorite should succeed
        result1, status1 = self.service.create_favorite(favorite_data)
        assert status1 == 201
        
        # Second favorite for same product should fail
        result2, status2 = self.service.create_favorite(favorite_data)
        
        # Should prevent duplicate or handle gracefully
        assert status2 in [400, 409]  # Bad request or conflict
        
        # Verify only one favorite exists
        favorites = db_session.query(Favorite).filter(
            Favorite.user_id == sample_user.id,
            Favorite.model_id == sample_product.id
        ).all()
        assert len(favorites) == 1
    
    def test_check_if_favorited(self, db_session, sample_user, sample_product):
        """Test checking if a product is favorited."""
        # Create favorite
        favorite_data = {
            'user_id': sample_user.id,
            'model_type': 'product',
            'model_id': sample_product.id
        }
        self.service.create_favorite(favorite_data)
        
        # Check if favorited
        result, status = self.service.check_favorite(
            user_id=sample_user.id,
            model_type='product',
            model_id=sample_product.id
        )
        
        assert status == 200
        assert result['is_favorite'] is True
    
    def test_check_if_not_favorited(self, db_session, sample_user, sample_product):
        """Test checking if a product is not favorited."""
        result, status = self.service.check_favorite(
            user_id=sample_user.id,
            model_type='product',
            model_id=sample_product.id
        )
        
        assert status == 200
        assert result['is_favorite'] is False
    
    # ========== Polymorphic Model Tests ==========
    
    def test_favorite_different_model_types(self, db_session, sample_user, sample_product):
        """Test favoriting different types of models."""
        model_types = ['product', 'category', 'store']
        
        for model_type in model_types:
            favorite_data = {
                'user_id': sample_user.id,
                'model_type': model_type,
                'model_id': sample_product.id  # Using product id as generic
            }
            result, status = self.service.create_favorite(favorite_data)
            assert status == 201
        
        # Verify all types were created
        result, _ = self.service.get_user_favorites(
            model_type=None,
            model_id=None,
            user_id=sample_user.id
        )
        
        model_types_created = set(fav['model_type'] for fav in result)
        assert len(model_types_created) >= len(model_types)
    
    def test_get_favorites_filtered_by_model(self, db_session, sample_user, sample_product):
        """Test getting favorites filtered by specific model ID."""
        # Create favorite
        favorite_data = {
            'user_id': sample_user.id,
            'model_type': 'product',
            'model_id': sample_product.id
        }
        self.service.create_favorite(favorite_data)
        
        result, status = self.service.get_user_favorites(
            model_type='product',
            model_id=sample_product.id,
            user_id=sample_user.id
        )
        
        assert status == 200
        assert len(result) > 0
        assert all(fav['model_id'] == str(sample_product.id) for fav in result)
    
    # ========== Multiple Users Tests ==========
    
    def test_different_users_can_favorite_same_product(self, db_session, sample_product):
        """Test that different users can favorite the same product."""
        from app.users.model import User
        from werkzeug.security import generate_password_hash
        
        # Create two users
        users = []
        for i in range(2):
            user = User(
                username=f'favuser{i}',
                phone=f'+333333333{i}',
                email=f'favuser{i}@test.com',
                password=generate_password_hash('test'),
                active=True
            )
            db_session.add(user)
            db_session.commit()
            users.append(user)
        
        # Both users favorite same product
        for user in users:
            favorite_data = {
                'user_id': user.id,
                'model_type': 'product',
                'model_id': sample_product.id
            }
            result, status = self.service.create_favorite(favorite_data)
            assert status == 201
        
        # Verify both favorites exist
        for user in users:
            favorites = db_session.query(Favorite).filter(
                Favorite.user_id == user.id,
                Favorite.model_id == sample_product.id
            ).all()
            assert len(favorites) == 1
    
    def test_user_favorite_multiple_products(self, db_session, sample_user):
        """Test user can favorite multiple products."""
        from app.product.model import Product
        
        # Create multiple products
        products = []
        for i in range(3):
            product = Product(
                code=f'FAV-PROD-{i}',
                base_price=100.00 * (i + 1),
                currency='USD'
            )
            db_session.add(product)
            db_session.commit()
            products.append(product)
        
        # Favorite all products
        for product in products:
            favorite_data = {
                'user_id': sample_user.id,
                'model_type': 'product',
                'model_id': product.id
            }
            result, status = self.service.create_favorite(favorite_data)
            assert status == 201
        
        # Verify all favorites
        result, _ = self.service.get_user_favorites(
            model_type='product',
            model_id=None,
            user_id=sample_user.id
        )
        
        assert len(result) >= 3
    
    # ========== Edge Cases Tests ==========
    
    def test_get_favorites_empty_user(self, db_session, sample_user):
        """Test getting favorites when user has none."""
        result, status = self.service.get_user_favorites(
            model_type=None,
            model_id=None,
            user_id=sample_user.id
        )
        
        assert status == 200
        assert len(result) == 0
    
    def test_create_favorite_invalid_user(self, db_session, sample_product):
        """Test creating favorite for non-existent user."""
        favorite_data = {
            'user_id': uuid.uuid4(),  # Non-existent
            'model_type': 'product',
            'model_id': sample_product.id
        }
        
        with pytest.raises(Exception):  # Foreign key constraint
            self.service.create_favorite(favorite_data)
    
    def test_delete_favorite_not_found(self, db_session):
        """Test deleting a non-existent favorite."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_favorite(non_existent_id)
    
    def test_get_favorite_by_invalid_id(self, db_session):
        """Test getting favorite with non-existent ID."""
        non_existent_id = uuid.uuid4()
        
        result = self.service.get_all_favorites(non_existent_id)
        
        assert len(result) == 0
    
    def test_favorite_with_null_model_id(self, db_session, sample_user):
        """Test creating favorite with null model_id."""
        favorite_data = {
            'user_id': sample_user.id,
            'model_type': 'product',
            'model_id': None
        }
        
        with pytest.raises(Exception):
            self.service.create_favorite(favorite_data)
    
    def test_get_favorites_with_filters(self, db_session, sample_user, sample_product):
        """Test getting favorites with various filter combinations."""
        # Create favorite
        favorite_data = {
            'user_id': sample_user.id,
            'model_type': 'product',
            'model_id': sample_product.id
        }
        self.service.create_favorite(favorite_data)
        
        # Test different filter combinations
        test_cases = [
            ('product', None, sample_user.id),
            ('product', sample_product.id, None),
            (None, sample_product.id, sample_user.id),
        ]
        
        for model_type, model_id, user_id in test_cases:
            result, status = self.service.get_user_favorites(
                model_type=model_type,
                model_id=model_id,
                user_id=user_id
            )
            assert status == 200
    
    # ========== Error Handling Tests ==========
    
    def test_create_favorite_missing_required_fields(self, db_session):
        """Test creating favorite with missing required fields."""
        incomplete_data = {
            'model_type': 'product'
            # Missing user_id and model_id
        }
        
        with pytest.raises(Exception):
            self.service.create_favorite(incomplete_data)
    
    def test_favorite_count_for_product(self, db_session, sample_product):
        """Test counting how many users favorited a product."""
        from app.users.model import User
        from werkzeug.security import generate_password_hash
        
        # Create 5 users who favorite the product
        for i in range(5):
            user = User(
                username=f'countuser{i}',
                phone=f'+444444444{i}',
                email=f'countuser{i}@test.com',
                password=generate_password_hash('test'),
                active=True
            )
            db_session.add(user)
            db_session.commit()
            
            favorite_data = {
                'user_id': user.id,
                'model_type': 'product',
                'model_id': sample_product.id
            }
            self.service.create_favorite(favorite_data)
        
        # Get count
        count = db_session.query(Favorite).filter(
            Favorite.model_type == 'product',
            Favorite.model_id == sample_product.id
        ).count()
        
        assert count == 5
    
    def test_unfavorite_and_refavorite(self, db_session, sample_user, sample_product):
        """Test removing and re-adding a favorite."""
        favorite_data = {
            'user_id': sample_user.id,
            'model_type': 'product',
            'model_id': sample_product.id
        }
        
        # Add to favorites
        self.service.create_favorite(favorite_data)
        favorite = db_session.query(Favorite).first()
        
        # Remove from favorites
        self.service.delete_favorite(favorite.id)
        
        # Verify removed
        favorites = db_session.query(Favorite).filter(
            Favorite.user_id == sample_user.id,
            Favorite.model_id == sample_product.id
        ).all()
        assert len(favorites) == 0
        
        # Re-add to favorites
        result, status = self.service.create_favorite(favorite_data)
        assert status == 201
        
        # Verify re-added
        favorites = db_session.query(Favorite).filter(
            Favorite.user_id == sample_user.id,
            Favorite.model_id == sample_product.id
        ).all()
        assert len(favorites) == 1

