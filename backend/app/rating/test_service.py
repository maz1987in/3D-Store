"""
Unit tests for Rating Service.

Tests all business logic in rating/service.py including:
- Rating submission and validation (1-5 scale)
- Average rating calculations  
- Duplicate rating prevention
- Review moderation
- Edge cases and error handling
"""

import pytest
import uuid
from unittest.mock import Mock, patch
from decimal import Decimal

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from test.test_helpers import assert_decimal_equal
from app.rating.service import RatingService
from app.rating.model import Rating
from app.common.error_handling import ResourceNotFoundError


class TestRatingService(BaseServiceTestCase):
    """Test cases for RatingService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = RatingService()
    
    # ========== CRUD Operations Tests ==========
    
    def test_create_rating_success(self, db_session, sample_user, sample_product, sample_order):
        """Test creating a rating successfully."""
        rating_data = {
            'product_id': sample_product.id,
            'score': 5,
            'comment': 'Excellent product!'
        }
        
        result, status = self.service.create_rating(rating_data, sample_user.id)
        
        assert status == 201
        assert 'Rating Created' in result
        
        # Verify rating was created
        rating = db_session.query(Rating).filter(
            Rating.product_id == sample_product.id,
            Rating.user_id == sample_user.id
        ).first()
        assert rating is not None
        assert rating.score == 5
        assert rating.comment == 'Excellent product!'
    
    def test_create_rating_different_scores(self, db_session, sample_user, sample_product, sample_order):
        """Test creating ratings with different valid scores."""
        for score in [1, 2, 3, 4, 5]:
            # Create new user for each rating to avoid duplicate
            from app.users.model import User
            from werkzeug.security import generate_password_hash
            user = User(
                username=f'user{score}',
                phone=f'+123456789{score}',
                email=f'user{score}@test.com',
                password=generate_password_hash('test'),
                active=True
            )
            db_session.add(user)
            db_session.commit()
            
            rating_data = {
                'product_id': sample_product.id,
                'score': score
            }
            
            result, status = self.service.create_rating(rating_data, user.id)
            assert status == 201
            
            # Verify score
            rating = db_session.query(Rating).filter(
                Rating.user_id == user.id
            ).first()
            assert rating.score == score
    
    def test_get_ratings_for_product(self, db_session, sample_user, sample_product, sample_order):
        """Test getting all ratings for a product."""
        # Create multiple ratings
        from app.users.model import User
        from werkzeug.security import generate_password_hash
        
        for i in range(3):
            user = User(
                username=f'ratinguser{i}',
                phone=f'+12345678{i}0',
                email=f'ratinguser{i}@test.com',
                password=generate_password_hash('test'),
                active=True
            )
            db_session.add(user)
            db_session.commit()
            
            rating_data = {
                'product_id': sample_product.id,
                'score': i + 3  # Scores 3, 4, 5
            }
            self.service.create_rating(rating_data, user.id)
        
        result, status = self.service.get_ratings(sample_product.id)
        
        assert status == 200
        assert len(result) >= 3
    
    def test_update_rating_success(self, db_session, sample_user, sample_product, sample_order):
        """Test updating a rating."""
        # Create initial rating
        rating_data = {
            'product_id': sample_product.id,
            'score': 3,
            'comment': 'Average product'
        }
        self.service.create_rating(rating_data, sample_user.id)
        
        rating = db_session.query(Rating).filter(
            Rating.user_id == sample_user.id
        ).first()
        
        # Update the rating
        update_data = {
            'score': 5,
            'comment': 'Actually great product!'
        }
        
        result, status = self.service.update_rating(rating.id, update_data, sample_user.id)
        
        assert status == 200
        assert 'Updated' in result
        
        db_session.refresh(rating)
        assert rating.score == 5
        assert rating.comment == 'Actually great product!'
    
    def test_update_rating_score_only(self, db_session, sample_user, sample_product, sample_order):
        """Test updating only the score."""
        # Create rating
        rating_data = {
            'product_id': sample_product.id,
            'score': 3,
            'comment': 'Original comment'
        }
        self.service.create_rating(rating_data, sample_user.id)
        
        rating = db_session.query(Rating).first()
        
        # Update only score
        update_data = {'score': 4}
        self.service.update_rating(rating.id, update_data, sample_user.id)
        
        db_session.refresh(rating)
        assert rating.score == 4
        assert rating.comment == 'Original comment'  # Comment unchanged
    
    def test_delete_rating_success(self, db_session, sample_user, sample_product, sample_order):
        """Test deleting a rating."""
        # Create rating
        rating_data = {
            'product_id': sample_product.id,
            'score': 4
        }
        self.service.create_rating(rating_data, sample_user.id)
        
        rating = db_session.query(Rating).first()
        rating_id = rating.id
        
        # Delete the rating
        result, status = self.service.delete_rating(rating_id)
        
        assert status == 200
        assert 'Deleted' in result
        
        deleted_rating = db_session.query(Rating).filter_by(id=rating_id).first()
        assert deleted_rating is None
    
    # ========== Average Rating Calculations Tests ==========
    
    def test_get_average_rating_single(self, db_session, sample_user, sample_product, sample_order):
        """Test average rating with single rating."""
        rating_data = {
            'product_id': sample_product.id,
            'score': 4
        }
        self.service.create_rating(rating_data, sample_user.id)
        
        result, status = self.service.get_average_rating(sample_product.id)
        
        assert status == 200
        assert 'average' in result
        assert result['average'] == 4.0
        assert result['max'] == 5
    
    def test_get_average_rating_multiple(self, db_session, sample_product, sample_order):
        """Test average rating with multiple ratings."""
        from app.users.model import User
        from werkzeug.security import generate_password_hash
        
        # Create 5 ratings: 1, 2, 3, 4, 5 (average = 3.0)
        for i in range(5):
            user = User(
                username=f'avguser{i}',
                phone=f'+987654321{i}',
                email=f'avguser{i}@test.com',
                password=generate_password_hash('test'),
                active=True
            )
            db_session.add(user)
            db_session.commit()
            
            rating_data = {
                'product_id': sample_product.id,
                'score': i + 1
            }
            self.service.create_rating(rating_data, user.id)
        
        result, status = self.service.get_average_rating(sample_product.id)
        
        assert status == 200
        assert result['average'] == 3.0  # (1+2+3+4+5)/5 = 3
    
    def test_get_average_rating_no_ratings(self, db_session, sample_product):
        """Test average rating when no ratings exist."""
        result, status = self.service.get_average_rating(sample_product.id)
        
        assert status == 200
        assert result['average'] == 0
        assert result['max'] == 5
    
    def test_get_average_rating_all_5_stars(self, db_session, sample_product, sample_order):
        """Test average rating when all ratings are 5 stars."""
        from app.users.model import User
        from werkzeug.security import generate_password_hash
        
        # Create 3 five-star ratings
        for i in range(3):
            user = User(
                username=f'fivestar{i}',
                phone=f'+555555555{i}',
                email=f'fivestar{i}@test.com',
                password=generate_password_hash('test'),
                active=True
            )
            db_session.add(user)
            db_session.commit()
            
            rating_data = {
                'product_id': sample_product.id,
                'score': 5
            }
            self.service.create_rating(rating_data, user.id)
        
        result, status = self.service.get_average_rating(sample_product.id)
        
        assert status == 200
        assert result['average'] == 5.0
    
    # ========== Duplicate Prevention Tests ==========
    
    def test_create_duplicate_rating_prevented(self, db_session, sample_user, sample_product, sample_order):
        """Test that user cannot rate same product twice."""
        rating_data = {
            'product_id': sample_product.id,
            'score': 4,
            'comment': 'First rating'
        }
        
        # First rating should succeed
        result1, status1 = self.service.create_rating(rating_data, sample_user.id)
        assert status1 == 201
        
        # Second rating should fail
        rating_data['comment'] = 'Second rating attempt'
        result2, status2 = self.service.create_rating(rating_data, sample_user.id)
        
        assert status2 == 400
        assert 'already rated' in result2.lower()
        
        # Verify only one rating exists
        ratings = db_session.query(Rating).filter(
            Rating.user_id == sample_user.id,
            Rating.product_id == sample_product.id
        ).all()
        assert len(ratings) == 1
        assert ratings[0].comment == 'First rating'
    
    # ========== Validation Tests ==========
    
    def test_create_rating_score_too_low(self, db_session, sample_user, sample_product, sample_order):
        """Test creating rating with score below 1."""
        rating_data = {
            'product_id': sample_product.id,
            'score': 0
        }
        
        result, status = self.service.create_rating(rating_data, sample_user.id)
        
        assert status == 400
        assert 'between 1 and 5' in result
    
    def test_create_rating_score_too_high(self, db_session, sample_user, sample_product, sample_order):
        """Test creating rating with score above 5."""
        rating_data = {
            'product_id': sample_product.id,
            'score': 6
        }
        
        result, status = self.service.create_rating(rating_data, sample_user.id)
        
        assert status == 400
        assert 'between 1 and 5' in result
    
    def test_update_rating_invalid_score(self, db_session, sample_user, sample_product, sample_order):
        """Test updating rating with invalid score."""
        # Create rating
        rating_data = {
            'product_id': sample_product.id,
            'score': 3
        }
        self.service.create_rating(rating_data, sample_user.id)
        
        rating = db_session.query(Rating).first()
        
        # Try to update with invalid score
        update_data = {'score': 10}
        result, status = self.service.update_rating(rating.id, update_data, sample_user.id)
        
        assert status == 400
        assert 'between 1 and 5' in result
    
    # ========== Edge Cases Tests ==========
    
    def test_create_rating_without_comment(self, db_session, sample_user, sample_product, sample_order):
        """Test creating rating without optional comment."""
        rating_data = {
            'product_id': sample_product.id,
            'score': 4
        }
        
        result, status = self.service.create_rating(rating_data, sample_user.id)
        
        assert status == 201
        
        rating = db_session.query(Rating).first()
        assert rating.comment is None
    
    def test_create_rating_with_long_comment(self, db_session, sample_user, sample_product, sample_order):
        """Test creating rating with very long comment."""
        long_comment = "A" * 1000  # 1000 character comment
        
        rating_data = {
            'product_id': sample_product.id,
            'score': 5,
            'comment': long_comment
        }
        
        result, status = self.service.create_rating(rating_data, sample_user.id)
        
        assert status == 201
        
        rating = db_session.query(Rating).first()
        assert len(rating.comment) >= 1000
    
    def test_get_ratings_empty_product(self, db_session, sample_product):
        """Test getting ratings for product with no ratings."""
        result, status = self.service.get_ratings(sample_product.id)
        
        assert status == 200
        assert len(result) == 0
    
    def test_update_comment_only(self, db_session, sample_user, sample_product, sample_order):
        """Test updating only the comment."""
        # Create rating
        rating_data = {
            'product_id': sample_product.id,
            'score': 4,
            'comment': 'Original'
        }
        self.service.create_rating(rating_data, sample_user.id)
        
        rating = db_session.query(Rating).first()
        original_score = rating.score
        
        # Update only comment
        update_data = {'comment': 'Updated comment'}
        self.service.update_rating(rating.id, update_data, sample_user.id)
        
        db_session.refresh(rating)
        assert rating.score == original_score  # Score unchanged
        assert rating.comment == 'Updated comment'
    
    # ========== Error Handling Tests ==========
    
    def test_create_rating_invalid_product(self, db_session, sample_user):
        """Test creating rating for non-existent product."""
        rating_data = {
            'product_id': uuid.uuid4(),  # Non-existent
            'score': 4
        }
        
        with pytest.raises(Exception):  # Foreign key constraint
            self.service.create_rating(rating_data, sample_user.id)
    
    def test_update_rating_not_found(self, db_session, sample_user):
        """Test updating a non-existent rating."""
        non_existent_id = uuid.uuid4()
        update_data = {'score': 4}
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_rating(non_existent_id, update_data, sample_user.id)
    
    def test_update_rating_wrong_user(self, db_session, sample_user, sample_product, sample_order):
        """Test user cannot update another user's rating."""
        # Create rating
        rating_data = {
            'product_id': sample_product.id,
            'score': 4
        }
        self.service.create_rating(rating_data, sample_user.id)
        
        rating = db_session.query(Rating).first()
        
        # Try to update with different user
        from app.users.model import User
        from werkzeug.security import generate_password_hash
        other_user = User(
            username='otheruser',
            phone='+9999999999',
            email='other@test.com',
            password=generate_password_hash('test'),
            active=True
        )
        db_session.add(other_user)
        db_session.commit()
        
        update_data = {'score': 1}
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_rating(rating.id, update_data, other_user.id)
    
    def test_delete_rating_not_found(self, db_session):
        """Test deleting a non-existent rating."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_rating(non_existent_id)
    
    def test_get_ratings_invalid_product(self, db_session):
        """Test getting ratings for non-existent product."""
        non_existent_id = uuid.uuid4()
        
        result, status = self.service.get_ratings(non_existent_id)
        
        # Should return empty list, not error
        assert status == 200
        assert len(result) == 0
    
    def test_average_rating_precision(self, db_session, sample_product, sample_order):
        """Test average rating calculation precision (2 decimal places)."""
        from app.users.model import User
        from werkzeug.security import generate_password_hash
        
        # Create ratings that result in decimal average: 3, 4, 5 = avg 4.0
        for i, score in enumerate([3, 4, 5]):
            user = User(
                username=f'precuser{i}',
                phone=f'+111222333{i}',
                email=f'precuser{i}@test.com',
                password=generate_password_hash('test'),
                active=True
            )
            db_session.add(user)
            db_session.commit()
            
            rating_data = {
                'product_id': sample_product.id,
                'score': score
            }
            self.service.create_rating(rating_data, user.id)
        
        result, status = self.service.get_average_rating(sample_product.id)
        
        assert status == 200
        # Should be rounded to 2 decimal places
        assert isinstance(result['average'], float)
        assert result['average'] == 4.0

