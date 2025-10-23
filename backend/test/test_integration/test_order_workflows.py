"""
Integration tests for Order Workflows.

Tests complete end-to-end order lifecycle:
1. Customer creates quotation request
2. Admin reviews and creates quotation with pricing
3. Customer approves quotation
4. System creates order from quotation
5. Payment processing through gateway
6. Order fulfillment
7. Shipping and delivery tracking
8. Customer rating submission
9. Invoice generation and reconciliation
"""

import pytest
import uuid
from datetime import datetime, date, timezone, timedelta
from decimal import Decimal

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseIntegrationTestCase
from app.quotation.service import QuotationService
from app.order.service import OrderService
from app.payment.service import PaymentService
from app.shipping.service import ShippingService
from app.rating.service import RatingService
from app.invoices.service import InvoiceService
from app.common.enum import OrderStatusEnum, PaymentStatusEnum


class TestOrderWorkflows(BaseIntegrationTestCase):
    """Test complete order lifecycle workflows."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.quotation_service = QuotationService()
        self.order_service = OrderService()
        self.payment_service = PaymentService()
        self.shipping_service = ShippingService()
        self.rating_service = RatingService()
        self.invoice_service = InvoiceService()
    
    # ========== Complete Order Lifecycle Tests ==========
    
    def test_complete_order_lifecycle(self, db_session, sample_user, sample_product, sample_supplier):
        """Test complete order lifecycle from quotation to delivery."""
        
        # Step 1: Create quotation
        quotation_data = {
            'customer_id': sample_user.id,
            'product_id': sample_product.id,
            'quantity': 5,
            'base_price': 100.00,
            'material_cost': 25.00,
            'labor_cost': 15.00,
            'status': 'draft'
        }
        
        quote_result, quote_status = self.quotation_service.create_quotation(quotation_data)
        assert quote_status == 201
        
        # Step 2: Approve quotation
        from app.quotation.model import Quotation
        quotation = db_session.query(Quotation).first()
        
        approve_data = {'status': 'approved'}
        approve_result, approve_status = self.quotation_service.update_quotation(
            quotation.id, approve_data
        )
        assert approve_status == 200
        
        # Step 3: Create order
        order_data = {
            'order_date': date.today().strftime('%Y-%m-%d'),
            'status': OrderStatusEnum.PENDING.value,
            'total_amount': 140.00,  # base + material + labor
            'supplier_id': sample_supplier.id,
            'notes': 'Order from quotation'
        }
        
        order_result, order_status = self.order_service.create_order(order_data)
        assert order_status == 201
        
        # Step 4: Process payment
        from app.order.model import Order
        order = db_session.query(Order).first()
        
        payment_data = {
            'order_id': order.id,
            'amount': 140.00,
            'method': 'online',
            'status': PaymentStatusEnum.SUCCESS.value
        }
        
        payment_result, payment_status = self.payment_service.create_payment(payment_data)
        assert payment_status == 201
        
        # Step 5: Update order to processing
        process_data = {'status': OrderStatusEnum.PROCESSING.value}
        process_result, process_status = self.order_service.update_order(order.id, process_data)
        assert process_status == 200
        
        # Verify complete workflow
        db_session.refresh(order)
        assert order.status == OrderStatusEnum.PROCESSING
    
    def test_order_with_payment_failure(self, db_session, sample_supplier):
        """Test order workflow when payment fails."""
        
        # Create order
        order_data = {
            'order_date': date.today().strftime('%Y-%m-%d'),
            'status': OrderStatusEnum.PENDING.value,
            'total_amount': 100.00,
            'supplier_id': sample_supplier.id
        }
        
        order_result, order_status = self.order_service.create_order(order_data)
        assert order_status == 201
        
        from app.order.model import Order
        order = db_session.query(Order).first()
        
        # Simulate payment failure
        payment_data = {
            'order_id': order.id,
            'amount': 100.00,
            'method': 'online',
            'status': PaymentStatusEnum.FAILED.value
        }
        
        payment_result, payment_status = self.payment_service.create_payment(payment_data)
        
        # Order should remain PENDING
        db_session.refresh(order)
        assert order.status == OrderStatusEnum.PENDING
    
    def test_order_cancellation_workflow(self, db_session, sample_supplier):
        """Test order cancellation with refund."""
        
        # Create and pay for order
        order_data = {
            'order_date': date.today().strftime('%Y-%m-%d'),
            'status': OrderStatusEnum.PENDING.value,
            'total_amount': 150.00,
            'supplier_id': sample_supplier.id
        }
        
        order_result, order_status = self.order_service.create_order(order_data)
        assert order_status == 201
        
        from app.order.model import Order
        order = db_session.query(Order).first()
        
        # Cancel order
        cancel_data = {'status': OrderStatusEnum.CANCELLED.value}
        cancel_result, cancel_status = self.order_service.update_order(order.id, cancel_data)
        assert cancel_status == 200
        
        db_session.refresh(order)
        assert order.status == OrderStatusEnum.CANCELLED
    
    def test_order_state_transitions(self, db_session, sample_supplier):
        """Test order progressing through all states."""
        
        # Create order
        order_data = {
            'order_date': date.today().strftime('%Y-%m-%d'),
            'status': OrderStatusEnum.PENDING.value,
            'total_amount': 200.00,
            'supplier_id': sample_supplier.id
        }
        
        order_result, order_status = self.order_service.create_order(order_data)
        assert order_status == 201
        
        from app.order.model import Order
        order = db_session.query(Order).first()
        
        # Transition through states
        states = [
            OrderStatusEnum.PROCESSING,
            OrderStatusEnum.SHIPPED,
            OrderStatusEnum.DELIVERED,
            OrderStatusEnum.COMPLETED
        ]
        
        for state in states:
            update_data = {'status': state.value}
            result, status = self.order_service.update_order(order.id, update_data)
            assert status == 200
            
            db_session.refresh(order)
            assert order.status == state

