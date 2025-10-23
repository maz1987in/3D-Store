"""
Integration tests for Inventory Workflows.

Tests complete inventory management workflows:
1. Material purchase order and stock-in transaction
2. Stock tracking across multiple locations
3. Low stock alerts trigger and notifications
4. Stock adjustments and corrections
5. Multi-branch inventory transfers
6. Inventory reconciliation and auditing
"""

import pytest
import uuid
from datetime import datetime, date, timezone
from decimal import Decimal

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseIntegrationTestCase
from app.inventory.service import InventoryService
from app.transaction.service import TransactionService
from app.product.service import ProductService


class TestInventoryWorkflows(BaseIntegrationTestCase):
    """Test complete inventory management workflows."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.inventory_service = InventoryService()
        self.transaction_service = TransactionService()
        self.product_service = ProductService()
    
    # ========== Stock Management Workflows ==========
    
    def test_purchase_and_stock_in_workflow(self, db_session, sample_product, sample_store):
        """Test complete purchase order to stock-in workflow."""
        
        # Step 1: Create inventory record
        inventory_data = {
            'product_id': sample_product.id,
            'store_id': sample_store.id,
            'quantity': 0,
            'quantity_alert': 10
        }
        
        inv_result, inv_status = self.inventory_service.create_inventory(inventory_data)
        assert inv_status == 201
        
        # Step 2: Create stock-in transaction
        transaction_data = {
            'product_id': sample_product.id,
            'from_location_id': sample_store.id,
            'quantity': 100,
            'unit_price': 15.00,
            'type': 'purchase',
            'notes': 'Initial stock purchase'
        }
        
        trans_result, trans_status = self.transaction_service.create_transaction(transaction_data)
        assert trans_status == 201
        
        # Step 3: Update inventory quantity
        from app.inventory.model import Inventory
        inventory = db_session.query(Inventory).filter(
            Inventory.product_id == sample_product.id,
            Inventory.store_id == sample_store.id
        ).first()
        
        update_data = {'quantity': 100}
        update_result, update_status = self.inventory_service.update_inventory(
            inventory.id, update_data
        )
        assert update_status == 200
        
        # Verify final state
        db_session.refresh(inventory)
        assert inventory.quantity == 100
    
    def test_low_stock_alert_workflow(self, db_session, sample_product, sample_store):
        """Test low stock alert triggering."""
        
        # Create inventory with low stock
        inventory_data = {
            'product_id': sample_product.id,
            'store_id': sample_store.id,
            'quantity': 5,
            'quantity_alert': 10  # Alert threshold
        }
        
        inv_result, inv_status = self.inventory_service.create_inventory(inventory_data)
        assert inv_status == 201
        
        # Verify alert condition
        from app.inventory.model import Inventory
        inventory = db_session.query(Inventory).filter(
            Inventory.product_id == sample_product.id
        ).first()
        
        is_low_stock = inventory.quantity < inventory.quantity_alert
        assert is_low_stock is True
    
    def test_multi_location_transfer_workflow(self, db_session, sample_product):
        """Test inventory transfer between locations."""
        from app.store.model import Store
        
        # Create two stores
        store1 = Store(name='Store 1', code='ST001', active=True)
        store2 = Store(name='Store 2', code='ST002', active=True)
        db_session.add_all([store1, store2])
        db_session.commit()
        
        # Create inventory in store 1
        inv1_data = {
            'product_id': sample_product.id,
            'store_id': store1.id,
            'quantity': 100,
            'quantity_alert': 10
        }
        self.inventory_service.create_inventory(inv1_data)
        
        # Create inventory in store 2
        inv2_data = {
            'product_id': sample_product.id,
            'store_id': store2.id,
            'quantity': 0,
            'quantity_alert': 5
        }
        self.inventory_service.create_inventory(inv2_data)
        
        # Create transfer transaction
        transfer_data = {
            'product_id': sample_product.id,
            'from_location_id': store1.id,
            'to_location_id': store2.id,
            'quantity': 30,
            'unit_price': 15.00,
            'type': 'transfer',
            'notes': 'Transfer from Store 1 to Store 2'
        }
        
        trans_result, trans_status = self.transaction_service.create_transaction(transfer_data)
        assert trans_status == 201
        
        # Update inventories
        from app.inventory.model import Inventory
        inv1 = db_session.query(Inventory).filter(
            Inventory.store_id == store1.id,
            Inventory.product_id == sample_product.id
        ).first()
        inv2 = db_session.query(Inventory).filter(
            Inventory.store_id == store2.id,
            Inventory.product_id == sample_product.id
        ).first()
        
        # Decrease from store 1
        self.inventory_service.update_inventory(inv1.id, {'quantity': 70})
        # Increase in store 2
        self.inventory_service.update_inventory(inv2.id, {'quantity': 30})
        
        # Verify transfer
        db_session.refresh(inv1)
        db_session.refresh(inv2)
        assert inv1.quantity == 70
        assert inv2.quantity == 30
    
    def test_inventory_adjustment_workflow(self, db_session, sample_product, sample_store):
        """Test inventory adjustment for corrections."""
        
        # Create inventory
        inventory_data = {
            'product_id': sample_product.id,
            'store_id': sample_store.id,
            'quantity': 100,
            'quantity_alert': 10
        }
        self.inventory_service.create_inventory(inventory_data)
        
        # Create adjustment transaction (e.g., damage, loss)
        adjustment_data = {
            'product_id': sample_product.id,
            'from_location_id': sample_store.id,
            'quantity': 5,
            'unit_price': 15.00,
            'type': 'adjustment',
            'notes': 'Damaged items removed'
        }
        
        trans_result, trans_status = self.transaction_service.create_transaction(adjustment_data)
        assert trans_status == 201
        
        # Update inventory to reflect adjustment
        from app.inventory.model import Inventory
        inventory = db_session.query(Inventory).first()
        
        update_data = {'quantity': 95}
        self.inventory_service.update_inventory(inventory.id, update_data)
        
        db_session.refresh(inventory)
        assert inventory.quantity == 95

