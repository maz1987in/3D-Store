"""
Customer Repository

This module provides the CustomerRepository class that implements data access
operations specific to the Customer entity in the 3D Store application.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from app.repositories.base import BaseRepository
from app.customers.model import Customer
from app.utilities.error_utils import handle_errors
from app.utilities.db_utils import session_scope
from datetime import datetime, timezone

class CustomerRepository(BaseRepository[Customer]):
    """
    Repository class for Customer entity operations.
    
    Extends BaseRepository with Customer-specific data access methods.
    """
    
    def __init__(self):
        super().__init__(Customer)
    
    @handle_errors("CustomerRepository")
    def get_customer_by_user_id(self, user_id: str, session: Optional[Session] = None) -> Optional[Customer]:
        """
        Retrieve a customer by their associated user ID.
        
        Args:
            user_id: The unique identifier of the user
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The customer if found, None otherwise
        """
        if session:
            return session.query(Customer).filter_by(user_id=user_id).first()
        
        with session_scope() as session:
            return session.query(Customer).filter_by(user_id=user_id).first()
    
    @handle_errors("CustomerRepository")
    def get_customer_by_email(self, email: str, session: Optional[Session] = None) -> Optional[Customer]:
        """
        Retrieve a customer by email address.
        
        Args:
            email: The email address to search for
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The customer if found, None otherwise
        """
        if session:
            return session.query(Customer).filter_by(email=email).first()
        
        with session_scope() as session:
            return session.query(Customer).filter_by(email=email).first()
    
    @handle_errors("CustomerRepository")
    def get_customer_by_mobile(self, mobile: str, session: Optional[Session] = None) -> Optional[Customer]:
        """
        Retrieve a customer by mobile number.
        
        Args:
            mobile: The mobile number to search for
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The customer if found, None otherwise
        """
        if session:
            return session.query(Customer).filter_by(mobile=mobile).first()
        
        with session_scope() as session:
            return session.query(Customer).filter_by(mobile=mobile).first()
    
    @handle_errors("CustomerRepository")
    def get_customer_by_code(self, customer_code: str, session: Optional[Session] = None) -> Optional[Customer]:
        """
        Retrieve a customer by their customer code.
        
        Args:
            customer_code: The customer code to search for
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The customer if found, None otherwise
        """
        if session:
            return session.query(Customer).filter_by(customer_code=customer_code).first()
        
        with session_scope() as session:
            return session.query(Customer).filter_by(customer_code=customer_code).first()
    
    @handle_errors("CustomerRepository")
    def get_customers_by_type(self, customer_type: str, session: Optional[Session] = None) -> List[Customer]:
        """
        Retrieve all customers of a specific type.
        
        Args:
            customer_type: The type of customer (individual, business, wholesale)
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of customers of the specified type
        """
        if session:
            return session.query(Customer).filter_by(customer_type=customer_type).all()
        
        with session_scope() as session:
            return session.query(Customer).filter_by(customer_type=customer_type).all()
    
    @handle_errors("CustomerRepository")
    def get_active_customers(self, session: Optional[Session] = None) -> List[Customer]:
        """
        Retrieve all active customers.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of active customers
        """
        if session:
            return session.query(Customer).filter_by(status='active').all()
        
        with session_scope() as session:
            return session.query(Customer).filter_by(status='active').all()
    
    @handle_errors("CustomerRepository")
    def get_verified_customers(self, session: Optional[Session] = None) -> List[Customer]:
        """
        Retrieve all verified customers.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of verified customers
        """
        if session:
            return session.query(Customer).filter_by(is_verified=True).all()
        
        with session_scope() as session:
            return session.query(Customer).filter_by(is_verified=True).all()
    
    @handle_errors("CustomerRepository")
    def get_customers_by_city(self, city: str, session: Optional[Session] = None) -> List[Customer]:
        """
        Retrieve all customers in a specific city.
        
        Args:
            city: The city name to filter by
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of customers in the specified city
        """
        if session:
            return session.query(Customer).filter_by(city=city).all()
        
        with session_scope() as session:
            return session.query(Customer).filter_by(city=city).all()
    
    @handle_errors("CustomerRepository")
    def get_customers_by_country(self, country: str, session: Optional[Session] = None) -> List[Customer]:
        """
        Retrieve all customers in a specific country.
        
        Args:
            country: The country name to filter by
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of customers in the specified country
        """
        if session:
            return session.query(Customer).filter_by(country=country).all()
        
        with session_scope() as session:
            return session.query(Customer).filter_by(country=country).all()
    
    @handle_errors("CustomerRepository")
    def get_business_customers(self, session: Optional[Session] = None) -> List[Customer]:
        """
        Retrieve all business customers.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of business customers
        """
        if session:
            return session.query(Customer).filter_by(customer_type='business').all()
        
        with session_scope() as session:
            return session.query(Customer).filter_by(customer_type='business').all()
    
    @handle_errors("CustomerRepository")
    def search_customers(self, search_term: str, session: Optional[Session] = None) -> List[Customer]:
        """
        Search customers by name, email, mobile, or business name.
        
        Args:
            search_term: The search term to look for
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of customers matching the search term
        """
        if session:
            search_pattern = f"%{search_term}%"
            return session.query(Customer).filter(
                or_(
                    Customer.email.ilike(search_pattern),
                    Customer.mobile.ilike(search_pattern),
                    Customer.business_name.ilike(search_pattern)
                )
            ).all()
        
        with session_scope() as session:
            return self.search_customers(search_term, session)
    
    @handle_errors("CustomerRepository")
    def get_customers_by_registration_date(self, start_date: datetime, end_date: datetime, session: Optional[Session] = None) -> List[Customer]:
        """
        Retrieve customers registered within a specific date range.
        
        Args:
            start_date: Start date for the range
            end_date: End date for the range
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of customers registered within the date range
        """
        if session:
            return session.query(Customer).filter(
                and_(
                    Customer.create_date >= start_date,
                    Customer.create_date <= end_date
                )
            ).order_by(desc(Customer.create_date)).all()
        
        with session_scope() as session:
            return session.query(Customer).filter(
                and_(
                    Customer.create_date >= start_date,
                    Customer.create_date <= end_date
                )
            ).order_by(desc(Customer.create_date)).all()
    
    @handle_errors("CustomerRepository")
    def get_recent_customers(self, limit: int = 10, session: Optional[Session] = None) -> List[Customer]:
        """
        Retrieve the most recently registered customers.
        
        Args:
            limit: Maximum number of customers to return
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of recent customers
        """
        if session:
            return session.query(Customer).order_by(desc(Customer.create_date)).limit(limit).all()
        
        with session_scope() as session:
            return session.query(Customer).order_by(desc(Customer.create_date)).limit(limit).all()
    
    @handle_errors("CustomerRepository")
    def verify_customer(self, customer_id: str, session: Optional[Session] = None) -> bool:
        """
        Verify a customer account.
        
        Args:
            customer_id: The unique identifier of the customer
            session: Optional database session (if None, creates a new one)
            
        Returns:
            True if verified successfully
        """
        if session:
            customer = session.query(Customer).filter_by(id=customer_id).first()
            if customer:
                customer.is_verified = True
                session.flush()
                return True
            return False
        
        with session_scope() as session:
            return self.verify_customer(customer_id, session)
    
    @handle_errors("CustomerRepository")
    def update_customer_status(self, customer_id: str, status: str, session: Optional[Session] = None) -> bool:
        """
        Update a customer's status.
        
        Args:
            customer_id: The unique identifier of the customer
            status: The new status (active, inactive, suspended)
            session: Optional database session (if None, creates a new one)
            
        Returns:
            True if updated successfully
        """
        if session:
            customer = session.query(Customer).filter_by(id=customer_id).first()
            if customer:
                customer.status = status
                session.flush()
                return True
            return False
        
        with session_scope() as session:
            return self.update_customer_status(customer_id, status, session)
    
    @handle_errors("CustomerRepository")
    def get_customer_statistics(self, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Get customer statistics for dashboard/reporting.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing customer statistics
        """
        if session:
            total_customers = session.query(Customer).count()
            active_customers = session.query(Customer).filter_by(status='active').count()
            verified_customers = session.query(Customer).filter_by(is_verified=True).count()
            business_customers = session.query(Customer).filter_by(customer_type='business').count()
            
            # Count customers by type
            customer_types = {}
            for customer_type in ['individual', 'business', 'wholesale']:
                count = session.query(Customer).filter_by(customer_type=customer_type).count()
                customer_types[customer_type] = count
            
            return {
                'total_customers': total_customers,
                'active_customers': active_customers,
                'verified_customers': verified_customers,
                'business_customers': business_customers,
                'customer_types': customer_types
            }
        
        with session_scope() as session:
            return self.get_customer_statistics(session)
