"""
Expense Repository

This module provides the ExpenseRepository class that implements data access
operations specific to the Expense entity in the 3D Store application.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from app.repositories.base import BaseRepository
from app.expense.model import Expense, ExpenseCategory
from app.utilities.error_utils import handle_errors
from app.utilities.db_utils import session_scope
from app.common.enum import ExpenseStatusEnum
from app.common.queries import create_sorters, filter_and_sort_query
from app.common import filters_serialization
from sqlalchemy_filters import apply_pagination
from datetime import datetime, timezone

class ExpenseRepository(BaseRepository[Expense]):
    """
    Repository class for Expense entity operations.
    
    Extends BaseRepository with Expense-specific data access methods.
    """
    
    def __init__(self):
        super().__init__(Expense)
    
    @handle_errors("ExpenseRepository")
    def get_expenses_with_category(self, filter_obj, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Retrieve expenses with their associated category information.
        
        Args:
            filter_obj: Filter object containing pagination and sorting parameters
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing expenses with categories and pagination metadata
        """
        if session:
            query = session.query(Expense, ExpenseCategory).outerjoin(ExpenseCategory, Expense.category_id == ExpenseCategory.id)
            
            # Apply sorting
            if filter_obj.sort is None:
                filter_obj.sorters = create_sorters('date', 'desc')
            query = filter_and_sort_query(filter_obj.filters, filter_obj.sorters, query, [Expense, ExpenseCategory])
            
            # Apply pagination
            query, pagination = apply_pagination(
                query, 
                page_number=int(filter_obj.page), 
                page_size=int(filter_obj.per_page)
            )
            
            expenses = query.all()
            
            return {
                'expenses': expenses,
                'filters': filters_serialization.get_pagination_serialization(
                    pagination, filter_obj.sort, filter_obj.sort_order, filter_obj.queries
                )
            }
        
        with session_scope() as session:
            return self.get_expenses_with_category(filter_obj, session)
    
    @handle_errors("ExpenseRepository")
    def get_expenses_by_category(self, category_id: str, session: Optional[Session] = None) -> List[Expense]:
        """
        Retrieve all expenses for a specific category.
        
        Args:
            category_id: The unique identifier of the category
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of expenses for the category
        """
        if session:
            return session.query(Expense).filter_by(category_id=category_id).order_by(desc(Expense.date)).all()
        
        with session_scope() as session:
            return session.query(Expense).filter_by(category_id=category_id).order_by(desc(Expense.date)).all()
    
    @handle_errors("ExpenseRepository")
    def get_expenses_by_status(self, status: ExpenseStatusEnum, session: Optional[Session] = None) -> List[Expense]:
        """
        Retrieve all expenses with a specific status.
        
        Args:
            status: The expense status to filter by
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of expenses with the specified status
        """
        if session:
            return session.query(Expense).filter_by(status=status).order_by(desc(Expense.date)).all()
        
        with session_scope() as session:
            return session.query(Expense).filter_by(status=status).order_by(desc(Expense.date)).all()
    
    @handle_errors("ExpenseRepository")
    def get_expenses_by_date_range(self, start_date: datetime, end_date: datetime, session: Optional[Session] = None) -> List[Expense]:
        """
        Retrieve expenses within a specific date range.
        
        Args:
            start_date: Start date for the range
            end_date: End date for the range
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of expenses within the date range
        """
        if session:
            return session.query(Expense).filter(
                and_(
                    Expense.date >= start_date,
                    Expense.date <= end_date
                )
            ).order_by(desc(Expense.date)).all()
        
        with session_scope() as session:
            return session.query(Expense).filter(
                and_(
                    Expense.date >= start_date,
                    Expense.date <= end_date
                )
            ).order_by(desc(Expense.date)).all()
    
    @handle_errors("ExpenseRepository")
    def get_expenses_by_amount_range(self, min_amount: float, max_amount: float, session: Optional[Session] = None) -> List[Expense]:
        """
        Retrieve expenses within a specific amount range.
        
        Args:
            min_amount: Minimum amount
            max_amount: Maximum amount
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of expenses within the amount range
        """
        if session:
            return session.query(Expense).filter(
                and_(
                    Expense.amount >= min_amount,
                    Expense.amount <= max_amount
                )
            ).order_by(desc(Expense.date)).all()
        
        with session_scope() as session:
            return session.query(Expense).filter(
                and_(
                    Expense.amount >= min_amount,
                    Expense.amount <= max_amount
                )
            ).order_by(desc(Expense.date)).all()
    
    @handle_errors("ExpenseRepository")
    def get_expenses_by_fiscal_year(self, fiscal_year_id: str, session: Optional[Session] = None) -> List[Expense]:
        """
        Retrieve all expenses for a specific fiscal year.
        
        Args:
            fiscal_year_id: The unique identifier of the fiscal year
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of expenses for the fiscal year
        """
        if session:
            return session.query(Expense).filter_by(fiscal_year_id=fiscal_year_id).order_by(desc(Expense.date)).all()
        
        with session_scope() as session:
            return session.query(Expense).filter_by(fiscal_year_id=fiscal_year_id).order_by(desc(Expense.date)).all()
    
    @handle_errors("ExpenseRepository")
    def get_pending_expenses(self, session: Optional[Session] = None) -> List[Expense]:
        """
        Retrieve all pending expenses.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of pending expenses
        """
        if session:
            return session.query(Expense).filter_by(status=ExpenseStatusEnum.PENDING).order_by(desc(Expense.date)).all()
        
        with session_scope() as session:
            return session.query(Expense).filter_by(status=ExpenseStatusEnum.PENDING).order_by(desc(Expense.date)).all()
    
    @handle_errors("ExpenseRepository")
    def get_approved_expenses(self, session: Optional[Session] = None) -> List[Expense]:
        """
        Retrieve all approved expenses.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of approved expenses
        """
        if session:
            return session.query(Expense).filter_by(status=ExpenseStatusEnum.APPROVED).order_by(desc(Expense.date)).all()
        
        with session_scope() as session:
            return session.query(Expense).filter_by(status=ExpenseStatusEnum.APPROVED).order_by(desc(Expense.date)).all()
    
    @handle_errors("ExpenseRepository")
    def get_rejected_expenses(self, session: Optional[Session] = None) -> List[Expense]:
        """
        Retrieve all rejected expenses.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of rejected expenses
        """
        if session:
            return session.query(Expense).filter_by(status=ExpenseStatusEnum.REJECTED).order_by(desc(Expense.date)).all()
        
        with session_scope() as session:
            return session.query(Expense).filter_by(status=ExpenseStatusEnum.REJECTED).order_by(desc(Expense.date)).all()
    
    @handle_errors("ExpenseRepository")
    def update_expense_status(self, expense_id: str, new_status: ExpenseStatusEnum, session: Optional[Session] = None) -> bool:
        """
        Update the status of an expense.
        
        Args:
            expense_id: The unique identifier of the expense
            new_status: The new status to set
            session: Optional database session (if None, creates a new one)
            
        Returns:
            True if updated successfully
        """
        if session:
            expense = session.query(Expense).filter_by(id=expense_id).first()
            if expense:
                expense.status = new_status
                session.flush()
                return True
            return False
        
        with session_scope() as session:
            return self.update_expense_status(expense_id, new_status, session)
    
    @handle_errors("ExpenseRepository")
    def get_expense_statistics(self, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Get expense statistics for dashboard/reporting.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing expense statistics
        """
        if session:
            total_expenses = session.query(Expense).count()
            pending_expenses = session.query(Expense).filter_by(status=ExpenseStatusEnum.PENDING).count()
            approved_expenses = session.query(Expense).filter_by(status=ExpenseStatusEnum.APPROVED).count()
            rejected_expenses = session.query(Expense).filter_by(status=ExpenseStatusEnum.REJECTED).count()
            
            # Calculate total amount
            total_amount = session.query(Expense).with_entities(
                session.query(Expense.amount).label('total')
            ).all()
            total_amount_value = sum([expense.total for expense in total_amount if expense.total])
            
            # Calculate total amount by status
            status_amounts = {}
            for status in ExpenseStatusEnum:
                amount_result = session.query(Expense).filter_by(status=status).with_entities(
                    session.query(Expense.amount).label('total')
                ).all()
                status_amounts[status.value] = sum([expense.total for expense in amount_result if expense.total])
            
            return {
                'total_expenses': total_expenses,
                'pending_expenses': pending_expenses,
                'approved_expenses': approved_expenses,
                'rejected_expenses': rejected_expenses,
                'total_amount': total_amount_value,
                'status_amounts': status_amounts
            }
        
        with session_scope() as session:
            return self.get_expense_statistics(session)
    
    @handle_errors("ExpenseRepository")
    def get_expenses_by_category_summary(self, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Get expense summary by category.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing expense summary by category
        """
        if session:
            # Get all expenses with their categories
            expenses = session.query(Expense).options(joinedload(Expense.category)).all()
            
            category_summary = {}
            for expense in expenses:
                category_name = expense.category.name if expense.category else 'Uncategorized'
                if category_name not in category_summary:
                    category_summary[category_name] = {
                        'count': 0,
                        'total_amount': 0.0,
                        'pending_count': 0,
                        'approved_count': 0,
                        'rejected_count': 0
                    }
                
                category_summary[category_name]['count'] += 1
                category_summary[category_name]['total_amount'] += float(expense.amount)
                
                if expense.status == ExpenseStatusEnum.PENDING:
                    category_summary[category_name]['pending_count'] += 1
                elif expense.status == ExpenseStatusEnum.APPROVED:
                    category_summary[category_name]['approved_count'] += 1
                elif expense.status == ExpenseStatusEnum.REJECTED:
                    category_summary[category_name]['rejected_count'] += 1
            
            return category_summary
        
        with session_scope() as session:
            return self.get_expenses_by_category_summary(session)
