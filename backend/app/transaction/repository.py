"""
Transaction Repository

This module provides the TransactionRepository class that implements data access
operations specific to the Transaction entity in the 3D Store application.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from app.repositories.base import BaseRepository
from app.transaction.model import Transaction
from app.product.model import Product
from app.branch.model import Branch
from app.financial.model import FiscalYear
from app.utilities.error_utils import handle_errors
from app.utilities.db_utils import session_scope
from app.common.enum import TransactionType
from datetime import datetime, timezone, timedelta

class TransactionRepository(BaseRepository[Transaction]):
    """
    Repository class for Transaction entity operations.
    
    Extends BaseRepository with Transaction-specific data access methods.
    """
    
    def __init__(self):
        super().__init__(Transaction)
    
    @handle_errors("TransactionRepository")
    def get_transactions_with_details(self, transaction_id: str, session: Optional[Session] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve a transaction with all its related details.
        
        Args:
            transaction_id: The unique identifier of the transaction
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing transaction with all related details
        """
        if session:
            transaction = session.query(Transaction).options(
                joinedload(Transaction.product),
                joinedload(Transaction.from_location),
                joinedload(Transaction.to_location),
                joinedload(Transaction.financial_year)
            ).filter_by(id=transaction_id).first()
            
            if not transaction:
                return None
            
            return {
                'transaction': transaction,
                'product': transaction.product,
                'from_location': transaction.from_location,
                'to_location': transaction.to_location,
                'financial_year': transaction.financial_year
            }
        
        with session_scope() as session:
            return self.get_transactions_with_details(transaction_id, session)
    
    @handle_errors("TransactionRepository")
    def get_transactions_by_product(self, product_id: str, session: Optional[Session] = None) -> List[Transaction]:
        """
        Retrieve all transactions for a specific product.
        
        Args:
            product_id: The unique identifier of the product
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of transactions for the product
        """
        if session:
            return session.query(Transaction).filter_by(product_id=product_id).order_by(desc(Transaction.transaction_date)).all()
        
        with session_scope() as session:
            return session.query(Transaction).filter_by(product_id=product_id).order_by(desc(Transaction.transaction_date)).all()
    
    @handle_errors("TransactionRepository")
    def get_transactions_by_type(self, transaction_type: TransactionType, session: Optional[Session] = None) -> List[Transaction]:
        """
        Retrieve all transactions of a specific type.
        
        Args:
            transaction_type: The type of transaction
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of transactions of the specified type
        """
        if session:
            return session.query(Transaction).filter_by(transaction_type=transaction_type).order_by(desc(Transaction.transaction_date)).all()
        
        with session_scope() as session:
            return session.query(Transaction).filter_by(transaction_type=transaction_type).order_by(desc(Transaction.transaction_date)).all()
    
    @handle_errors("TransactionRepository")
    def get_transactions_by_location(self, location_id: str, location_type: str = 'from', session: Optional[Session] = None) -> List[Transaction]:
        """
        Retrieve transactions by location (from or to).
        
        Args:
            location_id: The unique identifier of the location
            location_type: Type of location (from or to)
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of transactions for the location
        """
        if session:
            if location_type == 'from':
                return session.query(Transaction).filter_by(from_location_id=location_id).order_by(desc(Transaction.transaction_date)).all()
            else:
                return session.query(Transaction).filter_by(to_location_id=location_id).order_by(desc(Transaction.transaction_date)).all()
        
        with session_scope() as session:
            return self.get_transactions_by_location(location_id, location_type, session)
    
    @handle_errors("TransactionRepository")
    def get_transactions_by_fiscal_year(self, fiscal_year_id: str, session: Optional[Session] = None) -> List[Transaction]:
        """
        Retrieve all transactions for a specific fiscal year.
        
        Args:
            fiscal_year_id: The unique identifier of the fiscal year
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of transactions for the fiscal year
        """
        if session:
            return session.query(Transaction).filter_by(financial_year_id=fiscal_year_id).order_by(desc(Transaction.transaction_date)).all()
        
        with session_scope() as session:
            return session.query(Transaction).filter_by(financial_year_id=fiscal_year_id).order_by(desc(Transaction.transaction_date)).all()
    
    @handle_errors("TransactionRepository")
    def get_transactions_by_date_range(self, start_date: datetime, end_date: datetime, session: Optional[Session] = None) -> List[Transaction]:
        """
        Retrieve transactions within a specific date range.
        
        Args:
            start_date: Start date for the range
            end_date: End date for the range
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of transactions within the date range
        """
        if session:
            return session.query(Transaction).filter(
                and_(
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date
                )
            ).order_by(desc(Transaction.transaction_date)).all()
        
        with session_scope() as session:
            return session.query(Transaction).filter(
                and_(
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date
                )
            ).order_by(desc(Transaction.transaction_date)).all()
    
    @handle_errors("TransactionRepository")
    def get_recent_transactions(self, limit: int = 10, session: Optional[Session] = None) -> List[Transaction]:
        """
        Retrieve the most recent transactions.
        
        Args:
            limit: Maximum number of transactions to return
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of recent transactions
        """
        if session:
            return session.query(Transaction).order_by(desc(Transaction.transaction_date)).limit(limit).all()
        
        with session_scope() as session:
            return session.query(Transaction).order_by(desc(Transaction.transaction_date)).limit(limit).all()
    
    @handle_errors("TransactionRepository")
    def get_transactions_by_quantity_range(self, min_quantity: int, max_quantity: int, session: Optional[Session] = None) -> List[Transaction]:
        """
        Retrieve transactions within a specific quantity range.
        
        Args:
            min_quantity: Minimum quantity
            max_quantity: Maximum quantity
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of transactions within the quantity range
        """
        if session:
            return session.query(Transaction).filter(
                and_(
                    Transaction.quantity >= min_quantity,
                    Transaction.quantity <= max_quantity
                )
            ).order_by(desc(Transaction.transaction_date)).all()
        
        with session_scope() as session:
            return session.query(Transaction).filter(
                and_(
                    Transaction.quantity >= min_quantity,
                    Transaction.quantity <= max_quantity
                )
            ).order_by(desc(Transaction.transaction_date)).all()
    
    @handle_errors("TransactionRepository")
    def get_transaction_statistics(self, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Get transaction statistics for dashboard/reporting.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing transaction statistics
        """
        if session:
            total_transactions = session.query(Transaction).count()
            
            # Count transactions by type
            transaction_types = {}
            for transaction_type in TransactionType:
                count = session.query(Transaction).filter_by(transaction_type=transaction_type).count()
                transaction_types[transaction_type.value] = count
            
            # Get total quantity moved
            total_quantity = session.query(Transaction).with_entities(
                session.query(Transaction.quantity).label('total')
            ).all()
            total_quantity_value = sum([transaction.total for transaction in total_quantity if transaction.total])
            
            # Get recent transactions count (last 30 days)
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            recent_transactions = session.query(Transaction).filter(
                Transaction.transaction_date >= thirty_days_ago
            ).count()
            
            return {
                'total_transactions': total_transactions,
                'transaction_types': transaction_types,
                'total_quantity': total_quantity_value,
                'recent_transactions': recent_transactions
            }
        
        with session_scope() as session:
            return self.get_transaction_statistics(session)
    
    @handle_errors("TransactionRepository")
    def get_product_movement_summary(self, product_id: str, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Get movement summary for a specific product.
        
        Args:
            product_id: The unique identifier of the product
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing product movement summary
        """
        if session:
            transactions = session.query(Transaction).filter_by(product_id=product_id).all()
            
            total_in = sum([t.quantity for t in transactions if t.transaction_type in [TransactionType.IN, TransactionType.RECEIVED]])
            total_out = sum([t.quantity for t in transactions if t.transaction_type in [TransactionType.OUT, TransactionType.SOLD]])
            total_transferred = sum([t.quantity for t in transactions if t.transaction_type == TransactionType.TRANSFER])
            
            return {
                'total_in': total_in,
                'total_out': total_out,
                'total_transferred': total_transferred,
                'net_movement': total_in - total_out,
                'total_transactions': len(transactions)
            }
        
        with session_scope() as session:
            return self.get_product_movement_summary(product_id, session)
    
    @handle_errors("TransactionRepository")
    def get_location_movement_summary(self, location_id: str, location_type: str = 'from', session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Get movement summary for a specific location.
        
        Args:
            location_id: The unique identifier of the location
            location_type: Type of location (from or to)
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing location movement summary
        """
        if session:
            if location_type == 'from':
                transactions = session.query(Transaction).filter_by(from_location_id=location_id).all()
            else:
                transactions = session.query(Transaction).filter_by(to_location_id=location_id).all()
            
            total_quantity = sum([t.quantity for t in transactions])
            transaction_count = len(transactions)
            
            # Count by transaction type
            type_counts = {}
            for transaction_type in TransactionType:
                count = len([t for t in transactions if t.transaction_type == transaction_type])
                type_counts[transaction_type.value] = count
            
            return {
                'total_quantity': total_quantity,
                'transaction_count': transaction_count,
                'type_counts': type_counts
            }
        
        with session_scope() as session:
            return self.get_location_movement_summary(location_id, location_type, session)
