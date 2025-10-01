"""
Company Repository

This module provides the CompanyRepository class that implements data access
operations specific to the Company entity in the 3D Store application.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from app.repositories.base import BaseRepository
from app.company.model import Company
from app.utilities.error_utils import handle_errors
from app.utilities.db_utils import session_scope

class CompanyRepository(BaseRepository[Company]):
    """
    Repository class for Company entity operations.
    
    Extends BaseRepository with Company-specific data access methods.
    """
    
    def __init__(self):
        super().__init__(Company)
    
    @handle_errors("CompanyRepository")
    def get_company_by_name(self, name: str, session: Optional[Session] = None) -> Optional[Company]:
        """
        Retrieve a company by its name.
        
        Args:
            name: The company name to search for
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The company if found, None otherwise
        """
        if session:
            return session.query(Company).filter_by(name=name).first()
        
        with session_scope() as session:
            return session.query(Company).filter_by(name=name).first()
    
    @handle_errors("CompanyRepository")
    def get_company_by_code(self, code: str, session: Optional[Session] = None) -> Optional[Company]:
        """
        Retrieve a company by its code.
        
        Args:
            code: The company code to search for
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The company if found, None otherwise
        """
        if session:
            return session.query(Company).filter_by(code=code).first()
        
        with session_scope() as session:
            return session.query(Company).filter_by(code=code).first()
    
    @handle_errors("CompanyRepository")
    def get_active_companies(self, session: Optional[Session] = None) -> List[Company]:
        """
        Retrieve all active companies.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of active companies
        """
        if session:
            return session.query(Company).filter_by(is_active=True).all()
        
        with session_scope() as session:
            return session.query(Company).filter_by(is_active=True).all()
    
    @handle_errors("CompanyRepository")
    def search_companies(self, search_term: str, session: Optional[Session] = None) -> List[Company]:
        """
        Search companies by name or code.
        
        Args:
            search_term: The search term to look for
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of companies matching the search term
        """
        if session:
            search_pattern = f"%{search_term}%"
            return session.query(Company).filter(
                or_(
                    Company.name.ilike(search_pattern),
                    Company.code.ilike(search_pattern)
                )
            ).all()
        
        with session_scope() as session:
            return self.search_companies(search_term, session)
    
    @handle_errors("CompanyRepository")
    def get_company_statistics(self, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Get company statistics for dashboard/reporting.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing company statistics
        """
        if session:
            total_companies = session.query(Company).count()
            active_companies = session.query(Company).filter_by(is_active=True).count()
            inactive_companies = session.query(Company).filter_by(is_active=False).count()
            
            return {
                'total_companies': total_companies,
                'active_companies': active_companies,
                'inactive_companies': inactive_companies
            }
        
        with session_scope() as session:
            return self.get_company_statistics(session)
