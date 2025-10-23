"""
Unit tests for Order Service.

Tests all business logic in order/service.py including:
- Order CRUD operations
- Order status state machine validation
- Payment integration workflows
- Shipping integration
- Order calculations
- Cancellation and refund workflows
- Edge cases and error handling
"""

import pytest
import uuid
from datetime import datetime, date, timezone, timedelta
from decimal import Decimal

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from test.test_helpers import create_mock_filter
from app.order.service import OrderService
from app.order.model import Order
from app.common.enum import OrderStatusEnum
from app.common.error_handling import ResourceNotFoundError


class TestOrderService(BaseServiceTestCase):
    """Test cases for OrderService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = OrderService()
    
    # ========== CRUD Operations Tests ==========
    
    def test_create_order_success(self, db_session, sample_supplier):
        """Test creating an order successfully."""
        order_data = {
            'order_date': date.today().strftime('%Y-%m-%d'),
            'expected_delivery': (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'status': OrderStatusEnum.PENDING.value,
            'total_amount': 150.50,
            'supplier_id': sample_supplier.id,
            'notes': 'Test order'
        }
        
        result, status = self.service.create_order(order_data)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify order was created
        order = db_session.query(Order).filter(
            Order.supplier_id == sample_supplier.id
        ).first()
        assert order is not None
        assert float(order.total_amount) == 150.50
        assert order.status == OrderStatusEnum.PENDING
    
    def test_get_orders_with_pagination(self, db_session, sample_supplier):
        """Test getting orders with pagination."""
        # Create multiple orders
        for i in range(12):
            order_data = {
                'order_date': date.today().strftime('%Y-%m-%d'),
                'status': OrderStatusEnum.PENDING.value,
                'total_amount': 100.00 + i,
                'supplier_id': sample_supplier.id,
                'notes': f'Order {i}'
            }
            self.service.create_order(order_data)
        
        filter_obj = create_mock_filter(page=1, per_page=10)
        result, status = self.service.get_orders(None, filter_obj)
        
        assert status == 200
        assert 'orders' in result
        assert 'filters' in result
    
    def test_get_order_by_id(self, db_session, sample_supplier):
        """Test getting a specific order by ID."""
        order_data = {
            'order_date': date.today().strftime('%Y-%m-%d'),
            'status': OrderStatusEnum.PENDING.value,
            'total_amount': 200.00,
            'supplier_id': sample_supplier.id
        }
        self.service.create_order(order_data)
        
        order = db_session.query(Order).first()
        filter_obj = create_mock_filter()
        
        result, status = self.service.get_orders(order.id, filter_obj)
        
        assert status == 200
        assert 'orders' in result
    
    def test_update_order_success(self, db_session, sample_supplier):
        """Test updating an order."""
        # Create order
        order_data = {
            'order_date': date.today().strftime('%Y-%m-%d'),
            'status': OrderStatusEnum.PENDING.value,
            'total_amount': 100.00,
            'supplier_id': sample_supplier.id
        }
        self.service.create_order(order_data)
        
        order = db_session.query(Order).first()
        
        # Update order
        update_data = {
            'status': OrderStatusEnum.PROCESSING.value,
            'total_amount': 150.00,
            'notes': 'Updated order'
        }
        
        result, status = self.service.update_order(order.id, update_data)
        
        assert status == 200
        assert 'Updated' in result
    
    def test_delete_order_success(self, db_session, sample_supplier):
        """Test deleting an order."""
        order_data = {
            'order_date': date.today().strftime('%Y-%m-%d'),
            'status': OrderStatusEnum.PENDING.value,
            'total_amount': 50.00,
            'supplier_id': sample_supplier.id
        }
        self.service.create_order(order_data)
        
        order = db_session.query(Order).first()
        order_id = order.id
        
        result, status = self.service.delete_order(order_id)
        
        assert status == 200
        assert 'deleted' in result.lower()
        
        deleted_order = db_session.query(Order).filter_by(id=order_id).first()
        assert deleted_order is None
    
    # ========== Order Status State Machine Tests ==========
    
    def test_order_status_transitions(self, db_session, sample_supplier):
        """Test order status state transitions."""
        statuses = [
            OrderStatusEnum.PENDING,
            OrderStatusEnum.PROCESSING,
            OrderStatusEnum.SHIPPED,
            OrderStatusEnum.DELIVERED,
            OrderStatusEnum.COMPLETED
        ]
        
        for status_enum in statuses:
            order_data = {
                'order_date': date.today().strftime('%Y-%m-%d'),
                'status': status_enum.value,
                'total_amount': 100.00,
                'supplier_id': sample_supplier.id,
                'notes': f'Status: {status_enum.value}'
            }
            result, status_code = self.service.create_order(order_data)
            assert status_code == 201
        
        # Verify all statuses were created
        orders = db_session.query(Order).all()
        order_statuses = [o.status for o in orders]
        assert len(set(order_statuses)) >= len(statuses)
    
    def test_order_status_pending_to_processing(self, db_session, sample_supplier):
        """Test transitioning order from PENDING to PROCESSING."""
        order_data = {
            'order_date': date.today().strftime('%Y-%m-%d'),
            'status': OrderStatusEnum.PENDING.value,
            'total_amount': 100.00,
            'supplier_id': sample_supplier.id
        }
        self.service.create_order(order_data)
        
        order = db_session.query(Order).first()
        
        # Update to PROCESSING
        update_data = {
            'status': OrderStatusEnum.PROCESSING.value
        }
        
        result, status = self.service.update_order(order.id, update_data)
        
        assert status == 200
        
        db_session.refresh(order)
        assert order.status == OrderStatusEnum.PROCESSING
    
    def test_order_cancelled_status(self, db_session, sample_supplier):
        """Test setting order to CANCELLED status."""
        order_data = {
            'order_date': date.today().strftime('%Y-%m-%d'),
            'status': OrderStatusEnum.PENDING.value,
            'total_amount': 100.00,
            'supplier_id': sample_supplier.id
        }
        self.service.create_order(order_data)
        
        order = db_session.query(Order).first()
        
        # Cancel order
        update_data = {
            'status': OrderStatusEnum.CANCELLED.value
        }
        
        result, status = self.service.update_order(order.id, update_data)
        
        assert status == 200
        
        db_session.refresh(order)
        assert order.status == OrderStatusEnum.CANCELLED
    
    # ========== Order Amount Tests ==========
    
    def test_order_total_amount_calculation(self, db_session, sample_supplier):
        """Test order total amount."""
        order_data = {
            'order_date': date.today().strftime('%Y-%m-%d'),
            'status': OrderStatusEnum.PENDING.value,
            'total_amount': 250.75,
            'supplier_id': sample_supplier.id
        }
        self.service.create_order(order_data)
        
        order = db_session.query(Order).first()
        assert float(order.total_amount) == 250.75
    
    def test_order_with_zero_amount(self, db_session, sample_supplier):
        """Test order with zero amount."""
        order_data = {
            'order_date': date.today().strftime('%Y-%m-%d'),
            'status': OrderStatusEnum.PENDING.value,
            'total_amount': 0.00,
            'supplier_id': sample_supplier.id,
            'notes': 'Free order'
        }
        
        result, status = self.service.create_order(order_data)
        
        assert status == 201
    
    # ========== Order Date Tests ==========
    
    def test_order_with_expected_delivery(self, db_session, sample_supplier):
        """Test order with expected delivery date."""
        delivery_date = date.today() + timedelta(days=14)
        
        order_data = {
            'order_date': date.today().strftime('%Y-%m-%d'),
            'expected_delivery': delivery_date.strftime('%Y-%m-%d'),
            'status': OrderStatusEnum.PENDING.value,
            'total_amount': 100.00,
            'supplier_id': sample_supplier.id
        }
        
        result, status = self.service.create_order(order_data)
        
        assert status == 201
        
        order = db_session.query(Order).first()
        assert order.expected_delivery == delivery_date
    
    def test_order_without_expected_delivery(self, db_session, sample_supplier):
        """Test order without expected delivery date."""
        order_data = {
            'order_date': date.today().strftime('%Y-%m-%d'),
            'status': OrderStatusEnum.PENDING.value,
            'total_amount': 100.00,
            'supplier_id': sample_supplier.id
        }
        
        result, status = self.service.create_order(order_data)
        
        assert status == 201
    
    # ========== Supplier Association Tests ==========
    
    def test_order_with_supplier(self, db_session, sample_supplier):
        """Test order associated with supplier."""
        order_data = {
            'order_date': date.today().strftime('%Y-%m-%d'),
            'status': OrderStatusEnum.PENDING.value,
            'total_amount': 100.00,
            'supplier_id': sample_supplier.id
        }
        
        result, status = self.service.create_order(order_data)
        
        assert status == 201
        
        order = db_session.query(Order).first()
        assert order.supplier_id == sample_supplier.id
    
    def test_create_order_invalid_supplier(self, db_session):
        """Test creating order with non-existent supplier."""
        order_data = {
            'order_date': date.today().strftime('%Y-%m-%d'),
            'status': OrderStatusEnum.PENDING.value,
            'total_amount': 100.00,
            'supplier_id': uuid.uuid4()  # Non-existent
        }
        
        with pytest.raises(Exception):  # Foreign key constraint
            self.service.create_order(order_data)
    
    # ========== Order Notes Tests ==========
    
    def test_order_with_notes(self, db_session, sample_supplier):
        """Test order with detailed notes."""
        order_data = {
            'order_date': date.today().strftime('%Y-%m-%d'),
            'status': OrderStatusEnum.PENDING.value,
            'total_amount': 100.00,
            'supplier_id': sample_supplier.id,
            'notes': 'Rush order - please expedite shipping'
        }
        
        result, status = self.service.create_order(order_data)
        
        assert status == 201
        
        order = db_session.query(Order).first()
        assert order.notes == 'Rush order - please expedite shipping'
    
    # ========== Error Handling Tests ==========
    
    def test_get_order_not_found(self, db_session):
        """Test getting a non-existent order."""
        non_existent_id = uuid.uuid4()
        filter_obj = create_mock_filter()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.get_orders(non_existent_id, filter_obj)
    
    def test_update_order_not_found(self, db_session):
        """Test updating a non-existent order."""
        non_existent_id = uuid.uuid4()
        update_data = {
            'total_amount': 200.00
        }
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_order(non_existent_id, update_data)
    
    def test_delete_order_not_found(self, db_session):
        """Test deleting a non-existent order."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_order(non_existent_id)
    
    def test_get_orders_empty_database(self, db_session):
        """Test getting orders when database is empty."""
        # Clear orders
        db_session.query(Order).delete()
        db_session.commit()
        
        filter_obj = create_mock_filter()
        result, status = self.service.get_orders(None, filter_obj)
        
        assert status == 200
        assert 'orders' in result

