"""
Rating Repository

This module provides the RatingRepository class that implements data access
operations specific to the Rating entity in the 3D Store application.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func
from app.repositories.base import BaseRepository
from app.rating.model import Rating
from app.product.model import Product
from app.users.model import User
from app.utilities.error_utils import handle_errors
from app.utilities.db_utils import session_scope

class RatingRepository(BaseRepository[Rating]):
    """
    Repository class for Rating entity operations.
    
    Extends BaseRepository with Rating-specific data access methods.
    """
    
    def __init__(self):
        super().__init__(Rating)
    
    @handle_errors("RatingRepository")
    def get_ratings_with_details(self, rating_id: str, session: Optional[Session] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve a rating with all its related details.
        
        Args:
            rating_id: The unique identifier of the rating
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing rating with all related details
        """
        if session:
            rating = session.query(Rating).options(
                joinedload(Rating.product),
                joinedload(Rating.user)
            ).filter_by(id=rating_id).first()
            
            if not rating:
                return None
            
            return {
                'rating': rating,
                'product': rating.product,
                'user': rating.user
            }
        
        with session_scope() as session:
            return self.get_ratings_with_details(rating_id, session)
    
    @handle_errors("RatingRepository")
    def get_ratings_by_product(self, product_id: str, session: Optional[Session] = None) -> List[Rating]:
        """
        Retrieve all ratings for a specific product.
        
        Args:
            product_id: The unique identifier of the product
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of ratings for the product
        """
        if session:
            return session.query(Rating).filter_by(product_id=product_id).order_by(desc(Rating.create_date)).all()
        
        with session_scope() as session:
            return session.query(Rating).filter_by(product_id=product_id).order_by(desc(Rating.create_date)).all()
    
    @handle_errors("RatingRepository")
    def get_ratings_by_user(self, user_id: str, session: Optional[Session] = None) -> List[Rating]:
        """
        Retrieve all ratings by a specific user.
        
        Args:
            user_id: The unique identifier of the user
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of ratings by the user
        """
        if session:
            return session.query(Rating).filter_by(user_id=user_id).order_by(desc(Rating.create_date)).all()
        
        with session_scope() as session:
            return session.query(Rating).filter_by(user_id=user_id).order_by(desc(Rating.create_date)).all()
    
    @handle_errors("RatingRepository")
    def get_ratings_by_score(self, score: float, session: Optional[Session] = None) -> List[Rating]:
        """
        Retrieve all ratings with a specific score.
        
        Args:
            score: The rating score to filter by
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of ratings with the specified score
        """
        if session:
            return session.query(Rating).filter_by(score=score).order_by(desc(Rating.create_date)).all()
        
        with session_scope() as session:
            return session.query(Rating).filter_by(score=score).order_by(desc(Rating.create_date)).all()
    
    @handle_errors("RatingRepository")
    def get_ratings_by_score_range(self, min_score: float, max_score: float, session: Optional[Session] = None) -> List[Rating]:
        """
        Retrieve ratings within a specific score range.
        
        Args:
            min_score: Minimum score
            max_score: Maximum score
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of ratings within the score range
        """
        if session:
            return session.query(Rating).filter(
                and_(
                    Rating.score >= min_score,
                    Rating.score <= max_score
                )
            ).order_by(desc(Rating.create_date)).all()
        
        with session_scope() as session:
            return session.query(Rating).filter(
                and_(
                    Rating.score >= min_score,
                    Rating.score <= max_score
                )
            ).order_by(desc(Rating.create_date)).all()
    
    @handle_errors("RatingRepository")
    def get_high_ratings(self, min_score: float = 4.0, session: Optional[Session] = None) -> List[Rating]:
        """
        Retrieve high ratings (above minimum score).
        
        Args:
            min_score: Minimum score for high ratings
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of high ratings
        """
        if session:
            return session.query(Rating).filter(Rating.score >= min_score).order_by(desc(Rating.create_date)).all()
        
        with session_scope() as session:
            return session.query(Rating).filter(Rating.score >= min_score).order_by(desc(Rating.create_date)).all()
    
    @handle_errors("RatingRepository")
    def get_low_ratings(self, max_score: float = 2.0, session: Optional[Session] = None) -> List[Rating]:
        """
        Retrieve low ratings (below maximum score).
        
        Args:
            max_score: Maximum score for low ratings
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of low ratings
        """
        if session:
            return session.query(Rating).filter(Rating.score <= max_score).order_by(desc(Rating.create_date)).all()
        
        with session_scope() as session:
            return session.query(Rating).filter(Rating.score <= max_score).order_by(desc(Rating.create_date)).all()
    
    @handle_errors("RatingRepository")
    def get_average_rating_by_product(self, product_id: str, session: Optional[Session] = None) -> Optional[float]:
        """
        Get the average rating for a specific product.
        
        Args:
            product_id: The unique identifier of the product
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Average rating for the product, None if no ratings exist
        """
        if session:
            result = session.query(func.avg(Rating.score)).filter_by(product_id=product_id).scalar()
            return round(float(result), 2) if result else None
        
        with session_scope() as session:
            return self.get_average_rating_by_product(product_id, session)
    
    @handle_errors("RatingRepository")
    def get_rating_count_by_product(self, product_id: str, session: Optional[Session] = None) -> int:
        """
        Get the total number of ratings for a specific product.
        
        Args:
            product_id: The unique identifier of the product
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Total number of ratings for the product
        """
        if session:
            return session.query(Rating).filter_by(product_id=product_id).count()
        
        with session_scope() as session:
            return session.query(Rating).filter_by(product_id=product_id).count()
    
    @handle_errors("RatingRepository")
    def get_rating_distribution_by_product(self, product_id: str, session: Optional[Session] = None) -> Dict[str, int]:
        """
        Get rating distribution for a specific product.
        
        Args:
            product_id: The unique identifier of the product
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing rating distribution
        """
        if session:
            distribution = {}
            for score in range(1, 6):
                count = session.query(Rating).filter(
                    and_(
                        Rating.product_id == product_id,
                        Rating.score == score
                    )
                ).count()
                distribution[str(score)] = count
            
            return distribution
        
        with session_scope() as session:
            return self.get_rating_distribution_by_product(product_id, session)
    
    @handle_errors("RatingRepository")
    def get_recent_ratings(self, limit: int = 10, session: Optional[Session] = None) -> List[Rating]:
        """
        Retrieve the most recent ratings.
        
        Args:
            limit: Maximum number of ratings to return
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of recent ratings
        """
        if session:
            return session.query(Rating).order_by(desc(Rating.create_date)).limit(limit).all()
        
        with session_scope() as session:
            return session.query(Rating).order_by(desc(Rating.create_date)).limit(limit).all()
    
    @handle_errors("RatingRepository")
    def get_rating_statistics(self, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Get rating statistics for dashboard/reporting.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing rating statistics
        """
        if session:
            total_ratings = session.query(Rating).count()
            average_rating = session.query(func.avg(Rating.score)).scalar()
            average_rating = round(float(average_rating), 2) if average_rating else 0.0
            
            # Count ratings by score
            score_counts = {}
            for score in range(1, 6):
                count = session.query(Rating).filter_by(score=score).count()
                score_counts[str(score)] = count
            
            # Count ratings with comments
            ratings_with_comments = session.query(Rating).filter(Rating.comment.isnot(None)).count()
            
            return {
                'total_ratings': total_ratings,
                'average_rating': average_rating,
                'score_counts': score_counts,
                'ratings_with_comments': ratings_with_comments
            }
        
        with session_scope() as session:
            return self.get_rating_statistics(session)
    
    @handle_errors("RatingRepository")
    def get_top_rated_products(self, limit: int = 10, min_ratings: int = 5, session: Optional[Session] = None) -> List[Dict[str, Any]]:
        """
        Get top rated products based on average rating and minimum number of ratings.
        
        Args:
            limit: Maximum number of products to return
            min_ratings: Minimum number of ratings required
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of top rated products with their ratings
        """
        if session:
            # Get products with their average ratings and rating counts
            result = session.query(
                Product,
                func.avg(Rating.score).label('average_rating'),
                func.count(Rating.id).label('rating_count')
            ).join(Rating, Product.id == Rating.product_id).group_by(Product.id).having(
                func.count(Rating.id) >= min_ratings
            ).order_by(desc('average_rating')).limit(limit).all()
            
            top_products = []
            for product, avg_rating, rating_count in result:
                top_products.append({
                    'product': product,
                    'average_rating': round(float(avg_rating), 2),
                    'rating_count': rating_count
                })
            
            return top_products
        
        with session_scope() as session:
            return self.get_top_rated_products(limit, min_ratings, session)
    
    @handle_errors("RatingRepository")
    def get_user_rating_for_product(self, user_id: str, product_id: str, session: Optional[Session] = None) -> Optional[Rating]:
        """
        Get a user's rating for a specific product.
        
        Args:
            user_id: The unique identifier of the user
            product_id: The unique identifier of the product
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The user's rating for the product if exists, None otherwise
        """
        if session:
            return session.query(Rating).filter_by(user_id=user_id, product_id=product_id).first()
        
        with session_scope() as session:
            return session.query(Rating).filter_by(user_id=user_id, product_id=product_id).first()
    
    @handle_errors("RatingRepository")
    def update_rating(self, rating_id: str, new_score: float, new_comment: str = None, session: Optional[Session] = None) -> bool:
        """
        Update a rating's score and comment.
        
        Args:
            rating_id: The unique identifier of the rating
            new_score: The new rating score
            new_comment: The new comment (optional)
            session: Optional database session (if None, creates a new one)
            
        Returns:
            True if updated successfully
        """
        if session:
            rating = session.query(Rating).filter_by(id=rating_id).first()
            if rating:
                rating.score = new_score
                if new_comment is not None:
                    rating.comment = new_comment
                session.flush()
                return True
            return False
        
        with session_scope() as session:
            return self.update_rating(rating_id, new_score, new_comment, session)
