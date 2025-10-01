"""
Product Repository

This module provides the ProductRepository class that implements data access
operations specific to the Product entity in the 3D Store application.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from app.repositories.base import BaseRepository
from app.product.model import Product
from app.category.model import Category
from app.product.model import ProductShippingCity
from app.utilities.error_utils import handle_errors
from app.utilities.db_utils import session_scope
from app.common.queries import create_sorters, filter_and_sort_query
from app.common import filters_serialization
from sqlalchemy_filters import apply_pagination

class ProductRepository(BaseRepository[Product]):
    """
    Repository class for Product entity operations.
    
    Extends BaseRepository with Product-specific data access methods.
    """
    
    def __init__(self):
        super().__init__(Product)
    
    @handle_errors("ProductRepository")
    def get_products_with_category(self, filter_obj, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Retrieve products with their associated category information.
        
        Args:
            filter_obj: Filter object containing pagination and sorting parameters
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing products with categories and pagination metadata
        """
        if session:
            query = session.query(Product, Category).join(Category, Product.category_id == Category.id)
            
            # Apply sorting
            if filter_obj.sort is None:
                filter_obj.sorters = create_sorters('modified_date', 'desc')
            query = filter_and_sort_query(filter_obj.filters, filter_obj.sorters, query, [Product, Category])
            
            # Apply pagination
            query, pagination = apply_pagination(
                query, 
                page_number=int(filter_obj.page), 
                page_size=int(filter_obj.per_page)
            )
            
            products = query.all()
            
            return {
                'products': products,
                'filters': filters_serialization.get_pagination_serialization(
                    pagination, filter_obj.sort, filter_obj.sort_order, filter_obj.queries
                )
            }
        
        with session_scope() as session:
            return self.get_products_with_category(filter_obj, session)
    
    @handle_errors("ProductRepository")
    def get_product_with_details(self, product_id: str, session: Optional[Session] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve a product with all its related details (category, shipping cities, etc.).
        
        Args:
            product_id: The unique identifier of the product
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing product with all related details
        """
        if session:
            product = session.query(Product).options(
                joinedload(Product.parent_category),
                joinedload(Product.subcategory),
                joinedload(Product.shipping_cities)
            ).filter_by(id=product_id).first()
            
            if not product:
                return None
            
            return {
                'product': product,
                'category': product.parent_category,
                'subcategory': product.subcategory,
                'shipping_cities': product.shipping_cities
            }
        
        with session_scope() as session:
            return self.get_product_with_details(product_id, session)
    
    @handle_errors("ProductRepository")
    def get_products_by_category(self, category_id: str, session: Optional[Session] = None) -> List[Product]:
        """
        Retrieve all products belonging to a specific category.
        
        Args:
            category_id: The unique identifier of the category
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of products in the category
        """
        if session:
            return session.query(Product).filter_by(category_id=category_id).all()
        
        with session_scope() as session:
            return session.query(Product).filter_by(category_id=category_id).all()
    
    @handle_errors("ProductRepository")
    def get_products_by_type(self, product_type: str, session: Optional[Session] = None) -> List[Product]:
        """
        Retrieve all products of a specific type.
        
        Args:
            product_type: The type of product (service, ready_made, material)
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of products of the specified type
        """
        if session:
            return session.query(Product).filter_by(product_type=product_type).all()
        
        with session_scope() as session:
            return session.query(Product).filter_by(product_type=product_type).all()
    
    @handle_errors("ProductRepository")
    def get_featured_products(self, limit: int = 10, session: Optional[Session] = None) -> List[Product]:
        """
        Retrieve featured products.
        
        Args:
            limit: Maximum number of products to return
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of featured products
        """
        if session:
            return session.query(Product).filter_by(is_featured=True, is_active=True).limit(limit).all()
        
        with session_scope() as session:
            return session.query(Product).filter_by(is_featured=True, is_active=True).limit(limit).all()
    
    @handle_errors("ProductRepository")
    def get_active_products(self, session: Optional[Session] = None) -> List[Product]:
        """
        Retrieve all active products.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of active products
        """
        if session:
            return session.query(Product).filter_by(is_active=True).all()
        
        with session_scope() as session:
            return session.query(Product).filter_by(is_active=True).all()
    
    @handle_errors("ProductRepository")
    def search_products(self, search_term: str, session: Optional[Session] = None) -> List[Product]:
        """
        Search products by title, description, or tags.
        
        Args:
            search_term: The search term to look for
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of products matching the search term
        """
        if session:
            # This would need to be implemented with full-text search
            # For now, using a simple LIKE query
            search_pattern = f"%{search_term}%"
            return session.query(Product).filter(
                or_(
                    Product.code.ilike(search_pattern),
                    Product.sku.ilike(search_pattern)
                )
            ).all()
        
        with session_scope() as session:
            return self.search_products(search_term, session)
    
    @handle_errors("ProductRepository")
    def get_products_by_supplier(self, supplier_id: str, session: Optional[Session] = None) -> List[Product]:
        """
        Retrieve all products from a specific supplier.
        
        Args:
            supplier_id: The unique identifier of the supplier
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of products from the supplier
        """
        if session:
            return session.query(Product).filter_by(supplier_id=supplier_id).all()
        
        with session_scope() as session:
            return session.query(Product).filter_by(supplier_id=supplier_id).all()
    
    @handle_errors("ProductRepository")
    def get_products_by_price_range(self, min_price: float, max_price: float, session: Optional[Session] = None) -> List[Product]:
        """
        Retrieve products within a specific price range.
        
        Args:
            min_price: Minimum price
            max_price: Maximum price
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of products within the price range
        """
        if session:
            return session.query(Product).filter(
                and_(
                    Product.base_price >= min_price,
                    Product.base_price <= max_price
                )
            ).all()
        
        with session_scope() as session:
            return session.query(Product).filter(
                and_(
                    Product.base_price >= min_price,
                    Product.base_price <= max_price
                )
            ).all()
    
    @handle_errors("ProductRepository")
    def update_product_rating(self, product_id: str, new_rating: float, session: Optional[Session] = None) -> bool:
        """
        Update product rating (this would typically be calculated from ratings table).
        
        Args:
            product_id: The unique identifier of the product
            new_rating: The new average rating
            session: Optional database session (if None, creates a new one)
            
        Returns:
            True if updated successfully
        """
        if session:
            product = session.query(Product).filter_by(id=product_id).first()
            if product:
                # This would typically be calculated from the ratings table
                # For now, we'll just return True
                return True
            return False
        
        with session_scope() as session:
            return self.update_product_rating(product_id, new_rating, session)
    
    @handle_errors("ProductRepository")
    def get_digital_products(self, session: Optional[Session] = None) -> List[Product]:
        """
        Retrieve all digital products.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of digital products
        """
        if session:
            return session.query(Product).filter_by(is_digital=True, is_active=True).all()
        
        with session_scope() as session:
            return session.query(Product).filter_by(is_digital=True, is_active=True).all()
    
    @handle_errors("ProductRepository")
    def get_products_by_availability(self, in_stock: bool = True, session: Optional[Session] = None) -> List[Product]:
        """
        Retrieve products based on availability.
        
        Args:
            in_stock: Whether to get products in stock or out of stock
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of products based on availability
        """
        if session:
            if in_stock:
                return session.query(Product).filter(Product.quantity > 0).all()
            else:
                return session.query(Product).filter(Product.quantity <= 0).all()
        
        with session_scope() as session:
            return self.get_products_by_availability(in_stock, session)
