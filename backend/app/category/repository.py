"""
Category Repository

This module provides the CategoryRepository class that implements data access
operations specific to the Category entity in the 3D Store application.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from app.repositories.base import BaseRepository
from app.category.model import Category
from app.utilities.error_utils import handle_errors
from app.utilities.db_utils import session_scope
from app.common.queries import create_sorters, filter_and_sort_query
from app.common import filters_serialization
from sqlalchemy_filters import apply_pagination

class CategoryRepository(BaseRepository[Category]):
    """
    Repository class for Category entity operations.
    
    Extends BaseRepository with Category-specific data access methods.
    """
    
    def __init__(self):
        super().__init__(Category)
    
    @handle_errors("CategoryRepository")
    def get_categories_with_children(self, session: Optional[Session] = None) -> List[Category]:
        """
        Retrieve all categories with their subcategories.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of categories with subcategories
        """
        if session:
            return session.query(Category).options(
                joinedload(Category.sub_categories)
            ).filter_by(parent_id=None).all()
        
        with session_scope() as session:
            return session.query(Category).options(
                joinedload(Category.sub_categories)
            ).filter_by(parent_id=None).all()
    
    @handle_errors("CategoryRepository")
    def get_category_with_details(self, category_id: str, session: Optional[Session] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve a category with all its related details.
        
        Args:
            category_id: The unique identifier of the category
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing category with all related details
        """
        if session:
            category = session.query(Category).options(
                joinedload(Category.sub_categories),
                joinedload(Category.products),
                joinedload(Category.default_material),
                joinedload(Category.default_settings)
            ).filter_by(id=category_id).first()
            
            if not category:
                return None
            
            return {
                'category': category,
                'sub_categories': category.sub_categories,
                'products': category.products,
                'default_material': category.default_material,
                'default_settings': category.default_settings
            }
        
        with session_scope() as session:
            return self.get_category_with_details(category_id, session)
    
    @handle_errors("CategoryRepository")
    def get_root_categories(self, session: Optional[Session] = None) -> List[Category]:
        """
        Retrieve all root categories (categories without parent).
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of root categories
        """
        if session:
            return session.query(Category).filter_by(parent_id=None).all()
        
        with session_scope() as session:
            return session.query(Category).filter_by(parent_id=None).all()
    
    @handle_errors("CategoryRepository")
    def get_subcategories(self, parent_id: str, session: Optional[Session] = None) -> List[Category]:
        """
        Retrieve all subcategories of a specific parent category.
        
        Args:
            parent_id: The unique identifier of the parent category
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of subcategories
        """
        if session:
            return session.query(Category).filter_by(parent_id=parent_id).all()
        
        with session_scope() as session:
            return session.query(Category).filter_by(parent_id=parent_id).all()
    
    @handle_errors("CategoryRepository")
    def get_categories_by_type(self, category_type: str, session: Optional[Session] = None) -> List[Category]:
        """
        Retrieve all categories of a specific type.
        
        Args:
            category_type: The type of category (product, service, material, ready_made)
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of categories of the specified type
        """
        if session:
            return session.query(Category).filter_by(category_type=category_type).all()
        
        with session_scope() as session:
            return session.query(Category).filter_by(category_type=category_type).all()
    
    @handle_errors("CategoryRepository")
    def get_active_categories(self, session: Optional[Session] = None) -> List[Category]:
        """
        Retrieve all active categories.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of active categories
        """
        if session:
            return session.query(Category).filter_by(is_active=True).all()
        
        with session_scope() as session:
            return session.query(Category).filter_by(is_active=True).all()
    
    @handle_errors("CategoryRepository")
    def get_featured_categories(self, session: Optional[Session] = None) -> List[Category]:
        """
        Retrieve all featured categories.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of featured categories
        """
        if session:
            return session.query(Category).filter_by(is_featured=True, is_active=True).all()
        
        with session_scope() as session:
            return session.query(Category).filter_by(is_featured=True, is_active=True).all()
    
    @handle_errors("CategoryRepository")
    def get_category_by_slug(self, slug: str, session: Optional[Session] = None) -> Optional[Category]:
        """
        Retrieve a category by its slug.
        
        Args:
            slug: The URL-friendly slug of the category
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The category if found, None otherwise
        """
        if session:
            return session.query(Category).filter_by(slug=slug).first()
        
        with session_scope() as session:
            return session.query(Category).filter_by(slug=slug).first()
    
    @handle_errors("CategoryRepository")
    def get_category_by_code(self, code: str, session: Optional[Session] = None) -> Optional[Category]:
        """
        Retrieve a category by its code.
        
        Args:
            code: The category code
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The category if found, None otherwise
        """
        if session:
            return session.query(Category).filter_by(code=code).first()
        
        with session_scope() as session:
            return session.query(Category).filter_by(code=code).first()
    
    @handle_errors("CategoryRepository")
    def get_categories_with_products(self, session: Optional[Session] = None) -> List[Category]:
        """
        Retrieve categories that have products.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of categories with products
        """
        if session:
            return session.query(Category).join(Category.products).distinct().all()
        
        with session_scope() as session:
            return session.query(Category).join(Category.products).distinct().all()
    
    @handle_errors("CategoryRepository")
    def get_category_hierarchy(self, session: Optional[Session] = None) -> List[Dict[str, Any]]:
        """
        Retrieve the complete category hierarchy.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of category hierarchy with nested structure
        """
        if session:
            root_categories = session.query(Category).filter_by(parent_id=None).all()
            hierarchy = []
            
            for category in root_categories:
                category_data = {
                    'category': category,
                    'subcategories': self._build_subcategory_hierarchy(category.id, session)
                }
                hierarchy.append(category_data)
            
            return hierarchy
        
        with session_scope() as session:
            return self.get_category_hierarchy(session)
    
    def _build_subcategory_hierarchy(self, parent_id: str, session: Session) -> List[Dict[str, Any]]:
        """
        Recursively build subcategory hierarchy.
        
        Args:
            parent_id: The parent category ID
            session: Database session
            
        Returns:
            List of subcategories with nested structure
        """
        subcategories = session.query(Category).filter_by(parent_id=parent_id).all()
        hierarchy = []
        
        for subcategory in subcategories:
            subcategory_data = {
                'category': subcategory,
                'subcategories': self._build_subcategory_hierarchy(subcategory.id, session)
            }
            hierarchy.append(subcategory_data)
        
        return hierarchy
    
    @handle_errors("CategoryRepository")
    def get_categories_by_commission_rate(self, min_rate: float, max_rate: float, session: Optional[Session] = None) -> List[Category]:
        """
        Retrieve categories within a specific commission rate range.
        
        Args:
            min_rate: Minimum commission rate
            max_rate: Maximum commission rate
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of categories within the commission rate range
        """
        if session:
            return session.query(Category).filter(
                and_(
                    Category.base_commission_rate >= min_rate,
                    Category.base_commission_rate <= max_rate
                )
            ).all()
        
        with session_scope() as session:
            return session.query(Category).filter(
                and_(
                    Category.base_commission_rate >= min_rate,
                    Category.base_commission_rate <= max_rate
                )
            ).all()
    
    @handle_errors("CategoryRepository")
    def update_category_sort_order(self, category_id: str, sort_order: int, session: Optional[Session] = None) -> bool:
        """
        Update the sort order of a category.
        
        Args:
            category_id: The unique identifier of the category
            sort_order: The new sort order
            session: Optional database session (if None, creates a new one)
            
        Returns:
            True if updated successfully
        """
        if session:
            category = session.query(Category).filter_by(id=category_id).first()
            if category:
                category.sort_order = sort_order
                session.flush()
                return True
            return False
        
        with session_scope() as session:
            return self.update_category_sort_order(category_id, sort_order, session)
    
    @handle_errors("CategoryRepository")
    def get_category_statistics(self, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Get category statistics for dashboard/reporting.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing category statistics
        """
        if session:
            total_categories = session.query(Category).count()
            active_categories = session.query(Category).filter_by(is_active=True).count()
            featured_categories = session.query(Category).filter_by(is_featured=True).count()
            root_categories = session.query(Category).filter_by(parent_id=None).count()
            
            # Count categories by type
            category_types = {}
            for category_type in ['product', 'service', 'material', 'ready_made']:
                count = session.query(Category).filter_by(category_type=category_type).count()
                category_types[category_type] = count
            
            return {
                'total_categories': total_categories,
                'active_categories': active_categories,
                'featured_categories': featured_categories,
                'root_categories': root_categories,
                'category_types': category_types
            }
        
        with session_scope() as session:
            return self.get_category_statistics(session)
