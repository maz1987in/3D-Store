"""
Store Repository

This module provides the StoreRepository class that implements data access
operations specific to the Store entity in the 3D Store application.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from app.repositories.base import BaseRepository
from app.store.model import Store
from app.utilities.error_utils import handle_errors
from app.utilities.db_utils import session_scope

class StoreRepository(BaseRepository[Store]):
    """
    Repository class for Store entity operations.
    
    Extends BaseRepository with Store-specific data access methods.
    """
    
    def __init__(self):
        super().__init__(Store)
    
    @handle_errors("StoreRepository")
    def get_store_by_location(self, location: str, session: Optional[Session] = None) -> Optional[Store]:
        """
        Retrieve a store by its location.
        
        Args:
            location: The store location to search for
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The store if found, None otherwise
        """
        if session:
            return session.query(Store).filter_by(location=location).first()
        
        with session_scope() as session:
            return session.query(Store).filter_by(location=location).first()
    
    @handle_errors("StoreRepository")
    def get_store_by_manager(self, manager: str, session: Optional[Session] = None) -> Optional[Store]:
        """
        Retrieve a store by its manager.
        
        Args:
            manager: The store manager name to search for
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The store if found, None otherwise
        """
        if session:
            return session.query(Store).filter_by(manager=manager).first()
        
        with session_scope() as session:
            return session.query(Store).filter_by(manager=manager).first()
    
    @handle_errors("StoreRepository")
    def search_stores(self, search_term: str, session: Optional[Session] = None) -> List[Store]:
        """
        Search stores by location or manager.
        
        Args:
            search_term: The search term to look for
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of stores matching the search term
        """
        if session:
            search_pattern = f"%{search_term}%"
            return session.query(Store).filter(
                or_(
                    Store.location.ilike(search_pattern),
                    Store.manager.ilike(search_pattern)
                )
            ).all()
        
        with session_scope() as session:
            return self.search_stores(search_term, session)
    
    @handle_errors("StoreRepository")
    def get_store_statistics(self, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Get store statistics for dashboard/reporting.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing store statistics
        """
        if session:
            total_stores = session.query(Store).count()
            
            return {
                'total_stores': total_stores
            }
        
        with session_scope() as session:
            return self.get_store_statistics(session)
