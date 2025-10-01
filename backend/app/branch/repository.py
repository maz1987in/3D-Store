"""
Branch Repository

This module provides the BranchRepository class that implements data access
operations specific to the Branch entity in the 3D Store application.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from app.repositories.base import BaseRepository
from app.branch.model import Branch
from app.utilities.error_utils import handle_errors
from app.utilities.db_utils import session_scope

class BranchRepository(BaseRepository[Branch]):
    """
    Repository class for Branch entity operations.
    
    Extends BaseRepository with Branch-specific data access methods.
    """
    
    def __init__(self):
        super().__init__(Branch)
    
    @handle_errors("BranchRepository")
    def get_branch_by_location(self, location: str, session: Optional[Session] = None) -> Optional[Branch]:
        """
        Retrieve a branch by its location.
        
        Args:
            location: The branch location to search for
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The branch if found, None otherwise
        """
        if session:
            return session.query(Branch).filter_by(location=location).first()
        
        with session_scope() as session:
            return session.query(Branch).filter_by(location=location).first()
    
    @handle_errors("BranchRepository")
    def get_branch_by_manager(self, manager: str, session: Optional[Session] = None) -> Optional[Branch]:
        """
        Retrieve a branch by its manager.
        
        Args:
            manager: The branch manager name to search for
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The branch if found, None otherwise
        """
        if session:
            return session.query(Branch).filter_by(manager=manager).first()
        
        with session_scope() as session:
            return session.query(Branch).filter_by(manager=manager).first()
    
    @handle_errors("BranchRepository")
    def search_branches(self, search_term: str, session: Optional[Session] = None) -> List[Branch]:
        """
        Search branches by location or manager.
        
        Args:
            search_term: The search term to look for
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of branches matching the search term
        """
        if session:
            search_pattern = f"%{search_term}%"
            return session.query(Branch).filter(
                or_(
                    Branch.location.ilike(search_pattern),
                    Branch.manager.ilike(search_pattern)
                )
            ).all()
        
        with session_scope() as session:
            return self.search_branches(search_term, session)
    
    @handle_errors("BranchRepository")
    def get_branch_statistics(self, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Get branch statistics for dashboard/reporting.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing branch statistics
        """
        if session:
            total_branches = session.query(Branch).count()
            
            return {
                'total_branches': total_branches
            }
        
        with session_scope() as session:
            return self.get_branch_statistics(session)
