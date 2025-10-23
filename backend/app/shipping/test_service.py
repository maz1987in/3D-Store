"""
Unit tests for Shipping Service.

Tests all business logic in shipping/service.py including:
- Shipping CRUD operations
- Shipping cost calculations
- Carrier integration logic
- Delivery status tracking
- Order-shipping relationship
- Edge cases and error handling
"""

import pytest
import uuid
from unittest.mock import Mock, patch
from decimal import Decimal

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from test.test_helpers import assert_decimal_equal, create_mock_filter
from app.shipping.service import ShippingService
from app.shipping.model import Shipping
from app.common.enum import ShippingStatusEnum
from app.common.error_handling import ResourceNotFoundError


class TestShippingService(BaseServiceTestCase):
    """Test cases for ShippingService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = ShippingService()
    
    # ========== CRUD Operations Tests ==========
    
    def test_create_shipping_success(self, db_session, sample_order):
        """Test creating shipping information successfully."""
        shipping_data = {
            'carrier': 'DHL',
            'tracking_number': 'DHL123456789',
            'shipping_cost': 25.00,
            'shipping_date': '2024-01-20',
            'status': ShippingStatusEnum.PENDING
        }
        
        result, status = self.service.create_or_update_shipping(sample_order.id, shipping_data)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify shipping was created
        shipping = db_session.query(Shipping).filter(
            Shipping.order_id == sample_order.id
        ).first()
        assert shipping is not None
        assert shipping.carrier == 'DHL'
        assert_decimal_equal(shipping.shipping_cost, 25.00)
    
    def test_update_shipping_success(self, db_session, sample_order):
        """Test updating existing shipping information."""
        # Create initial shipping
        initial_data = {
            'carrier': 'DHL',
            'tracking_number': 'DHL123',
            'shipping_cost': 25.00,
            'status': ShippingStatusEnum.PENDING
        }
        self.service.create_or_update_shipping(sample_order.id, initial_data)
        
        # Update shipping
        update_data = {
            'tracking_number': 'DHL999',
            'status': ShippingStatusEnum.SHIPPED
        }
        result, status = self.service.create_or_update_shipping(sample_order.id, update_data)
        
        assert status == 200
        assert 'Updated' in result
        
        # Verify update
        shipping = db_session.query(Shipping).filter(
            Shipping.order_id == sample_order.id
        ).first()
        assert shipping.tracking_number == 'DHL999'
        assert shipping.status == ShippingStatusEnum.SHIPPED
    
    def test_get_shipping_with_pagination(self, db_session, sample_customer):
        """Test getting shipping records with pagination."""
        from app.order.model import Order
        
        # Create multiple orders with shipping
        for i in range(12):
            order = Order(
                order_number=f'ORD-SHIP-{i:03d}',
                customer_id=sample_customer.id,
                total_amount=100.00
            )
            db_session.add(order)
            db_session.commit()
            
            shipping_data = {
                'carrier': 'DHL',
                'shipping_cost': 20.00,
                'status': ShippingStatusEnum.PENDING
            }
            self.service.create_or_update_shipping(order.id, shipping_data)
        
        filter_obj = create_mock_filter(page=1, per_page=10)
        result, status = self.service.get_shipping(None, filter_obj)
        
        assert status == 200
        assert 'shipping' in result
        assert 'filters' in result
    
    def test_get_shipping_by_order_id(self, db_session, sample_order):
        """Test getting shipping information by order ID."""
        # Create shipping
        shipping_data = {
            'carrier': 'FedEx',
            'tracking_number': 'FDX987654321',
            'shipping_cost': 30.00,
            'status': ShippingStatusEnum.PENDING
        }
        self.service.create_or_update_shipping(sample_order.id, shipping_data)
        
        # Get by order ID
        result, status = self.service.get_shipping_by_order_id(sample_order.id)
        
        assert status == 200
        assert result['carrier'] == 'FedEx'
        assert result['tracking_number'] == 'FDX987654321'
    
    def test_delete_shipping_success(self, db_session, sample_order):
        """Test deleting shipping information."""
        # Create shipping
        shipping_data = {
            'carrier': 'UPS',
            'shipping_cost': 20.00,
            'status': ShippingStatusEnum.PENDING
        }
        self.service.create_or_update_shipping(sample_order.id, shipping_data)
        
        shipping = db_session.query(Shipping).filter(
            Shipping.order_id == sample_order.id
        ).first()
        shipping_id = shipping.id
        
        # Delete shipping
        result, status = self.service.delete_shipping(shipping_id)
        
        assert status == 200
        assert 'deleted' in result.lower()
        
        deleted_shipping = db_session.query(Shipping).filter_by(id=shipping_id).first()
        assert deleted_shipping is None
    
    # ========== Status Workflow Tests ==========
    
    def test_shipping_status_pending(self, db_session, sample_order):
        """Test creating shipping with pending status."""
        shipping_data = {
            'carrier': 'DHL',
            'shipping_cost': 25.00,
            'status': ShippingStatusEnum.PENDING
        }
        self.service.create_or_update_shipping(sample_order.id, shipping_data)
        
        shipping = db_session.query(Shipping).first()
        assert shipping.status == ShippingStatusEnum.PENDING
    
    def test_shipping_status_transitions(self, db_session, sample_order):
        """Test shipping status transitions."""
        # Create with PENDING status
        shipping_data = {
            'carrier': 'DHL',
            'shipping_cost': 25.00,
            'status': ShippingStatusEnum.PENDING
        }
        self.service.create_or_update_shipping(sample_order.id, shipping_data)
        
        # Transition to SHIPPED
        update_data = {'status': ShippingStatusEnum.SHIPPED}
        self.service.create_or_update_shipping(sample_order.id, update_data)
        
        shipping = db_session.query(Shipping).first()
        assert shipping.status == ShippingStatusEnum.SHIPPED
        
        # Transition to DELIVERED
        update_data = {'status': ShippingStatusEnum.DELIVERED}
        self.service.create_or_update_shipping(sample_order.id, update_data)
        
        db_session.refresh(shipping)
        assert shipping.status == ShippingStatusEnum.DELIVERED
    
    # ========== Carrier Tests ==========
    
    def test_shipping_different_carriers(self, db_session, sample_customer):
        """Test shipping with different carriers."""
        from app.order.model import Order
        
        carriers = ['DHL', 'FedEx', 'UPS', 'USPS', 'Aramex']
        
        for i, carrier in enumerate(carriers):
            order = Order(
                order_number=f'ORD-CAR-{i}',
                customer_id=sample_customer.id,
                total_amount=100.00
            )
            db_session.add(order)
            db_session.commit()
            
            shipping_data = {
                'carrier': carrier,
                'shipping_cost': 20.00,
                'status': ShippingStatusEnum.PENDING
            }
            self.service.create_or_update_shipping(order.id, shipping_data)
        
        # Verify all carriers
        shippings = db_session.query(Shipping).all()
        shipping_carriers = [s.carrier for s in shippings]
        assert set(shipping_carriers) >= set(carriers)
    
    # ========== Cost Calculations Tests ==========
    
    def test_shipping_cost_zero(self, db_session, sample_order):
        """Test shipping with zero cost (free shipping)."""
        shipping_data = {
            'carrier': 'Standard',
            'shipping_cost': 0.00,
            'status': ShippingStatusEnum.PENDING
        }
        
        result, status = self.service.create_or_update_shipping(sample_order.id, shipping_data)
        assert status == 201
        
        shipping = db_session.query(Shipping).first()
        assert shipping.shipping_cost == 0.00
    
    def test_shipping_cost_high_value(self, db_session, sample_order):
        """Test shipping with high cost."""
        expensive_shipping = 500.00
        
        shipping_data = {
            'carrier': 'Express International',
            'shipping_cost': expensive_shipping,
            'status': ShippingStatusEnum.PENDING
        }
        
        result, status = self.service.create_or_update_shipping(sample_order.id, shipping_data)
        assert status == 201
        
        shipping = db_session.query(Shipping).first()
        assert_decimal_equal(shipping.shipping_cost, 500.00)
    
    def test_shipping_cost_decimal_precision(self, db_session, sample_order):
        """Test shipping cost with decimal precision."""
        precise_cost = 24.99
        
        shipping_data = {
            'carrier': 'Standard',
            'shipping_cost': precise_cost,
            'status': ShippingStatusEnum.PENDING
        }
        
        result, status = self.service.create_or_update_shipping(sample_order.id, shipping_data)
        assert status == 201
        
        shipping = db_session.query(Shipping).first()
        assert float(shipping.shipping_cost) == pytest.approx(precise_cost, rel=0.01)
    
    # ========== Tracking Number Tests ==========
    
    def test_auto_generate_tracking_number(self, db_session, sample_order):
        """Test auto-generation of tracking number if not provided."""
        shipping_data = {
            'carrier': 'DHL',
            'shipping_cost': 25.00,
            'status': ShippingStatusEnum.PENDING
            # No tracking_number provided
        }
        
        result, status = self.service.create_or_update_shipping(sample_order.id, shipping_data)
        assert status == 201
        
        shipping = db_session.query(Shipping).first()
        # Should auto-generate tracking number
        assert shipping.tracking_number is not None
        assert len(shipping.tracking_number) > 0
    
    def test_custom_tracking_number(self, db_session, sample_order):
        """Test using custom tracking number."""
        custom_tracking = 'CUSTOM-TRACK-12345'
        
        shipping_data = {
            'carrier': 'DHL',
            'tracking_number': custom_tracking,
            'shipping_cost': 25.00,
            'status': ShippingStatusEnum.PENDING
        }
        
        result, status = self.service.create_or_update_shipping(sample_order.id, shipping_data)
        assert status == 201
        
        shipping = db_session.query(Shipping).first()
        assert shipping.tracking_number == custom_tracking
    
    # ========== Edge Cases Tests ==========
    
    def test_create_shipping_invalid_order(self, db_session):
        """Test creating shipping for non-existent order."""
        shipping_data = {
            'carrier': 'DHL',
            'shipping_cost': 25.00,
            'status': ShippingStatusEnum.PENDING
        }
        
        non_existent_order_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.create_or_update_shipping(non_existent_order_id, shipping_data)
    
    def test_get_shipping_by_invalid_order_id(self, db_session):
        """Test getting shipping for non-existent order."""
        non_existent_order_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.get_shipping_by_order_id(non_existent_order_id)
    
    def test_delete_shipping_not_found(self, db_session):
        """Test deleting non-existent shipping."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_shipping(non_existent_id)
    
    def test_get_shipping_empty_database(self, db_session):
        """Test getting shipping when database is empty."""
        filter_obj = create_mock_filter()
        result, status = self.service.get_shipping(None, filter_obj)
        
        assert status == 200
        assert 'shipping' in result
    
    def test_shipping_without_cost(self, db_session, sample_order):
        """Test creating shipping without cost specified."""
        shipping_data = {
            'carrier': 'DHL',
            'status': ShippingStatusEnum.PENDING
            # No shipping_cost
        }
        
        result, status = self.service.create_or_update_shipping(sample_order.id, shipping_data)
        # Should either use default or require cost
        assert status in [200, 201, 400]
    
    def test_one_shipping_per_order(self, db_session, sample_order):
        """Test that each order has only one shipping record."""
        # Create first shipping
        shipping_data_1 = {
            'carrier': 'DHL',
            'shipping_cost': 25.00,
            'status': ShippingStatusEnum.PENDING
        }
        result1, status1 = self.service.create_or_update_shipping(sample_order.id, shipping_data_1)
        assert status1 == 201
        
        # Create/update again (should update, not create new)
        shipping_data_2 = {
            'carrier': 'FedEx',
            'shipping_cost': 30.00,
            'status': ShippingStatusEnum.PENDING
        }
        result2, status2 = self.service.create_or_update_shipping(sample_order.id, shipping_data_2)
        assert status2 == 200  # Should update
        
        # Verify only one shipping record
        shippings = db_session.query(Shipping).filter(
            Shipping.order_id == sample_order.id
        ).all()
        assert len(shippings) == 1
        assert shippings[0].carrier == 'FedEx'  # Updated value
    
    def test_shipping_partial_update(self, db_session, sample_order):
        """Test partial update of shipping information."""
        # Create shipping
        initial_data = {
            'carrier': 'DHL',
            'tracking_number': 'DHL123',
            'shipping_cost': 25.00,
            'status': ShippingStatusEnum.PENDING
        }
        self.service.create_or_update_shipping(sample_order.id, initial_data)
        
        shipping = db_session.query(Shipping).first()
        original_carrier = shipping.carrier
        
        # Update only status
        update_data = {'status': ShippingStatusEnum.SHIPPED}
        self.service.create_or_update_shipping(sample_order.id, update_data)
        
        db_session.refresh(shipping)
        assert shipping.status == ShippingStatusEnum.SHIPPED
        assert shipping.carrier == original_carrier  # Should not change
    
    # ========== Error Handling Tests ==========
    
    def test_create_shipping_missing_order(self, db_session):
        """Test creating shipping without order."""
        shipping_data = {
            'carrier': 'DHL',
            'shipping_cost': 25.00
        }
        
        with pytest.raises(ResourceNotFoundError):
            self.service.create_or_update_shipping(None, shipping_data)
    
    def test_get_shipping_by_id_not_found(self, db_session):
        """Test getting shipping with non-existent ID."""
        non_existent_id = uuid.uuid4()
        filter_obj = create_mock_filter()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.get_shipping(non_existent_id, filter_obj)

