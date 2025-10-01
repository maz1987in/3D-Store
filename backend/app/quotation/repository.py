"""
Quotation Repository

This module provides the QuotationRepository class that implements data access
operations specific to the Quotation entity in the 3D Store application.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from app.repositories.base import BaseRepository
from app.quotation.model import Quotation
from app.customers.model import Customer
from app.branch.model import Branch
from app.users.model import User
from app.utilities.error_utils import handle_errors
from app.utilities.db_utils import session_scope
from app.common.enum import QuoteStatusEnum
from app.common.queries import create_sorters, filter_and_sort_query
from app.common import filters_serialization
from sqlalchemy_filters import apply_pagination
from datetime import datetime, timezone

class QuotationRepository(BaseRepository[Quotation]):
    """
    Repository class for Quotation entity operations.
    
    Extends BaseRepository with Quotation-specific data access methods.
    """
    
    def __init__(self):
        super().__init__(Quotation)
    
    @handle_errors("QuotationRepository")
    def get_quotations_with_details(self, filter_obj, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Retrieve quotations with their associated details.
        
        Args:
            filter_obj: Filter object containing pagination and sorting parameters
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing quotations with details and pagination metadata
        """
        if session:
            query = session.query(Quotation, Customer, Branch, User).outerjoin(
                Customer, Quotation.customer_id == Customer.id
            ).outerjoin(
                Branch, Quotation.branch_id == Branch.id
            ).outerjoin(
                User, Quotation.user_id == User.id
            )
            
            # Apply sorting
            if filter_obj.sort is None:
                filter_obj.sorters = create_sorters('date', 'desc')
            query = filter_and_sort_query(filter_obj.filters, filter_obj.sorters, query, [Quotation, Customer, Branch, User])
            
            # Apply pagination
            query, pagination = apply_pagination(
                query, 
                page_number=int(filter_obj.page), 
                page_size=int(filter_obj.per_page)
            )
            
            quotations = query.all()
            
            return {
                'quotations': quotations,
                'filters': filters_serialization.get_pagination_serialization(
                    pagination, filter_obj.sort, filter_obj.sort_order, filter_obj.queries
                )
            }
        
        with session_scope() as session:
            return self.get_quotations_with_details(filter_obj, session)
    
    @handle_errors("QuotationRepository")
    def get_quotation_by_number(self, number: str, session: Optional[Session] = None) -> Optional[Quotation]:
        """
        Retrieve a quotation by its number.
        
        Args:
            number: The quotation number to search for
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The quotation if found, None otherwise
        """
        if session:
            return session.query(Quotation).filter_by(number=number).first()
        
        with session_scope() as session:
            return session.query(Quotation).filter_by(number=number).first()
    
    @handle_errors("QuotationRepository")
    def get_quotations_by_customer(self, customer_id: str, session: Optional[Session] = None) -> List[Quotation]:
        """
        Retrieve all quotations for a specific customer.
        
        Args:
            customer_id: The unique identifier of the customer
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of quotations for the customer
        """
        if session:
            return session.query(Quotation).filter_by(customer_id=customer_id).order_by(desc(Quotation.date)).all()
        
        with session_scope() as session:
            return session.query(Quotation).filter_by(customer_id=customer_id).order_by(desc(Quotation.date)).all()
    
    @handle_errors("QuotationRepository")
    def get_quotations_by_status(self, status: QuoteStatusEnum, session: Optional[Session] = None) -> List[Quotation]:
        """
        Retrieve all quotations with a specific status.
        
        Args:
            status: The quotation status to filter by
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of quotations with the specified status
        """
        if session:
            return session.query(Quotation).filter_by(qoute_status=status).order_by(desc(Quotation.date)).all()
        
        with session_scope() as session:
            return session.query(Quotation).filter_by(qoute_status=status).order_by(desc(Quotation.date)).all()
    
    @handle_errors("QuotationRepository")
    def get_quotations_by_branch(self, branch_id: str, session: Optional[Session] = None) -> List[Quotation]:
        """
        Retrieve all quotations for a specific branch.
        
        Args:
            branch_id: The unique identifier of the branch
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of quotations for the branch
        """
        if session:
            return session.query(Quotation).filter_by(branch_id=branch_id).order_by(desc(Quotation.date)).all()
        
        with session_scope() as session:
            return session.query(Quotation).filter_by(branch_id=branch_id).order_by(desc(Quotation.date)).all()
    
    @handle_errors("QuotationRepository")
    def get_quotations_by_user(self, user_id: str, session: Optional[Session] = None) -> List[Quotation]:
        """
        Retrieve all quotations created by a specific user.
        
        Args:
            user_id: The unique identifier of the user
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of quotations created by the user
        """
        if session:
            return session.query(Quotation).filter_by(user_id=user_id).order_by(desc(Quotation.date)).all()
        
        with session_scope() as session:
            return session.query(Quotation).filter_by(user_id=user_id).order_by(desc(Quotation.date)).all()
    
    @handle_errors("QuotationRepository")
    def get_quotations_by_date_range(self, start_date: datetime, end_date: datetime, session: Optional[Session] = None) -> List[Quotation]:
        """
        Retrieve quotations within a specific date range.
        
        Args:
            start_date: Start date for the range
            end_date: End date for the range
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of quotations within the date range
        """
        if session:
            return session.query(Quotation).filter(
                and_(
                    Quotation.date >= start_date,
                    Quotation.date <= end_date
                )
            ).order_by(desc(Quotation.date)).all()
        
        with session_scope() as session:
            return session.query(Quotation).filter(
                and_(
                    Quotation.date >= start_date,
                    Quotation.date <= end_date
                )
            ).order_by(desc(Quotation.date)).all()
    
    @handle_errors("QuotationRepository")
    def get_quotations_by_amount_range(self, min_amount: float, max_amount: float, session: Optional[Session] = None) -> List[Quotation]:
        """
        Retrieve quotations within a specific amount range.
        
        Args:
            min_amount: Minimum amount
            max_amount: Maximum amount
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of quotations within the amount range
        """
        if session:
            return session.query(Quotation).filter(
                and_(
                    Quotation.grand_total >= min_amount,
                    Quotation.grand_total <= max_amount
                )
            ).order_by(desc(Quotation.date)).all()
        
        with session_scope() as session:
            return session.query(Quotation).filter(
                and_(
                    Quotation.grand_total >= min_amount,
                    Quotation.grand_total <= max_amount
                )
            ).order_by(desc(Quotation.date)).all()
    
    @handle_errors("QuotationRepository")
    def get_pending_quotations(self, session: Optional[Session] = None) -> List[Quotation]:
        """
        Retrieve all pending quotations.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of pending quotations
        """
        if session:
            return session.query(Quotation).filter_by(qoute_status=QuoteStatusEnum.PENDING).order_by(desc(Quotation.date)).all()
        
        with session_scope() as session:
            return session.query(Quotation).filter_by(qoute_status=QuoteStatusEnum.PENDING).order_by(desc(Quotation.date)).all()
    
    @handle_errors("QuotationRepository")
    def get_approved_quotations(self, session: Optional[Session] = None) -> List[Quotation]:
        """
        Retrieve all approved quotations.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of approved quotations
        """
        if session:
            return session.query(Quotation).filter_by(qoute_status=QuoteStatusEnum.APPROVED).order_by(desc(Quotation.date)).all()
        
        with session_scope() as session:
            return session.query(Quotation).filter_by(qoute_status=QuoteStatusEnum.APPROVED).order_by(desc(Quotation.date)).all()
    
    @handle_errors("QuotationRepository")
    def get_rejected_quotations(self, session: Optional[Session] = None) -> List[Quotation]:
        """
        Retrieve all rejected quotations.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of rejected quotations
        """
        if session:
            return session.query(Quotation).filter_by(qoute_status=QuoteStatusEnum.REJECTED).order_by(desc(Quotation.date)).all()
        
        with session_scope() as session:
            return session.query(Quotation).filter_by(qoute_status=QuoteStatusEnum.REJECTED).order_by(desc(Quotation.date)).all()
    
    @handle_errors("QuotationRepository")
    def update_quotation_status(self, quotation_id: str, new_status: QuoteStatusEnum, session: Optional[Session] = None) -> bool:
        """
        Update the status of a quotation.
        
        Args:
            quotation_id: The unique identifier of the quotation
            new_status: The new status to set
            session: Optional database session (if None, creates a new one)
            
        Returns:
            True if updated successfully
        """
        if session:
            quotation = session.query(Quotation).filter_by(id=quotation_id).first()
            if quotation:
                quotation.qoute_status = new_status
                session.flush()
                return True
            return False
        
        with session_scope() as session:
            return self.update_quotation_status(quotation_id, new_status, session)
    
    @handle_errors("QuotationRepository")
    def get_quotation_statistics(self, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Get quotation statistics for dashboard/reporting.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing quotation statistics
        """
        if session:
            total_quotations = session.query(Quotation).count()
            pending_quotations = session.query(Quotation).filter_by(qoute_status=QuoteStatusEnum.PENDING).count()
            approved_quotations = session.query(Quotation).filter_by(qoute_status=QuoteStatusEnum.APPROVED).count()
            rejected_quotations = session.query(Quotation).filter_by(qoute_status=QuoteStatusEnum.REJECTED).count()
            
            # Calculate total amounts
            total_amount = session.query(Quotation).with_entities(
                session.query(Quotation.grand_total).label('total')
            ).all()
            total_amount_value = sum([quotation.total for quotation in total_amount if quotation.total])
            
            # Calculate total amount by status
            status_amounts = {}
            for status in QuoteStatusEnum:
                amount_result = session.query(Quotation).filter_by(qoute_status=status).with_entities(
                    session.query(Quotation.grand_total).label('total')
                ).all()
                status_amounts[status.value] = sum([quotation.total for quotation in amount_result if quotation.total])
            
            return {
                'total_quotations': total_quotations,
                'pending_quotations': pending_quotations,
                'approved_quotations': approved_quotations,
                'rejected_quotations': rejected_quotations,
                'total_amount': total_amount_value,
                'status_amounts': status_amounts
            }
        
        with session_scope() as session:
            return self.get_quotation_statistics(session)
