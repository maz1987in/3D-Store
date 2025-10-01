"""
Order Repository

This module provides the OrderRepository class that implements data access
operations specific to the Order entity in the 3D Store application.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from app.repositories.base import BaseRepository
from app.order.model import Order, OrderItem
from app.customers.model import Customer
from app.supplier.model import Supplier
from app.utilities.error_utils import handle_errors
from app.utilities.db_utils import session_scope
from app.common.enum import OrderStatusEnum
from app.common.queries import create_sorters, filter_and_sort_query
from app.common import filters_serialization
from sqlalchemy_filters import apply_pagination
from datetime import datetime, timezone

class OrderRepository(BaseRepository[Order]):
    """
    Repository class for Order entity operations.
    
    Extends BaseRepository with Order-specific data access methods.
    """
    
    def __init__(self):
        super().__init__(Order)
    
    @handle_errors("OrderRepository")
    def get_orders_with_supplier(self, filter_obj, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Retrieve orders with their associated supplier information.
        
        Args:
            filter_obj: Filter object containing pagination and sorting parameters
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing orders with suppliers and pagination metadata
        """
        if session:
            query = session.query(Order, Supplier).outerjoin(Supplier, Order.supplier_id == Supplier.id)
            
            # Apply sorting
            if filter_obj.sort is None:
                filter_obj.sorters = create_sorters('modified_date', 'desc')
            query = filter_and_sort_query(filter_obj.filters, filter_obj.sorters, query, [Order, Supplier])
            
            # Apply pagination
            query, pagination = apply_pagination(
                query, 
                page_number=int(filter_obj.page), 
                page_size=int(filter_obj.per_page)
            )
            
            orders = query.all()
            
            return {
                'orders': orders,
                'filters': filters_serialization.get_pagination_serialization(
                    pagination, filter_obj.sort, filter_obj.sort_order, filter_obj.queries
                )
            }
        
        with session_scope() as session:
            return self.get_orders_with_supplier(filter_obj, session)
    
    @handle_errors("OrderRepository")
    def get_order_with_details(self, order_id: str, session: Optional[Session] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve an order with all its related details (customer, items, etc.).
        
        Args:
            order_id: The unique identifier of the order
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing order with all related details
        """
        if session:
            order = session.query(Order).options(
                joinedload(Order.customer),
                joinedload(Order.shipping_info),
                joinedload(Order.print_jobs),
                joinedload(Order.order_items)
            ).filter_by(id=order_id).first()
            
            if not order:
                return None
            
            return {
                'order': order,
                'customer': order.customer,
                'shipping_info': order.shipping_info,
                'print_jobs': order.print_jobs,
                'order_items': order.order_items
            }
        
        with session_scope() as session:
            return self.get_order_with_details(order_id, session)
    
    @handle_errors("OrderRepository")
    def get_orders_by_customer(self, customer_id: str, session: Optional[Session] = None) -> List[Order]:
        """
        Retrieve all orders for a specific customer.
        
        Args:
            customer_id: The unique identifier of the customer
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of orders for the customer
        """
        if session:
            return session.query(Order).filter_by(customer_id=customer_id).order_by(desc(Order.order_date)).all()
        
        with session_scope() as session:
            return session.query(Order).filter_by(customer_id=customer_id).order_by(desc(Order.order_date)).all()
    
    @handle_errors("OrderRepository")
    def get_orders_by_status(self, status: OrderStatusEnum, session: Optional[Session] = None) -> List[Order]:
        """
        Retrieve all orders with a specific status.
        
        Args:
            status: The order status to filter by
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of orders with the specified status
        """
        if session:
            return session.query(Order).filter_by(status=status).all()
        
        with session_scope() as session:
            return session.query(Order).filter_by(status=status).all()
    
    @handle_errors("OrderRepository")
    def get_orders_by_type(self, order_type: str, session: Optional[Session] = None) -> List[Order]:
        """
        Retrieve all orders of a specific type.
        
        Args:
            order_type: The type of order (print_service, ready_made, mixed)
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of orders of the specified type
        """
        if session:
            return session.query(Order).filter_by(order_type=order_type).all()
        
        with session_scope() as session:
            return session.query(Order).filter_by(order_type=order_type).all()
    
    @handle_errors("OrderRepository")
    def get_orders_by_date_range(self, start_date: datetime, end_date: datetime, session: Optional[Session] = None) -> List[Order]:
        """
        Retrieve orders within a specific date range.
        
        Args:
            start_date: Start date for the range
            end_date: End date for the range
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of orders within the date range
        """
        if session:
            return session.query(Order).filter(
                and_(
                    Order.order_date >= start_date,
                    Order.order_date <= end_date
                )
            ).order_by(desc(Order.order_date)).all()
        
        with session_scope() as session:
            return session.query(Order).filter(
                and_(
                    Order.order_date >= start_date,
                    Order.order_date <= end_date
                )
            ).order_by(desc(Order.order_date)).all()
    
    @handle_errors("OrderRepository")
    def get_orders_by_priority(self, priority: str, session: Optional[Session] = None) -> List[Order]:
        """
        Retrieve orders with a specific priority.
        
        Args:
            priority: The priority level (low, normal, high, urgent)
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of orders with the specified priority
        """
        if session:
            return session.query(Order).filter_by(priority=priority).all()
        
        with session_scope() as session:
            return session.query(Order).filter_by(priority=priority).all()
    
    @handle_errors("OrderRepository")
    def get_orders_by_payment_status(self, payment_status: str, session: Optional[Session] = None) -> List[Order]:
        """
        Retrieve orders with a specific payment status.
        
        Args:
            payment_status: The payment status (pending, paid, partial, refunded)
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of orders with the specified payment status
        """
        if session:
            return session.query(Order).filter_by(payment_status=payment_status).all()
        
        with session_scope() as session:
            return session.query(Order).filter_by(payment_status=payment_status).all()
    
    @handle_errors("OrderRepository")
    def get_orders_by_supplier(self, supplier_id: str, session: Optional[Session] = None) -> List[Order]:
        """
        Retrieve all orders for a specific supplier.
        
        Args:
            supplier_id: The unique identifier of the supplier
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of orders for the supplier
        """
        if session:
            return session.query(Order).filter_by(supplier_id=supplier_id).all()
        
        with session_scope() as session:
            return session.query(Order).filter_by(supplier_id=supplier_id).all()
    
    @handle_errors("OrderRepository")
    def get_orders_by_total_range(self, min_total: float, max_total: float, session: Optional[Session] = None) -> List[Order]:
        """
        Retrieve orders within a specific total amount range.
        
        Args:
            min_total: Minimum total amount
            max_total: Maximum total amount
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of orders within the total range
        """
        if session:
            return session.query(Order).filter(
                and_(
                    Order.total_amount >= min_total,
                    Order.total_amount <= max_total
                )
            ).all()
        
        with session_scope() as session:
            return session.query(Order).filter(
                and_(
                    Order.total_amount >= min_total,
                    Order.total_amount <= max_total
                )
            ).all()
    
    @handle_errors("OrderRepository")
    def get_recent_orders(self, limit: int = 10, session: Optional[Session] = None) -> List[Order]:
        """
        Retrieve the most recent orders.
        
        Args:
            limit: Maximum number of orders to return
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of recent orders
        """
        if session:
            return session.query(Order).order_by(desc(Order.order_date)).limit(limit).all()
        
        with session_scope() as session:
            return session.query(Order).order_by(desc(Order.order_date)).limit(limit).all()
    
    @handle_errors("OrderRepository")
    def get_orders_requiring_attention(self, session: Optional[Session] = None) -> List[Order]:
        """
        Retrieve orders that require attention (high priority, overdue, etc.).
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of orders requiring attention
        """
        if session:
            return session.query(Order).filter(
                or_(
                    Order.priority.in_(['high', 'urgent']),
                    and_(
                        Order.expected_delivery < datetime.now(timezone.utc),
                        Order.status != OrderStatusEnum.COMPLETED
                    )
                )
            ).all()
        
        with session_scope() as session:
            return session.query(Order).filter(
                or_(
                    Order.priority.in_(['high', 'urgent']),
                    and_(
                        Order.expected_delivery < datetime.now(timezone.utc),
                        Order.status != OrderStatusEnum.COMPLETED
                    )
                )
            ).all()
    
    @handle_errors("OrderRepository")
    def update_order_status(self, order_id: str, new_status: OrderStatusEnum, session: Optional[Session] = None) -> bool:
        """
        Update the status of an order.
        
        Args:
            order_id: The unique identifier of the order
            new_status: The new status to set
            session: Optional database session (if None, creates a new one)
            
        Returns:
            True if updated successfully
        """
        if session:
            order = session.query(Order).filter_by(id=order_id).first()
            if order:
                order.status = new_status
                session.flush()
                return True
            return False
        
        with session_scope() as session:
            return self.update_order_status(order_id, new_status, session)
    
    @handle_errors("OrderRepository")
    def get_order_statistics(self, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Get order statistics for dashboard/reporting.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing order statistics
        """
        if session:
            total_orders = session.query(Order).count()
            pending_orders = session.query(Order).filter_by(status=OrderStatusEnum.PENDING).count()
            completed_orders = session.query(Order).filter_by(status=OrderStatusEnum.COMPLETED).count()
            
            # Calculate total revenue
            total_revenue = session.query(Order).filter_by(payment_status='paid').with_entities(
                session.query(Order.total_amount).label('total')
            ).all()
            revenue = sum([float(order.total) for order in total_revenue if order.total])
            
            return {
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'completed_orders': completed_orders,
                'total_revenue': revenue
            }
        
        with session_scope() as session:
            return self.get_order_statistics(session)
